"""Tests for the Hard Gate evaluation."""

import pytest

from src.evaluation.hard_gate import HardGate


class TestHardGate:
    def test_hard_gate_passes(self):
        gate = HardGate()
        events = [
            {"id": "a", "sequence_number": 0, "causal_predecessors": [], "value_object_change": "introduced", "modality_changes": [{}], "unlocks": "next step", "blocks": ""},
            {"id": "b", "sequence_number": 1, "causal_predecessors": ["a"], "value_object_change": "transferred", "modality_changes": [], "unlocks": "", "blocks": "", "state_after": "new"},
        ]
        scenes = [
            {"greimas_diagnostic": {"value_object_change": "acquired"}, "conflict_load": {"internal": "high"}}
        ]
        result = gate.evaluate(events=events, scenes=scenes)
        assert result.passed is True

    def test_hard_gate_fails(self):
        gate = HardGate()
        events = [
            {"id": "a", "sequence_number": 0, "causal_predecessors": [], "value_object_change": "none", "modality_changes": [], "unlocks": "", "blocks": ""},
        ]
        scenes = [
            {"greimas_diagnostic": {"value_object_change": "none"}, "conflict_load": {}}
        ]
        result = gate.evaluate(events=events, scenes=scenes)
        assert result.passed is False
        assert len(result.failure_reasons) > 0
