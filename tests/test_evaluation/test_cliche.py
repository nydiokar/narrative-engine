"""Tests for the cliché detection engine."""

import pytest

from src.evaluation.cliche import ClicheDetector


class TestClicheDetector:
    def test_no_signals_detected(self):
        result = ClicheDetector.detect(explicit_signals=[])
        assert result.is_fresh is True
        assert result.cliche_score == 0

    def test_all_signals_detected(self):
        all_signals = [
            ("default_genre_setting", 3),
            ("default_protagonist_type", 3),
            ("default_motivation", 3),
            ("default_villain_motive", 3),
            ("default_ending", 3),
            ("no_cost_for_victory", 3),
            ("no_contradiction_inside_protagonist", 3),
            ("theme_stated_not_dramatized", 3),
            ("world_as_decoration", 3),
            ("villain_evil_without_value", 3),
            ("chosen_one_without_burden", 3),
            ("revenge_without_deformation", 3),
            ("romance_without_specific_incompatibility", 3),
            ("mentor_dies_only_to_motivate", 3),
        ]
        result = ClicheDetector.detect(explicit_signals=all_signals)
        assert result.is_fresh is False
        assert result.cliche_score > 3
        assert result.novelty_penalty > 0.5

    def test_some_signals(self):
        result = ClicheDetector.detect(explicit_signals=[("default_ending", 2)])
        assert result.is_fresh is True
        assert result.cliche_score == 2

    def test_list_signals(self):
        signals = ClicheDetector.list_signals()
        assert len(signals) == 14
        assert all("name" in s for s in signals)

    def test_list_freshness_generators(self):
        generators = ClicheDetector.list_freshness_generators()
        assert len(generators) == 14
        assert all("name" in g for g in generators)

    def test_novelty_penalty_range(self):
        result = ClicheDetector.detect(explicit_signals=[])
        assert 0.0 <= result.novelty_penalty <= 1.0
