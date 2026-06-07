"""Modality rules — the four modal competences (vouloir, savoir, pouvoir, devoir).

Modalities qualify an actant's capacity to act and follow strict consistency
and combination rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Union

from src.contracts.models import (
    BeingAbleState,
    HavingToState,
    KnowingState,
    ModalityState,
    ModalityType,
    WantingState,
)


@dataclass
class ModalityCheckResult:
    modality: ModalityType
    state: Any
    is_valid: bool = True
    issues: list[str] = field(default_factory=list)


@dataclass
class ModalityConsistencyResult:
    actant_id: str
    is_consistent: bool = True
    check_results: list[ModalityCheckResult] = field(default_factory=list)
    global_issues: list[str] = field(default_factory=list)


class ModalityValidator:
    """Validates modality states, transitions, and combination rules.

    Rules from the specification:
    1. An actant can only execute an action if wanting AND (being_able OR having_to)
    2. Knowing modifies the quality but not the possibility of action
    3. Conflicting modalities (wanting ≠ having_to) generate tension (not an error)
    """

    @staticmethod
    def can_execute_action(
        wanting: WantingState | str,
        being_able: BeingAbleState | str,
        having_to: HavingToState | str,
    ) -> tuple[bool, str]:
        """Rule 1: Actant can act if wanting AND (being_able OR having_to)."""
        if isinstance(wanting, str):
            wanting = WantingState(wanting)
        if isinstance(being_able, str):
            being_able = BeingAbleState(being_able)
        if isinstance(having_to, str):
            having_to = HavingToState(having_to)
        wants = wanting == WantingState.DESIRES
        able = being_able == BeingAbleState.ABLE
        obligated = having_to == HavingToState.OBLIGATED

        if not wants:
            return False, "Actant does not want to act (wanting != DESIRES)"

        if not able and not obligated:
            return False, (
                "Actant wants to act but is neither ABLE nor OBLIGATED — "
                "action impossible"
            )

        return True, ""

    @staticmethod
    def has_tension(
        wanting: WantingState | str,
        having_to: HavingToState | str,
    ) -> bool:
        """Rule 3: Conflicting modalities generate narrative tension.

        Tension exists when the actant's desire and obligation pull in
        opposite directions:
        - Wants to act but is not obligated (free desire)
        - Does not want to act but is forced (coerced)
        - Indifferent but obligated (reluctant duty)
        """
        if isinstance(wanting, str):
            wanting = WantingState(wanting)
        if isinstance(having_to, str):
            having_to = HavingToState(having_to)
        return (
            (wanting == WantingState.DESIRES and having_to != HavingToState.OBLIGATED)
            or (wanting == WantingState.REJECTS and having_to == HavingToState.OBLIGATED)
            or (wanting == WantingState.INDIFFERENT and having_to == HavingToState.OBLIGATED)
        )

    @staticmethod
    def check_modality_set(
        actant_id: str,
        wanting: WantingState | str,
        knowing: KnowingState | str,
        being_able: BeingAbleState | str,
        having_to: HavingToState | str,
    ) -> ModalityConsistencyResult:
        if isinstance(wanting, str):
            wanting = WantingState(wanting)
        if isinstance(knowing, str):
            knowing = KnowingState(knowing)
        if isinstance(being_able, str):
            being_able = BeingAbleState(being_able)
        if isinstance(having_to, str):
            having_to = HavingToState(having_to)

        results: list[ModalityCheckResult] = []
        global_issues: list[str] = []

        for mod, name in [
            (wanting, "wanting"),
            (knowing, "knowing"),
            (being_able, "being_able"),
            (having_to, "having_to"),
        ]:
            results.append(ModalityCheckResult(
                modality=ModalityType(name),
                state=mod,
                is_valid=True,
            ))

        can_act, msg = ModalityValidator.can_execute_action(wanting, being_able, having_to)
        tension = ModalityValidator.has_tension(wanting, having_to)

        if not can_act:
            global_issues.append(f"Action blocked for {actant_id}: {msg}")

        if tension:
            global_issues.append(
                f"Narrative tension: {actant_id} wants={wanting.value} but "
                f"having_to={having_to.value}"
            )

        # Knowing quality modifier
        if knowing == KnowingState.IGNORANT and can_act:
            global_issues.append(
                f"{actant_id} can act but is IGNORANT — action quality may be impaired"
            )

        return ModalityConsistencyResult(
            actant_id=actant_id,
            is_consistent=len(global_issues) == 0,
            check_results=results,
            global_issues=global_issues,
        )

    @staticmethod
    def check_transition(
        modality: ModalityType,
        from_state: ModalityState | str,
        to_state: ModalityState | str,
        trigger: str = "",
    ) -> ModalityCheckResult:
        """Validate that a modality transition has a non-empty trigger."""
        if isinstance(from_state, str):
            from_state = ModalityState(from_state)
        if isinstance(to_state, str):
            to_state = ModalityState(to_state)

        issues: list[str] = []

        if not trigger.strip():
            issues.append(
                f"Transition {modality.value}: {from_state.value} → {to_state.value} "
                "has no trigger — modality changed without cause"
            )

        return ModalityCheckResult(
            modality=modality,
            state=to_state,
            is_valid=len(issues) == 0,
            issues=issues,
        )
