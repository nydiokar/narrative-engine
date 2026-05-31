"""Action/State logic (действие / състояние) — the fundamental narrative unit.

Every meaningful action must transform a state. Every important state must
condition possible actions. This module provides the 5-question scene
diagnostic and the action/state validator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StateType(str, Enum):
    LACK = "state_of_lack"
    FULFILLMENT = "state_of_fulfillment"
    TEST = "state_of_test"
    CONFLICT = "state_of_conflict"
    ALLIANCE = "state_of_alliance"
    MISRECOGNITION = "state_of_misrecognition"
    QUALIFICATION = "state_of_qualification"
    PERFORMANCE = "state_of_performance"
    REVELATION = "state_of_revelation"
    JUDGMENT = "state_of_judgment"


@dataclass
class SceneDiagnosticResult:
    q1_state_before: str = ""
    q2_action_occurs: str = ""
    q3_state_after: str = ""
    q4_value_object_change: str = "none"
    q5_future_possible_or_blocked: str = ""
    
    passes: bool = False
    failures: list[str] = field(default_factory=list)


class SceneDiagnosticEngine:
    """Runs the 5-question Greimas diagnostic on a scene.

    Each scene must answer:
    1. What state exists before the scene?
    2. What action occurs?
    3. What state changes after the action?
    4. Which value-object increased, decreased, transferred, revealed,
       corrupted, or became desirable?
    5. Which future action is now possible or impossible?
    """

    @staticmethod
    def run_diagnostic(
        state_before: str,
        action: str,
        state_after: str,
        value_object_change: str,
        future_effect: str,
    ) -> SceneDiagnosticResult:
        result = SceneDiagnosticResult(
            q1_state_before=state_before,
            q2_action_occurs=action,
            q3_state_after=state_after,
            q4_value_object_change=value_object_change,
            q5_future_possible_or_blocked=future_effect,
        )

        if not state_before.strip():
            result.failures.append("Q1: No state_before defined — missing baseline configuration")

        if not action.strip():
            result.failures.append("Q2: No action defined — scene has no operation")

        if not state_after.strip():
            result.failures.append("Q3: No state_after defined — cannot confirm transformation")

        if action.strip() and state_before.strip() and state_after.strip():
            if state_before.strip() == state_after.strip():
                result.failures.append("Q3: State did not change — action does not transform")

        if value_object_change.strip().lower() in ("", "none", "unchanged"):
            result.failures.append("Q4: No value-object change — nothing was gained, lost, or redefined")

        if not future_effect.strip():
            result.failures.append("Q5: No future action enabled or blocked — scene is causally dead")

        result.passes = len(result.failures) == 0
        return result

    @staticmethod
    def run_on_scene_dict(scene: dict[str, Any]) -> SceneDiagnosticResult:
        """Run the diagnostic from a scene-like dict (e.g. a SceneContract model_dump)."""
        greimas = scene.get("greimas_diagnostic", {})
        if isinstance(greimas, dict):
            state_before = greimas.get("state_before", "")
            action = greimas.get("action_occurs", "")
            state_after = greimas.get("state_after", "")
            value_change = greimas.get("value_object_change", "none")
            future_effect = greimas.get("future_action_possible_or_blocked", "")
        else:
            state_before = getattr(greimas, "state_before", "")
            action = getattr(greimas, "action_occurs", "")
            state_after = getattr(greimas, "state_after", "")
            value_change = getattr(greimas, "value_object_change", "none")
            future_effect = getattr(greimas, "future_action_possible_or_blocked", "")

        return SceneDiagnosticEngine.run_diagnostic(
            state_before=state_before or "",
            action=action or "",
            state_after=state_after or "",
            value_object_change=value_change or "none",
            future_effect=future_effect or "",
        )


@dataclass
class ActionStateValidationResult:
    is_valid: bool = False
    issues: list[str] = field(default_factory=list)
    state_type_before: StateType | None = None
    state_type_after: StateType | None = None


class ActionStateValidator:
    """Validates that actions actually transform states per Greimas rules."""

    VALID_TRANSITIONS: dict[StateType, set[StateType]] = {
        StateType.LACK: {StateType.QUALIFICATION, StateType.CONFLICT, StateType.FULFILLMENT},
        StateType.FULFILLMENT: {StateType.JUDGMENT, StateType.CONFLICT, StateType.LACK},
        StateType.TEST: {StateType.QUALIFICATION, StateType.CONFLICT, StateType.JUDGMENT},
        StateType.CONFLICT: {StateType.ALLIANCE, StateType.FULFILLMENT, StateType.LACK, StateType.JUDGMENT, StateType.REVELATION},
        StateType.ALLIANCE: {StateType.CONFLICT, StateType.FULFILLMENT, StateType.TEST},
        StateType.MISRECOGNITION: {StateType.REVELATION, StateType.CONFLICT, StateType.JUDGMENT},
        StateType.QUALIFICATION: {StateType.PERFORMANCE, StateType.TEST, StateType.CONFLICT},
        StateType.PERFORMANCE: {StateType.JUDGMENT, StateType.FULFILLMENT, StateType.LACK},
        StateType.REVELATION: {StateType.JUDGMENT, StateType.CONFLICT, StateType.FULFILLMENT},
        StateType.JUDGMENT: {StateType.FULFILLMENT, StateType.LACK, StateType.MISRECOGNITION},
    }

    @classmethod
    def validate_transition(
        cls,
        state_before: StateType | str,
        state_after: StateType | str,
        action_description: str = "",
    ) -> ActionStateValidationResult:
        if isinstance(state_before, str):
            try:
                state_before = StateType(state_before)
            except ValueError:
                return ActionStateValidationResult(
                    is_valid=False,
                    issues=[f"Unknown state type: {state_before}"],
                )
        if isinstance(state_after, str):
            try:
                state_after = StateType(state_after)
            except ValueError:
                return ActionStateValidationResult(
                    is_valid=False,
                    issues=[f"Unknown state type: {state_after}"],
                )

        if state_before == state_after:
            return ActionStateValidationResult(
                is_valid=False,
                state_type_before=state_before,
                state_type_after=state_after,
                issues=["Action did not change state type — filler by definition"],
            )

        valid_targets = cls.VALID_TRANSITIONS.get(state_before, set())
        if state_after not in valid_targets:
            return ActionStateValidationResult(
                is_valid=False,
                state_type_before=state_before,
                state_type_after=state_after,
                issues=[
                    f"Invalid transition: {state_before.value} → {state_after.value}. "
                    f"Valid targets: {[s.value for s in valid_targets]}"
                ],
            )

        return ActionStateValidationResult(
            is_valid=True,
            state_type_before=state_before,
            state_type_after=state_after,
        )

    @classmethod
    def validate_scene_diagnostic(
        cls, diagnostic: SceneDiagnosticResult
    ) -> ActionStateValidationResult:
        if not diagnostic.passes:
            return ActionStateValidationResult(
                is_valid=False,
                issues=diagnostic.failures[:],
            )
        return ActionStateValidationResult(is_valid=True)
