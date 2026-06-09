"""Tests for the Fabula Coherence Engine (10 checks)."""

import pytest

from src.engine.fabula.coherence import FabulaCoherenceEngine, FabulaCoherenceReport
from src.contracts.models import CoherenceCheckResult


class TestFabulaCoherenceEngine:
    def test_all_checks_pass_with_valid_data(self):
        events = [
            {
                "id": "evt1", "sequence_number": 0,
                "causal_predecessors": [],
                "value_object_change": "introduced",
                "modality_changes": [{"actant_id": "hero", "modality": "wanting", "from_state": "indifferent", "to_state": "desires", "trigger": "oracle speaks"}],
                "state_after": "hero desires freedom",
                "unlocks": "hero can now seek freedom",
            },
            {
                "id": "evt2", "sequence_number": 1,
                "causal_predecessors": ["evt1"],
                "value_object_change": "transferred",
                "modality_changes": [{"actant_id": "hero", "modality": "being_able", "from_state": "unable", "to_state": "able", "trigger": "receives sword"}],
                "state_after": "hero is able to fight",
                "unlocks": "hero can engage tyrant",
            },
        ]
        scenes = [
            {
                "greimas_diagnostic": {"value_object_change": "acquired"},
                "conflict_load": {"internal": "medium", "interpersonal": "high"},
            }
        ]
        characters = [
            {"id": "hero", "core_desires": ["freedom"], "core_fears": ["captivity"]}
        ]

        episodes = [
            {
                "title": "Ep1", "sequence_number": 0,
                "propp_functions": ["villainy", "struggle", "victory", "liquidation"],
            }
        ]
        report = FabulaCoherenceEngine.run_all_checks(
            events=events, scenes=scenes, characters=characters, episodes=episodes
        )
        assert report.passed is True
        assert len(report.checks) == 11

    def test_causal_soundness_fails_orphan(self):
        events = [
            {"id": "evt1", "sequence_number": 0, "causal_predecessors": []},
            {"id": "evt2", "sequence_number": 1, "causal_predecessors": []},  # orphan
        ]
        check = FabulaCoherenceEngine.check_causal_soundness(events)
        assert check.passed is False
        assert any("no causal predecessors" in v for v in check.violations)

    def test_stakes_presence_fails(self):
        scenes = [
            {"greimas_diagnostic": {"value_object_change": "none"}}
        ]
        check = FabulaCoherenceEngine.check_stakes_presence(scenes)
        assert check.passed is False

    def test_stakes_presence_passes(self):
        scenes = [
            {"greimas_diagnostic": {"value_object_change": "transferred"}}
        ]
        check = FabulaCoherenceEngine.check_stakes_presence(scenes)
        assert check.passed is True

    def test_conflict_active_fails(self):
        scenes = [
            {"conflict_load": {"internal": "none", "interpersonal": "none"}}
        ]
        check = FabulaCoherenceEngine.check_conflict_active(scenes)
        assert check.passed is False

    def test_conflict_active_passes(self):
        scenes = [
            {"conflict_load": {"internal": "high"}}
        ]
        check = FabulaCoherenceEngine.check_conflict_active(scenes)
        assert check.passed is True

    def test_event_necessity_fails(self):
        events = [
            {
                "id": "evt1", "sequence_number": 0,
                "causal_predecessors": [],
                "value_object_change": "none",
                "modality_changes": [],
                "unlocks": "",
                "blocks": "",
            }
        ]
        check = FabulaCoherenceEngine.check_event_necessity(events)
        assert check.passed is False
        assert any("filler" in v for v in check.violations)

    def test_event_necessity_passes_on_unlocks(self):
        events = [
            {
                "id": "evt1", "sequence_number": 0,
                "causal_predecessors": [],
                "value_object_change": "none",
                "modality_changes": [],
                "unlocks": "hero can now enter the castle",
                "blocks": "",
            }
        ]
        check = FabulaCoherenceEngine.check_event_necessity(events)
        assert check.passed is True

    def test_character_intentionality_fails(self):
        events = [
            {"id": "evt1", "sequence_number": 0, "causal_predecessors": [], "actant": "hero", "operation": "fights"}
        ]
        characters = [
            {"id": "hero", "core_desires": [], "core_fears": []}
        ]
        check = FabulaCoherenceEngine.check_character_intentionality(events, characters)
        assert check.passed is False

    def test_empty_events_no_crash(self):
        report = FabulaCoherenceEngine.run_all_checks()
        assert len(report.checks) == 11
        # causal_soundness on empty list should pass
        assert report.checks[0].passed is True

    def test_summary_format(self):
        report = FabulaCoherenceEngine.run_all_checks(events=[], scenes=[], episodes=[])
        assert "Fabula Coherence" in report.summary
