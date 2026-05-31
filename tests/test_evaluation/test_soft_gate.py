"""Tests for the Soft Gate scoring."""

import pytest

from src.evaluation.soft_gate import SoftGate


class TestSoftGate:
    def test_all_defaults_zero(self):
        gate = SoftGate(threshold=5.0)
        result = gate.evaluate()
        assert result.passed is False
        assert result.composite_score == 0.0

    def test_perfect_scores(self):
        gate = SoftGate(threshold=5.0)
        for dim in gate.dimensions:
            gate.set_score(dim.name, 10)
        result = gate.evaluate()
        assert result.passed is True
        assert result.composite_score == 10.0

    def test_composite_calculation(self):
        gate = SoftGate(threshold=5.0)
        gate.set_score("genre_fit", 8)
        gate.set_score("thematic_clarity", 7)
        result = gate.evaluate()
        assert result.composite_score > 0

    def test_low_scores_produce_notes(self):
        gate = SoftGate(threshold=5.0)
        gate.set_score("novelty", 2, notes="Too generic")
        result = gate.evaluate()
        assert len(result.notes) > 0

    def test_unknown_dimension_raises(self):
        gate = SoftGate()
        with pytest.raises(ValueError, match="Unknown dimension"):
            gate.set_score("fake_dim", 5)
