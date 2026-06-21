"""Tests for checkpoint skip/resume logic."""

import pytest

from src.agents.director import Director
from src.agents.llm import MockLLMProvider, reset_llm, set_llm
from src.agents.store import ContractStore, reset_store
from src.contracts.models import Medium, StoryContract, ThemeContract
from src.pipeline.checkpoints import (
    CHECKPOINT_ORDER,
    find_next_checkpoint,
    run_to_checkpoint,
    verify_checkpoint,
    _verify_skipped_checkpoints,
)
from src.pipeline.orchestrator import default_agent_registry


@pytest.fixture(autouse=True)
def _reset():
    reset_store()
    reset_llm()
    yield


def _setup_mock():
    from scripts.demo import MOCK_RESPONSES
    mock = MockLLMProvider()
    for trigger, response in MOCK_RESPONSES.items():
        mock.add_rule(trigger, response)
    set_llm(mock, provider_type="mock")
    return mock


def _agents_and_director(store=None):
    if store is None:
        store = ContractStore()
    agents = default_agent_registry(store=store)
    director = Director(agents, store=store, medium=Medium.BOOK)
    return agents, director


# ── find_next_checkpoint ─────────────────────────────────────────────


def test_find_next_empty_store():
    store = ContractStore()
    assert find_next_checkpoint(store, "final") == "brief"


def test_find_next_brief_satisfied_stops_at_premise():
    store = ContractStore()
    store.put("story", StoryContract(title="T", premise="P"))
    store.put("theme", ThemeContract())
    assert find_next_checkpoint(store, "final") == "premise"


def test_find_next_target_already_reached():
    store = ContractStore()
    store.put("story", StoryContract(title="T", premise="P"))
    store.put("theme", ThemeContract())
    assert find_next_checkpoint(store, "brief") is None


# ── _verify_skipped_checkpoints ──────────────────────────────────────


def test_verify_skipped_all_pass(capsys):
    store = ContractStore()
    store.put("story", StoryContract(title="T", premise="P"))
    store.put("theme", ThemeContract())
    assert _verify_skipped_checkpoints(store, "premise", verbose=True) is True
    captured = capsys.readouterr()
    assert "brief satisfied" in captured.out


def test_verify_skipped_missing_theme_fails(capsys):
    store = ContractStore()
    store.put("story", StoryContract(title="T", premise="P"))
    assert _verify_skipped_checkpoints(store, "premise", verbose=True) is False
    captured = capsys.readouterr()
    assert "missing" in captured.out.lower()


# ── run_to_checkpoint with start_from ────────────────────────────────


def test_run_to_checkpoint_start_from_skips_earlier_workflows():
    """start_from='premise' should skip brief workflow, run premise + structure."""
    _setup_mock()
    store = ContractStore()
    store.put("story", StoryContract(title="T", premise="P"))
    store.put("theme", ThemeContract())
    _, director = _agents_and_director(store)

    reports = run_to_checkpoint(director, "structure", verbose=False, start_from="premise")

    assert len(reports) >= 1
    # The brief report (from skip phase) should pass
    brief_reports = [r for r in reports if r.stage == "brief"]
    assert len(brief_reports) == 1
    assert brief_reports[0].passed, f"Brief should pass via store: {brief_reports[0].errors}"

    # Execution log should NOT contain brief workflow steps
    wf_ids = {e["workflow"] for e in director.execution_log}
    assert "00-brief-and-taxonomy" not in wf_ids, "Brief workflow should have been skipped"
    assert "01-seed-to-premise" in wf_ids, "Premise workflow should have run"


def test_run_to_checkpoint_start_from_same_as_target_runs_normally():
    """start_from='brief' + checkpoint='brief' — first checkpoint, nothing to skip."""
    _setup_mock()
    store = ContractStore()
    store.put("story", StoryContract(title="T", premise="P"))
    store.put("theme", ThemeContract())
    _, director = _agents_and_director(store)

    reports = run_to_checkpoint(director, "brief", verbose=False, start_from="brief")

    assert len(reports) == 1
    assert reports[0].stage == "brief"
    assert reports[0].passed, f"Brief should pass: {reports[0].errors}"
    # Brief workflow should have run normally
    wf_ids = {e["workflow"] for e in director.execution_log}
    assert "00-brief-and-taxonomy" in wf_ids


def test_run_to_checkpoint_start_from_missing_contracts_fails():
    """If earlier checkpoints aren't satisfied, skip phase reports failure."""
    _setup_mock()
    store = ContractStore()
    # Only story — no theme, so "brief" checkpoint fails
    store.put("story", StoryContract(title="T", premise="P"))
    _, director = _agents_and_director(store)

    reports = run_to_checkpoint(director, "premise", verbose=False, start_from="premise")

    brief_reports = [r for r in reports if r.stage == "brief"]
    assert any(not r.passed for r in brief_reports), "Brief should fail due to missing theme"


def test_run_to_checkpoint_start_from_none_runs_from_beginning():
    """start_from=None (default) should run all workflows from the start."""
    _setup_mock()
    store = ContractStore()
    store.put("story", StoryContract(title="T", premise="P"))
    _, director = _agents_and_director(store)

    reports = run_to_checkpoint(director, "brief", verbose=False, start_from=None)

    assert len(reports) == 1
    assert reports[0].passed
    wf_ids = {e["workflow"] for e in director.execution_log}
    assert "00-brief-and-taxonomy" in wf_ids


# ── Integration: cmd_run style usage ─────────────────────────────────


def test_resume_from_loaded_state():
    """Simulate what cmd_run does with --load and auto-detect."""
    _setup_mock()

    # Create a store with state up to "brief" (story + theme)
    store = ContractStore()
    store.put("story", StoryContract(title="T", premise="P"))
    store.put("theme", ThemeContract())

    # find_next_checkpoint detects "premise" as the next to run
    next_ck = find_next_checkpoint(store, "premise")
    assert next_ck == "premise"

    # Build director from this state, start from detected checkpoint
    _, director = _agents_and_director(store)

    reports = run_to_checkpoint(director, "premise", verbose=False, start_from="premise")

    # Should have: brief(verified from store) + premise(ran)
    assert len(reports) >= 2
    for r in reports:
        assert r.passed, f"Checkpoint {r.stage} failed: {r.errors}"

    # Verify brief was skipped, premise ran
    wf_ids = {e["workflow"] for e in director.execution_log}
    assert "00-brief-and-taxonomy" not in wf_ids, "Brief should be skipped"
    assert "01-seed-to-premise" in wf_ids, "Premise should have run"
