"""Checkpoint system — run pipeline to a named stage and verify state.

Each checkpoint corresponds to a completed workflow. Verifying a checkpoint
checks that all expected contracts exist and have the right structure.

The revision loop runs after the critique workflow: if the hard gate fails,
the pipeline re-enters at the scene level and iterates up to MAX_RETRIES times
until all structural checks pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.agents.director import Director
from src.agents.store import ContractStore

REVISION_MAX_ATTEMPTS = 3

CHECKPOINT_WORKFLOW_MAP: list[tuple[str, str, str]] = [
    ("brief", "00-brief-and-taxonomy", "Brief and taxonomy complete"),
    ("premise", "01-seed-to-premise", "Seed transformed to premise with actants"),
    ("structure", "02-premise-to-structure", "Fabula structure and constraints"),
    ("episodes", "03-structure-to-episodes", "Episodes, chapters, arcs segmented"),
    ("scenes", "04-episodes-to-scenes", "Scenes written with Greimas diagnostics"),
    ("draft", "05-scenes-to-draft", "Draft assembled"),
    ("editorial", "06-editorial-passes", "Editorial passes complete"),
    ("final", "07-critique-and-revision", "Gates passed, final approval"),
]

CHECKPOINT_ORDER = [name for name, wid, desc in CHECKPOINT_WORKFLOW_MAP]
WORKFLOW_FOR_CHECKPOINT = {name: wid for name, wid, desc in CHECKPOINT_WORKFLOW_MAP}


@dataclass
class CheckpointReport:
    stage: str
    passed: bool
    contracts_found: dict[str, int]
    contracts_expected: dict[str, int]
    messages: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def expected_contracts_at_checkpoint(checkpoint: str) -> dict[str, int]:
    """Return the minimum number of each contract type expected at a checkpoint."""
    expectations: dict[str, dict[str, int]] = {
        "brief": {"story": 1, "theme": 1},
        "premise": {"story": 1, "theme": 1, "character": 1},
        "structure": {"story": 1, "theme": 1, "character": 1},
        "episodes": {"story": 1, "theme": 1, "character": 1, "episode": 1, "chapter": 1},
        "scenes": {"story": 1, "theme": 1, "character": 1, "episode": 1, "chapter": 1, "scene": 1},
        "draft": {"story": 1, "theme": 1, "character": 1, "episode": 1, "chapter": 1, "scene": 1},
        "editorial": {"story": 1, "theme": 1, "character": 1, "episode": 1, "chapter": 1, "scene": 1},
        "final": {"story": 1, "theme": 1, "character": 1, "episode": 1, "chapter": 1, "scene": 1, "critique": 1},
    }
    return expectations.get(checkpoint, {})


def verify_checkpoint(
    store: ContractStore,
    checkpoint: str,
) -> CheckpointReport:
    """Check that the store has all expected contracts for this checkpoint."""
    expected = expected_contracts_at_checkpoint(checkpoint)
    found: dict[str, int] = {}
    messages: list[str] = []
    errors: list[str] = []

    for type_key, min_count in expected.items():
        contracts = store.list_by_type(type_key)
        count = len(contracts)
        found[type_key] = count
        if count >= min_count:
            messages.append(f"  {type_key}: {count} contract(s) OK")
        else:
            errors.append(f"  {type_key}: expected >={min_count}, found {count} MISSING")

    passed = len(errors) == 0

    if passed:
        messages.insert(0, f"Checkpoint '{checkpoint}' PASSED")
    else:
        messages.insert(0, f"Checkpoint '{checkpoint}' FAILED")

    return CheckpointReport(
        stage=checkpoint,
        passed=passed,
        contracts_found=found,
        contracts_expected={k: v for k, v in expected.items()},
        messages=messages,
        errors=errors,
    )


def _hard_gate_failed(director: Director, workflow_id: str) -> bool:
    """Check if the hard gate step failed in the given workflow execution."""
    for entry in reversed(director.execution_log):
        if entry.get("workflow") != workflow_id:
            continue
        if entry.get("step") == "run_hard_gate":
            return not entry.get("success", False)
    return False


def run_to_checkpoint(
    director: Director,
    checkpoint: str,
    verbose: bool = True,
) -> list[CheckpointReport]:
    """Run all workflows up to and including the target checkpoint.

    After the critique workflow, if the hard gate fails, the pipeline loops
    back to regenerate scenes and re-check, up to REVISION_MAX_ATTEMPTS times.
    """
    reports: list[CheckpointReport] = []

    for name, wid, desc in CHECKPOINT_WORKFLOW_MAP:
        if verbose:
            print(f"\n{'='*60}")
            print(f"WORKFLOW: {wid}")
            print(f"{desc}")
            print(f"{'='*60}")

        results = director.run_workflow(wid)
        successes = sum(1 for r in results if r.success)
        total = len(results)
        status = "OK" if successes == total else "FAIL"

        if verbose:
            print(f"  Steps: {successes}/{total} passed {status}")
            for r in results:
                if not r.success:
                    print(f"  FAIL: {r.message}")
                    for e in (r.errors or []):
                        print(f"    - {e}")
                else:
                    artifact_info = f" ({len(r.artifacts)} artifacts)" if r.artifacts else ""
                    print(f"  OK: {r.message}{artifact_info}")

        # Revision loop: if hard gate failed, try targeted revision before regenerating
        if wid == "07-critique-and-revision" and _hard_gate_failed(director, wid):
            for attempt in range(1, REVISION_MAX_ATTEMPTS + 1):
                is_last_attempt = attempt == REVISION_MAX_ATTEMPTS

                if is_last_attempt:
                    # Last resort: full regeneration
                    if verbose:
                        print(f"\n  --- Regeneration attempt {attempt}/{REVISION_MAX_ATTEMPTS} ---")
                    deleted = director.store.delete_by_type("scene")
                    if verbose:
                        print(f"  Removed {deleted} old scene(s)")
                    redo_workflows = [
                        ("04-episodes-to-scenes", "Scenes rewritten"),
                        ("05-scenes-to-draft", "Draft reassembled"),
                        ("07-critique-and-revision", "Gates rechecked"),
                    ]
                else:
                    # Targeted revision: apply editorial changes, then re-check
                    if verbose:
                        print(f"\n  --- Targeted revision attempt {attempt}/{REVISION_MAX_ATTEMPTS} ---")
                    redo_workflows = [
                        ("06-editorial-passes", "Editorial passes reapplied"),
                        ("07-critique-and-revision", "Gates rechecked"),
                    ]

                for redo_wid, redo_desc in redo_workflows:
                    if verbose:
                        print(f"\n  REDO: {redo_wid} ({redo_desc})")
                    redo_results = director.run_workflow(redo_wid)
                    redo_successes = sum(1 for r in redo_results if r.success)
                    redo_total = len(redo_results)
                    redo_status = "OK" if redo_successes == redo_total else "FAIL"
                    if verbose:
                        for r in redo_results:
                            if not r.success:
                                print(f"    FAIL: {r.message}")
                            else:
                                print(f"    OK: {r.message}")

                # Check if hard gate now passes
                if not _hard_gate_failed(director, "07-critique-and-revision"):
                    if verbose:
                        print(f"  Hard gate passed after revision attempt {attempt}")
                    break
            else:
                if verbose:
                    print(f"  Hard gate still failing after {REVISION_MAX_ATTEMPTS} revision attempts")

        report = verify_checkpoint(director.store, name)
        reports.append(report)

        if verbose:
            for m in report.messages:
                print(m)
            if report.errors:
                for e in report.errors:
                    print(e)

        if not report.passed:
            if verbose:
                print(f"\nStopping at checkpoint '{name}' — contract expectations not met.")
            break

        if name == checkpoint:
            if verbose:
                print(f"\nOK Reached target checkpoint '{checkpoint}'")
            break

    return reports
