"""Todorovian narrative equilibrium — the 5-phase arc and sequence validation.

Based on Tzvetan Todorov's theory of narrative as transformation between
states of equilibrium. Every narrative episode maps to a phase in this arc.
The validator checks that:

1. Phases appear in canonical order (no regression)
2. Disruption is present if any later phase appears
3. The sequence is non-empty
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TodorovPhase(str, Enum):
    """The 5 phases of Todorov's narrative equilibrium model.

    A complete narrative traces: equilibrium → disruption → recognition
    → repair → new_equilibrium. Phases may be skipped but must not
    regress.
    """

    EQUILIBRIUM = "equilibrium"
    DISRUPTION = "disruption"
    RECOGNITION = "recognition"
    REPAIR = "repair"
    NEW_EQUILIBRIUM = "new_equilibrium"


# Canonical order of Todorov phases
_CANONICAL_ORDER: list[TodorovPhase] = [
    TodorovPhase.EQUILIBRIUM,
    TodorovPhase.DISRUPTION,
    TodorovPhase.RECOGNITION,
    TodorovPhase.REPAIR,
    TodorovPhase.NEW_EQUILIBRIUM,
]

_CANONICAL_INDEX: dict[TodorovPhase, int] = {
    p: i for i, p in enumerate(_CANONICAL_ORDER)
}


@dataclass
class TodorovValidationResult:
    """Result of validating a Todorov phase sequence."""

    passed: bool = False
    violations: list[str] = field(default_factory=list)
    episode_count: int = 0
    phases_found: list[TodorovPhase] = field(default_factory=list)


class TodorovValidator:
    """Validates that a sequence of episodes follows Todorov's equilibrium model."""

    @classmethod
    def validate_sequence(
        cls,
        phases: list[TodorovPhase],
        episode_label: str = "",
    ) -> TodorovValidationResult:
        """Validate a sequence of Todorov phases across episodes.

        Rules:
        1. Canonical order — phases must not regress backward
        2. Disruption required — if any phase beyond disruption appears,
           disruption must be present
        3. No empty sequence
        """
        violations: list[str] = []
        prefix = f"[{episode_label}] " if episode_label else ""

        if not phases:
            return TodorovValidationResult(
                passed=False,
                violations=[f"{prefix}Empty Todorov sequence — at least one phase is required"],
                episode_count=0,
            )

        # Rule 1: Canonical order (no regression)
        last_valid_index = -1
        for p in phases:
            idx = _CANONICAL_INDEX.get(p, -1)
            if idx == -1:
                violations.append(
                    f"{prefix}Unknown Todorov phase '{p.value}'"
                )
                continue
            if idx < last_valid_index:
                violations.append(
                    f"{prefix}Phase regression: '{p.value}' "
                    f"(canonical position {idx}) appears after position {last_valid_index}"
                )
            last_valid_index = idx

        # Rule 2: Disruption must be present if any later phase appears
        present = set(phases)
        later_phases = {
            TodorovPhase.RECOGNITION,
            TodorovPhase.REPAIR,
            TodorovPhase.NEW_EQUILIBRIUM,
        }
        if later_phases & present and TodorovPhase.DISRUPTION not in present:
            violations.append(
                f"{prefix}Missing 'disruption' — required when later phases appear"
            )

        return TodorovValidationResult(
            passed=len(violations) == 0,
            violations=violations,
            episode_count=len(phases),
            phases_found=phases,
        )

    @classmethod
    def validate_episodes(
        cls,
        episodes: list[dict[str, Any]],
    ) -> TodorovValidationResult:
        """Validate the Todorov phase sequence across all episodes.

        Phases are extracted from the ``todorov_phase`` key on each episode
        dict. If ``todorov_phase`` is missing or empty on every episode,
        the validation passes (backward compatible — no data to check).
        """
        if not episodes:
            return TodorovValidationResult(
                passed=True,
                violations=[],
                episode_count=0,
            )

        phases: list[TodorovPhase] = []
        parse_errors: list[str] = []

        for ep in episodes:
            raw = ep.get("todorov_phase", "")
            if not raw:
                continue
            try:
                normalized = raw.strip().lower().replace(" ", "_")
                phases.append(TodorovPhase(normalized))
            except ValueError:
                title = ep.get("title", ep.get("id", "?"))
                parse_errors.append(f"[{title}] Unknown Todorov phase: '{raw}'")

        # No Todorov phases specified anywhere — skip (backward compat)
        if not phases and not parse_errors:
            return TodorovValidationResult(
                passed=True,
                violations=[],
                episode_count=len(episodes),
            )

        result = cls.validate_sequence(phases)
        result.violations.extend(parse_errors)
        if parse_errors:
            result.passed = False
        return result
