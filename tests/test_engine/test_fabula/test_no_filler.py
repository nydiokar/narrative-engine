"""Tests for the No-Filler Enforcer."""

import pytest

from src.engine.fabula.no_filler import NoFillerEnforcer


class TestNoFillerEnforcer:
    def test_scene_passes_with_all_checks(self):
        scene = {
            "id": "scene1",
            "greimas_diagnostic": {
                "state_before": "peace",
                "action_occurs": "battle",
                "state_after": "war",
                "value_object_change": "transferred",
                "future_action_possible_or_blocked": "hero can now rally allies",
            },
            "modality_changes": [{"actant": "hero", "modality": "wanting"}],
        }
        result = NoFillerEnforcer.check_scene(scene)
        assert result.passed is True

    def test_scene_fails_no_change(self):
        scene = {
            "id": "scene2",
            "greimas_diagnostic": {
                "state_before": "waiting",
                "action_occurs": "",
                "state_after": "waiting",
                "value_object_change": "none",
                "future_action_possible_or_blocked": "",
            },
            "modality_changes": [],
        }
        result = NoFillerEnforcer.check_scene(scene)
        assert result.passed is False

    def test_scene_weak_justification(self):
        scene = {
            "id": "scene3",
            "greimas_diagnostic": {
                "state_before": "A",
                "action_occurs": "action",
                "state_after": "B",
                "value_object_change": "none",
                "future_action_possible_or_blocked": "",
            },
            "modality_changes": [],
        }
        result = NoFillerEnforcer.check_scene(scene)
        assert result.passed is False

    def test_character_without_actant_roles(self):
        char = {"id": "char1", "actant_roles": []}
        result = NoFillerEnforcer.check_character(char)
        assert result.passed is False

    def test_character_with_actant_roles(self):
        char = {"id": "char1", "actant_roles": ["subject"]}
        result = NoFillerEnforcer.check_character(char)
        assert result.passed is True

    def test_character_not_in_play(self):
        char = {"id": "char1", "actant_roles": ["helper"]}
        result = NoFillerEnforcer.check_character(char, actant_roles_in_play=["subject", "opponent"])
        assert result.passed is False

    def test_dialogue_conveys_information(self):
        dialogue = {"id": "d1", "conveys_information": True, "changes_configuration": False, "content": "The king is dead."}
        result = NoFillerEnforcer.check_dialogue(dialogue)
        assert result.passed is True

    def test_dialogue_filler(self):
        dialogue = {"id": "d2", "conveys_information": False, "changes_configuration": False, "content": "Nice weather."}
        result = NoFillerEnforcer.check_dialogue(dialogue)
        assert result.passed is False

    def test_event_with_predecessors_and_successors(self):
        event = {"id": "e1", "causal_predecessors": ["e0"], "causal_successors": ["e2"]}
        result = NoFillerEnforcer.check_event(event)
        assert result.passed is True

    def test_orphan_event(self):
        event = {"id": "e1", "causal_predecessors": [], "causal_successors": []}
        result = NoFillerEnforcer.check_event(event)
        assert result.passed is False

    def test_action_transforms_state(self):
        action = {"id": "hero", "state_before": "weak", "state_after": "strong", "operation": "training"}
        result = NoFillerEnforcer.check_action(action)
        assert result.passed is True

    def test_pseudo_action(self):
        action = {"id": "hero", "state_before": "standing", "state_after": "standing", "operation": "waiting"}
        result = NoFillerEnforcer.check_action(action)
        assert result.passed is False

    def test_batch_scenes(self):
        scenes = [
            {"id": "s1", "greimas_diagnostic": {"state_before": "A", "action_occurs": "B", "state_after": "C", "value_object_change": "transferred", "future_action_possible_or_blocked": "D"}, "modality_changes": [{}]},
            {"id": "s2", "greimas_diagnostic": {"state_before": "X", "action_occurs": "", "state_after": "X", "value_object_change": "none", "future_action_possible_or_blocked": ""}, "modality_changes": []},
        ]
        report = NoFillerEnforcer.check_scenes_batch(scenes)
        assert report.passed_count == 1
        assert report.total == 2
