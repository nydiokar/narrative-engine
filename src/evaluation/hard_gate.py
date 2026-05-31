"""Hard Gate — structural soundness evaluation.

The hard gate rejects narrative artifacts that fail any of the structural
checks. Only candidates that pass the hard gate proceed to soft-gate scoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.engine.fabula.coherence import (
    FabulaCoherenceCheck,
    FabulaCoherenceEngine,
    FabulaCoherenceReport,
)


@dataclass
class HardGateResult:
    passed: bool = False
    coherence_report: FabulaCoherenceReport | None = None
    failure_reasons: list[str] = field(default_factory=list)


class HardGate:
    """Runs all hard-gate checks on a narrative artifact."""

    def evaluate(
        self,
        events: list[dict[str, Any]] | None = None,
        scenes: list[dict[str, Any]] | None = None,
        characters: list[dict[str, Any]] | None = None,
        world_rules: list[str] | None = None,
    ) -> HardGateResult:
        report = FabulaCoherenceEngine.run_all_checks(
            events=events,
            scenes=scenes,
            characters=characters,
            world_rules=world_rules,
        )

        failure_reasons: list[str] = []
        for check in report.checks:
            if not check.passed:
                for v in check.violations:
                    failure_reasons.append(f"[{check.name}] {v}")

        return HardGateResult(
            passed=report.passed,
            coherence_report=report,
            failure_reasons=failure_reasons,
        )
