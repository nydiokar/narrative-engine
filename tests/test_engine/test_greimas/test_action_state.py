"""Tests for the action/state diagnostic engine."""

import pytest

from src.engine.greimas.action_state import (
    ActionStateValidator,
    SceneDiagnosticEngine,
    SceneDiagnosticResult,
    StateType,
)


class TestSceneDiagnosticEngine:
    def test_passes_complete_scene(self):
        result = SceneDiagnosticEngine.run_diagnostic(
            state_before="The hero is disjunct from the grail.",
            action="The hero crosses the threshold.",
            state_after="The hero is conjunct with the grail.",
            value_object_change="acquired",
            future_effect="The hero can now return home.",
        )
        assert result.passes is True
        assert len(result.failures) == 0

    def test_fails_missing_state_before(self):
        result = SceneDiagnosticEngine.run_diagnostic(
            state_before="",
            action="Something happens.",
            state_after="Stuff changed.",
            value_object_change="acquired",
            future_effect="More can happen.",
        )
        assert result.passes is False
        assert any("Q1" in f for f in result.failures)

    def test_fails_missing_action(self):
        result = SceneDiagnosticEngine.run_diagnostic(
            state_before="A state exists.",
            action="",
            state_after="Same state.",
            value_object_change="none",
            future_effect="",
        )
        assert result.passes is False
        assert any("Q2" in f for f in result.failures)

    def test_fails_no_state_change(self):
        result = SceneDiagnosticEngine.run_diagnostic(
            state_before="The hero waits.",
            action="The hero waits some more.",
            state_after="The hero waits.",
            value_object_change="none",
            future_effect="The hero keeps waiting.",
        )
        assert result.passes is False
        assert any("Q3" in f for f in result.failures)

    def test_fails_no_value_change(self):
        result = SceneDiagnosticEngine.run_diagnostic(
            state_before="State A.",
            action="Action happens.",
            state_after="State B.",
            value_object_change="none",
            future_effect="Future unfolds.",
        )
        assert result.passes is False
        assert any("Q4" in f for f in result.failures)

    def test_fails_no_future_effect(self):
        result = SceneDiagnosticEngine.run_diagnostic(
            state_before="State A.",
            action="Action.",
            state_after="State B.",
            value_object_change="transferred",
            future_effect="",
        )
        assert result.passes is False
        assert any("Q5" in f for f in result.failures)

    def test_run_on_scene_dict(self):
        scene = {
            "greimas_diagnostic": {
                "state_before": "Lack of freedom.",
                "action_occurs": "Hero rebels.",
                "state_after": "Freedom achieved.",
                "value_object_change": "acquired",
                "future_action_possible_or_blocked": "Community can rebuild.",
            }
        }
        result = SceneDiagnosticEngine.run_on_scene_dict(scene)
        assert result.passes is True

    def test_run_on_scene_dict_empty(self):
        result = SceneDiagnosticEngine.run_on_scene_dict({})
        assert result.passes is False


class TestActionStateValidator:
    def test_valid_transition(self):
        result = ActionStateValidator.validate_transition(
            StateType.LACK, StateType.QUALIFICATION
        )
        assert result.is_valid is True

    def test_invalid_transition(self):
        result = ActionStateValidator.validate_transition(
            StateType.FULFILLMENT, StateType.TEST
        )
        assert result.is_valid is False  # FULFILLMENT cannot transition directly to TEST

    def test_self_transition_is_filler(self):
        result = ActionStateValidator.validate_transition(
            StateType.CONFLICT, StateType.CONFLICT
        )
        assert result.is_valid is False
        assert "filler" in result.issues[0].lower()

    def test_unknown_state_type(self):
        result = ActionStateValidator.validate_transition("unknown_type", StateType.LACK)
        assert result.is_valid is False

    def test_validate_scene_diagnostic_passing(self):
        diag = SceneDiagnosticResult(
            q1_state_before="A",
            q2_action_occurs="B",
            q3_state_after="C",
            q4_value_object_change="transferred",
            q5_future_possible_or_blocked="D",
            passes=True,
        )
        result = ActionStateValidator.validate_scene_diagnostic(diag)
        assert result.is_valid is True

    def test_validate_scene_diagnostic_failing(self):
        diag = SceneDiagnosticResult(
            q1_state_before="",
            q2_action_occurs="B",
            q3_state_after="C",
            q4_value_object_change="none",
            q5_future_possible_or_blocked="",
            passes=False,
            failures=["Q1: No state_before defined"],
        )
        result = ActionStateValidator.validate_scene_diagnostic(diag)
        assert result.is_valid is False
