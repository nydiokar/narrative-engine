"""Tests for the narrative program and canonical schema checker."""

from uuid import uuid4

import pytest

from src.engine.greimas.narrative_program import (
    CanonicalPhase,
    CanonicalSchemaChecker,
    EpisodeTrackingValidator,
    NarrativeProgramData,
    NarrativeProgramValidationResult,
    PhaseValidationResult,
)


class TestCanonicalSchemaChecker:
    def test_valid_phase_order(self):
        issues = CanonicalSchemaChecker.validate_phase_order({
            "manipulation": True,
            "competence": True,
            "performance": True,
            "sanction": True,
        })
        assert issues == []

    def test_invalid_phase_order_gap(self):
        issues = CanonicalSchemaChecker.validate_phase_order({
            "manipulation": True,
            "competence": False,
            "performance": True,
            "sanction": True,
        })
        assert len(issues) > 0
        assert "performance" in issues[0].lower()

    def test_valid_narrative_program(self):
        np_data = NarrativeProgramData(
            id=uuid4(),
            subject="hero",
            object_of_value_id="freedom",
            object_of_value_type="freedom",
            manipulation_completed=True,
            competence_completed=True,
            performance_completed=True,
            sanction_completed=True,
            manipulation_sender="oracle",
            competence_modalities=["knowing", "being_able"],
            performance_operation="battle",
            sanction_judgment="positive",
            junction_initial="disjunction",
            junction_terminal="conjunction",
        )
        result = CanonicalSchemaChecker.validate_narrative_program(np_data)
        assert result.is_valid is True

    def test_invalid_no_terminal_change(self):
        np_data = NarrativeProgramData(
            id=uuid4(),
            subject="hero",
            object_of_value_id="freedom",
            object_of_value_type="freedom",
            manipulation_completed=True,
            competence_completed=True,
            performance_completed=True,
            sanction_completed=True,
            junction_initial="disjunction",
            junction_terminal="disjunction",  # no change
        )
        result = CanonicalSchemaChecker.validate_narrative_program(np_data)
        assert result.is_valid is False

    def test_invalid_missing_sender(self):
        np_data = NarrativeProgramData(
            id=uuid4(),
            subject="hero",
            object_of_value_id="freedom",
            object_of_value_type="freedom",
            manipulation_completed=True,
            manipulation_sender="",  # missing
        )
        result = CanonicalSchemaChecker.validate_narrative_program(np_data)
        assert result.is_valid is False

    def test_invalid_missing_operation(self):
        np_data = NarrativeProgramData(
            id=uuid4(),
            subject="hero",
            object_of_value_id="freedom",
            object_of_value_type="freedom",
            manipulation_completed=True,
            competence_completed=True,
            performance_completed=True,
            performance_operation="",  # missing
            manipulation_sender="oracle",
            competence_modalities=["knowing"],
            junction_initial="disjunction",
            junction_terminal="conjunction",
        )
        result = CanonicalSchemaChecker.validate_narrative_program(np_data)
        assert result.is_valid is False

    def test_validate_from_dict(self):
        data = {
            "id": str(uuid4()),
            "subject": "hero",
            "object_of_value": {"id": "oov1", "type": "freedom"},
            "canonical_phases": {
                "manipulation": {"sender": "oracle", "completed": True},
                "competence": {"modalities_acquired": ["knowing"], "completed": True},
                "performance": {"operation": "battle", "completed": True},
                "sanction": {"judgment": "positive", "completed": True},
            },
            "initial_state": {"junction": "disjunction"},
            "terminal_state": {"junction": "conjunction"},
        }
        result = CanonicalSchemaChecker.validate_from_dict(data)
        assert result.is_valid is True


class TestEpisodeTrackingValidator:
    def test_valid_tracking(self):
        tracking = {
            "episode_id": "ep1",
            "subject": "hero",
            "object_of_value": "freedom",
            "current_state": "disjunct from freedom",
            "desired_transformation": "acquire freedom",
            "opponent": "tyrant",
            "opponent_value_logic": "control",
            "helper": "mentor",
            "action_type": "battle",
            "resulting_state": "conjunct with freedom",
            "sanction_or_judgment": "recognized as liberator",
            "contribution": "establishes hero's legitimacy",
        }
        result = EpisodeTrackingValidator.validate_tracking(tracking)
        assert result.is_complete is True
        assert result.missing_fields == []

    def test_missing_fields(self):
        tracking = {
            "episode_id": "ep1",
            "subject": "hero",
            "object_of_value": "freedom",
        }
        result = EpisodeTrackingValidator.validate_tracking(tracking)
        assert result.is_complete is False
        assert "current_state" in result.missing_fields
        assert "desired_transformation" in result.missing_fields
        assert "opponent" in result.missing_fields
