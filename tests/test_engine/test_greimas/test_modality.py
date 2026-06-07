"""Tests for the modality rules engine."""
import pytest

from src.engine.greimas.modality import ModalityValidator
from src.contracts.models import (
    BeingAbleState,
    HavingToState,
    KnowingState,
    ModalityState,
    ModalityType,
    WantingState,
)


class TestModalityValidator:
    def test_can_execute_with_wanting_and_able(self):
        can, msg = ModalityValidator.can_execute_action(
            WantingState.DESIRES, BeingAbleState.ABLE, HavingToState.FREE
        )
        assert can is True
        assert msg == ""

    def test_can_execute_with_wanting_and_obligated(self):
        can, msg = ModalityValidator.can_execute_action(
            WantingState.DESIRES, BeingAbleState.UNABLE, HavingToState.OBLIGATED
        )
        assert can is True

    def test_cannot_execute_without_wanting(self):
        can, msg = ModalityValidator.can_execute_action(
            WantingState.INDIFFERENT, BeingAbleState.ABLE, HavingToState.FREE
        )
        assert can is False

    def test_cannot_execute_without_able_or_obligated(self):
        can, msg = ModalityValidator.can_execute_action(
            WantingState.DESIRES, BeingAbleState.UNABLE, HavingToState.FREE
        )
        assert can is False

    def test_tension_detected(self):
        tension = ModalityValidator.has_tension(
            WantingState.DESIRES, HavingToState.FREE
        )
        assert tension is True

    def test_no_tension(self):
        tension = ModalityValidator.has_tension(
            WantingState.DESIRES, HavingToState.OBLIGATED
        )
        assert tension is False

    def test_check_modality_set_valid(self):
        result = ModalityValidator.check_modality_set(
            actant_id="hero",
            wanting=WantingState.DESIRES,
            knowing=KnowingState.KNOWS,
            being_able=BeingAbleState.ABLE,
            having_to=HavingToState.OBLIGATED,
        )
        assert result.is_consistent is True

    def test_check_modality_set_blocked(self):
        result = ModalityValidator.check_modality_set(
            actant_id="hero",
            wanting=WantingState.INDIFFERENT,
            knowing=KnowingState.KNOWS,
            being_able=BeingAbleState.ABLE,
            having_to=HavingToState.FREE,
        )
        assert result.is_consistent is False
        assert any("blocked" in i.lower() for i in result.global_issues)

    def test_check_modality_set_ignorant_warning(self):
        result = ModalityValidator.check_modality_set(
            actant_id="hero",
            wanting=WantingState.DESIRES,
            knowing=KnowingState.IGNORANT,
            being_able=BeingAbleState.ABLE,
            having_to=HavingToState.FREE,
        )
        assert any("IGNORANT" in i for i in result.global_issues)

    def test_transition_valid(self):
        result = ModalityValidator.check_transition(
            ModalityType.WANTING,
            WantingState.INDIFFERENT,
            WantingState.DESIRES,
            trigger="Hero encounters the Object of value",
        )
        assert result.is_valid is True

    def test_transition_no_trigger(self):
        result = ModalityValidator.check_transition(
            ModalityType.KNOWING,
            KnowingState.IGNORANT,
            KnowingState.KNOWS,
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
        can_act, _ = ModalityValidator.can_execute_action(
            WantingState.DESIRES, BeingAbleState.ABLE, HavingToState.FREE
        )
        assert can_act is True

    def test_backward_compat_modality_state(self):
        """ModalityState enum still works for serialization/deserialization."""
        assert ModalityState.DESIRES.value == "desires"
        assert ModalityState.KNOWS.value == "knows"
        assert ModalityState.ABLE.value == "able"
        assert ModalityState.OBLIGATED.value == "obligated"
