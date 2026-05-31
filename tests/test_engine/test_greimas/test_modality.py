"""Tests for the modality rules engine."""

import pytest

from src.engine.greimas.modality import ModalityValidator
from src.contracts.models import ModalityState, ModalityType


class TestModalityValidator:
    def test_can_execute_with_wanting_and_able(self):
        can, msg = ModalityValidator.can_execute_action(
            ModalityState.DESIRES, ModalityState.ABLE, ModalityState.FREE
        )
        assert can is True
        assert msg == ""

    def test_can_execute_with_wanting_and_obligated(self):
        can, msg = ModalityValidator.can_execute_action(
            ModalityState.DESIRES, ModalityState.UNABLE, ModalityState.OBLIGATED
        )
        assert can is True

    def test_cannot_execute_without_wanting(self):
        can, msg = ModalityValidator.can_execute_action(
            ModalityState.INDIFFERENT, ModalityState.ABLE, ModalityState.FREE
        )
        assert can is False

    def test_cannot_execute_without_able_or_obligated(self):
        can, msg = ModalityValidator.can_execute_action(
            ModalityState.DESIRES, ModalityState.UNABLE, ModalityState.FREE
        )
        assert can is False

    def test_tension_detected(self):
        tension = ModalityValidator.has_tension(
            ModalityState.DESIRES, ModalityState.FREE
        )
        assert tension is True

    def test_no_tension(self):
        tension = ModalityValidator.has_tension(
            ModalityState.DESIRES, ModalityState.OBLIGATED
        )
        assert tension is False

    def test_check_modality_set_valid(self):
        result = ModalityValidator.check_modality_set(
            actant_id="hero",
            wanting=ModalityState.DESIRES,
            knowing=ModalityState.KNOWS,
            being_able=ModalityState.ABLE,
            having_to=ModalityState.OBLIGATED,
        )
        assert result.is_consistent is True

    def test_check_modality_set_blocked(self):
        result = ModalityValidator.check_modality_set(
            actant_id="hero",
            wanting=ModalityState.INDIFFERENT,
            knowing=ModalityState.KNOWS,
            being_able=ModalityState.ABLE,
            having_to=ModalityState.FREE,
        )
        assert result.is_consistent is False
        assert any("blocked" in i.lower() for i in result.global_issues)

    def test_check_modality_set_ignorant_warning(self):
        result = ModalityValidator.check_modality_set(
            actant_id="hero",
            wanting=ModalityState.DESIRES,
            knowing=ModalityState.IGNORANT,
            being_able=ModalityState.ABLE,
            having_to=ModalityState.FREE,
        )
        assert any("IGNORANT" in i for i in result.global_issues)

    def test_transition_valid(self):
        result = ModalityValidator.check_transition(
            ModalityType.WANTING,
            ModalityState.INDIFFERENT,
            ModalityState.DESIRES,
            trigger="Hero encounters the Object of value",
        )
        assert result.is_valid is True

    def test_transition_no_trigger(self):
        result = ModalityValidator.check_transition(
            ModalityType.KNOWING,
            ModalityState.IGNORANT,
            ModalityState.KNOWS,
            trigger="",
        )
        assert result.is_valid is False
        assert "no trigger" in result.issues[0]

    def test_check_modality_set_with_strings(self):
        result = ModalityValidator.check_modality_set(
            actant_id="hero",
            wanting="desires",
            knowing="knows",
            being_able="able",
            having_to="free",
        )
        # Tension is flagged but actant CAN act (wants AND able)
        can_act, _ = ModalityValidator.can_execute_action(
            ModalityState.DESIRES, ModalityState.ABLE, ModalityState.FREE
        )
        assert can_act is True
