"""Checkpoint system — run pipeline to a named stage and verify state.

Each checkpoint corresponds to a completed workflow. Verifying a checkpoint
checks that all expected contracts exist and have the right structure.

The revision loop runs after the critique workflow: if the hard gate fails,
the pipeline re-enters at the scene level and iterates up to MAX_RETRIES times
until all structural checks pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field

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
    step_failures: int = 0


def expected_contracts_at_checkpoint(checkpoint: str) -> dict[str, int]:
    """Return the minimum number of each contract type expected at a checkpoint."""
    expectations: dict[str, dict[str, int]] = {
        "brief": {"story": 1, "theme": 1, "discourse": 1},
        "premise": {"story": 1, "theme": 1, "character": 1, "discourse": 1},
        "structure": {"story": 1, "theme": 1, "character": 1, "discourse": 1},
        "episodes": {"story": 1, "theme": 1, "character": 1, "episode": 1, "chapter": 1, "discourse": 1},
        "scenes": {"story": 1, "theme": 1, "character": 1, "episode": 1, "chapter": 1, "scene": 1, "discourse": 1},
        "draft": {"story": 1, "theme": 1, "character": 1, "episode": 1, "chapter": 1, "scene": 1, "discourse": 1},
        "editorial": {"story": 1, "theme": 1, "character": 1, "episode": 1, "chapter": 1, "scene": 1, "discourse": 1},
        "final": {"story": 1, "theme": 1, "character": 1, "episode": 1, "chapter": 1, "scene": 1, "critique": 1, "discourse": 1},
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


def _verify_skipped_checkpoints(
    store: ContractStore,
    skip_target: str,
    verbose: bool = True,
) -> bool:
    """Verify that all checkpoints before skip_target are satisfied in the store.

    Returns True if all up to (but not including) skip_target pass.
    Returns False and prints the first failure if any checkpoint is missing contracts.
    """
    for name, wid, desc in CHECKPOINT_WORKFLOW_MAP:
        if name == skip_target:
            break
        report = verify_checkpoint(store, name)
        if not report.passed:
            if verbose:
                print(f"\n  State missing contracts for checkpoint '{name}'")
                for e in report.errors:
                    print(f"    {e}")
                print(f"  Cannot skip — re-run from '{name}' or fix state.")
            return False
        if verbose:
            ctypes = ", ".join(f"{k}={v}" for k, v in report.contracts_found.items())
            print(f"  ✓ {name} satisfied ({ctypes})")
    return True


def run_to_checkpoint(
    director: Director,
    checkpoint: str,
    verbose: bool = True,
    start_from: str | None = None,
) -> list[CheckpointReport]:
    """Run all workflows up to and including the target checkpoint.

    When ``start_from`` is set, workflows whose checkpoints precede it are
    skipped — their contracts are verified from the store instead of re-run.
    This enables iterative stage-by-stage testing with a real LLM.

    After the critique workflow, if the hard gate fails, the pipeline loops
    back to regenerate scenes and re-check, up to REVISION_MAX_ATTEMPTS times.
    """
    reports: list[CheckpointReport] = []

    # Track step failures per workflow (updated by revision loop re-runs)
    workflow_step_failures: dict[str, int] = {}

    # Phase 1: if start_from is set, verify and skip earlier checkpoints
    if start_from is not None:
        for name, wid, desc in CHECKPOINT_WORKFLOW_MAP:
            if name == start_from:
                break
            report = verify_checkpoint(director.store, name)
            report.step_failures = 0
            reports.append(report)
            if verbose:
                ctypes = ", ".join(f"{k}={v}" for k, v in report.contracts_found.items())
                print(f"\n  — Skipping {wid} ({ctypes}) —")

            if not report.passed:
                if verbose:
                    print(f"  State missing contracts for checkpoint '{name}'")
                    for e in report.errors:
                        print(f"    {e}")
                return reports

            director.store.mark_checkpoint(name)

            if name == checkpoint:
                if verbose:
                    print(f"\nOK Target checkpoint '{checkpoint}' already reached.")
                return reports

    # Phase 2: run remaining workflows from start_from (or from beginning)
    started = start_from is None

    for name, wid, desc in CHECKPOINT_WORKFLOW_MAP:
        if not started:
            if name == start_from:
                started = True
            else:
                continue

        if verbose:
            print(f"\n{'='*60}")
            print(f"WORKFLOW: {wid}")
            print(f"{desc}")
            print(f"{'='*60}")

        results = director.run_workflow(wid)
        successes = sum(1 for r in results if r.success)
        total = len(results)
        step_failures = total - successes
        workflow_step_failures[wid] = step_failures

        if verbose:
            status = "OK" if successes == total else "FAIL"
            print(f"  Steps: {successes}/{total} passed {status}")
            for r in results:
                if not r.success:
                    print(f"  FAIL: {r.message}")
                    for e in (r.errors or []):
                        print(f"    - {e}")
                elif r.message and r.message.startswith("Skipped"):
                    print(f"  SKIPPED: {r.message}")
                else:
                    artifact_info = f" ({len(r.artifacts)} artifacts)" if r.artifacts else ""
                    print(f"  OK: {r.message}{artifact_info}")

        # Revision loop: if hard gate failed, try targeted revision before regenerating
        if wid == "07-critique-and-revision" and _hard_gate_failed(director, wid):
            for attempt in range(1, REVISION_MAX_ATTEMPTS + 1):
                is_last_attempt = attempt == REVISION_MAX_ATTEMPTS

                if is_last_attempt:
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
                    workflow_step_failures[redo_wid] = redo_total - redo_successes
                    if verbose:
                        for r in redo_results:
                            if not r.success:
                                print(f"    FAIL: {r.message}")
                            elif r.message and r.message.startswith("Skipped"):
                                print(f"    SKIPPED: {r.message}")
                            else:
                                print(f"    OK: {r.message}")

                if not _hard_gate_failed(director, "07-critique-and-revision"):
                    if verbose:
                        print(f"  Hard gate passed after revision attempt {attempt}")
                    break
            else:
                msg = f"Hard gate still failing after {REVISION_MAX_ATTEMPTS} revision attempts"
                if verbose:
                    print(f"  {msg}")
                raise RuntimeError(msg)

        report = verify_checkpoint(director.store, name)
        report.step_failures = workflow_step_failures.get(wid, 0)

        # Gate on step failures — editorial is excluded because the revision
        # loop re-runs it after critique contracts exist.
        if report.step_failures > 0 and name != "editorial":
            report.passed = False
            report.messages[0] = f"Checkpoint '{name}' FAILED"
            report.errors.append(f"  {report.step_failures} step(s) failed in {wid}")

        reports.append(report)

        if report.passed:
            director.store.mark_checkpoint(name)

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


def _checkpoint_introduces_new_types(name: str) -> bool:
    """Check if this checkpoint requires contract types the previous one didn't.

    The checkpoints ``structure``, ``draft``, and ``editorial`` share the
    same contract type requirements as their predecessors (``premise`` and
    ``scenes`` respectively).  For these, contract-count verification alone
    can't distinguish a completed checkpoint from an un-run one; we rely
    on the store's ``_completed_checkpoints`` set instead.
    """
    # Checkpoints that share contract type requirements with their predecessor
    # cannot be verified by contract counts alone. The store's _completed_checkpoints
    # set is the authoritative source.
    if name in ("structure", "draft", "editorial", "final"):
        return False
    prev_types: set[str] = set()
    for n in CHECKPOINT_ORDER:
        expected = set(expected_contracts_at_checkpoint(n).keys())
        if n == name:
            return expected != prev_types
        prev_types = expected
    return True


def find_next_checkpoint(store: ContractStore, target: str) -> str | None:
    """Find the first checkpoint that is NOT yet satisfied by the store.

    Iterates through checkpoint order and runs ``verify_checkpoint`` on each.
    Returns the name of the first failing checkpoint, or ``None`` if all
    checkpoints up to (and including) ``target`` are already satisfied.

    This is used by the CLI to auto-detect a ``start_from`` point when loading
    saved pipeline state.
    """
    for name in CHECKPOINT_ORDER:
        # Checkpoints that don't introduce new contract types
        # (structure, draft, editorial) can only be verified via
        # the store's _completed_checkpoints, not by contract counts.
        if not _checkpoint_introduces_new_types(name):
            if not store.is_checkpoint_completed(name):
                return name
        else:
            report = verify_checkpoint(store, name)
            if not report.passed:
                return name
        if name == target:
            return None
    return None
