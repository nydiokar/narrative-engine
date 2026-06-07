"""Tests for Propp function sequence validation."""
import pytest

from src.engine.propp import (
    PROPP_METADATA,
    ProppFunction,
    ProppSequenceValidator,
)


class TestProppFunctionEnum:
    def test_all_functions_have_metadata(self):
        for fn in ProppFunction:
            assert fn in PROPP_METADATA
            meta = PROPP_METADATA[fn]
            assert "symbol" in meta
            assert "sphere" in meta
            assert "description" in meta
            assert "core" in meta

    def test_core_subset(self):
        core = {fn for fn in ProppFunction if PROPP_METADATA[fn]["core"]}
        assert ProppFunction.VILLAINY in core
        assert ProppFunction.LACK in core
        assert ProppFunction.STRUGGLE in core
        assert ProppFunction.VICTORY in core
        assert ProppFunction.LIQUIDATION in core
        assert ProppFunction.ABSENTATION not in core


class TestParseFunctions:
    def test_parses_valid_names(self):
        parsed, errors = ProppSequenceValidator.parse_functions(
            ["villainy", "struggle", "victory", "liquidation"]
        )
        assert len(parsed) == 4
        assert errors == []
        assert parsed == [
            ProppFunction.VILLAINY,
            ProppFunction.STRUGGLE,
            ProppFunction.VICTORY,
            ProppFunction.LIQUIDATION,
        ]

    def test_normalizes_case_and_spaces(self):
        parsed, errors = ProppSequenceValidator.parse_functions(
            ["Villainy", "Struggle", "victory"]
        )
        assert len(parsed) == 3
        assert errors == []

    def test_unknown_function_produces_error(self):
        parsed, errors = ProppSequenceValidator.parse_functions(
            ["villainy", "bogus_function"]
        )
        assert len(parsed) == 1
        assert len(errors) == 1
        assert "Unknown" in errors[0]

    def test_empty_list(self):
        parsed, errors = ProppSequenceValidator.parse_functions([])
        assert parsed == []
        assert errors == []


class TestValidateSequence:
    def test_complete_canonical_sequence_passes(self):
        result = ProppSequenceValidator.validate_sequence(
            [
                ProppFunction.VILLAINY,
                ProppFunction.MEDIATION,
                ProppFunction.STRUGGLE,
                ProppFunction.VICTORY,
                ProppFunction.LIQUIDATION,
            ]
        )
        assert result.passed is True
        assert result.violations == []

    def test_minimal_valid_sequence_passes(self):
        result = ProppSequenceValidator.validate_sequence(
            [ProppFunction.VILLAINY, ProppFunction.STRUGGLE,
             ProppFunction.VICTORY, ProppFunction.LIQUIDATION]
        )
        assert result.passed is True

    def test_empty_sequence_fails(self):
        result = ProppSequenceValidator.validate_sequence([])
        assert result.passed is False
        assert any("Empty" in v for v in result.violations)

    def test_out_of_order_functions_fail(self):
        result = ProppSequenceValidator.validate_sequence(
            [
                ProppFunction.VILLAINY,
                ProppFunction.VICTORY,
                ProppFunction.STRUGGLE,
            ]
        )
        assert result.passed is False
        assert any("order violation" in v for v in result.violations)

    def test_missing_inciting_incident_fails(self):
        result = ProppSequenceValidator.validate_sequence(
            [ProppFunction.STRUGGLE, ProppFunction.VICTORY]
        )
        assert result.passed is False
        assert any("inciting" in v.lower() for v in result.violations)

    def test_struggle_without_victory_fails(self):
        result = ProppSequenceValidator.validate_sequence(
            [ProppFunction.VILLAINY, ProppFunction.STRUGGLE]
        )
        assert result.passed is False
        assert any(
            "struggle" in v and "victory" in v for v in result.violations
        )

    def test_full_episode_passes(self):
        result = ProppSequenceValidator.validate_sequence(
            [
                ProppFunction.ABSENTATION,
                ProppFunction.INTERDICTION,
                ProppFunction.VIOLATION,
                ProppFunction.RECONNAISSANCE,
                ProppFunction.DELIVERY,
                ProppFunction.TRICKERY,
                ProppFunction.COMPLICITY,
                ProppFunction.VILLAINY,
                ProppFunction.MEDIATION,
                ProppFunction.BEGINNING_COUNTERACTION,
                ProppFunction.DEPARTURE,
                ProppFunction.DONOR_TEST,
                ProppFunction.HERO_REACTION,
                ProppFunction.RECEIPT_MAGICAL_AGENT,
                ProppFunction.GUIDANCE,
                ProppFunction.STRUGGLE,
                ProppFunction.BRANDING,
                ProppFunction.VICTORY,
                ProppFunction.LIQUIDATION,
                ProppFunction.RETURN,
                ProppFunction.PURSUIT,
                ProppFunction.RESCUE,
                ProppFunction.UNRECOGNIZED_ARRIVAL,
                ProppFunction.UNFOUNDED_CLAIMS,
                ProppFunction.DIFFICULT_TASK,
                ProppFunction.SOLUTION,
                ProppFunction.RECOGNITION,
                ProppFunction.EXPOSURE,
                ProppFunction.TRANSFIGURATION,
                ProppFunction.PUNISHMENT,
                ProppFunction.WEDDING,
            ]
        )
        assert result.passed is True

    def test_missing_core_functions_reported(self):
        result = ProppSequenceValidator.validate_sequence(
            [ProppFunction.ABSENTATION]
        )
        assert result.passed is False
        assert ProppFunction.VILLAINY in result.missing_core


class TestValidateEpisodes:
    def test_single_episode(self):
        episodes = [
            {
                "title": "Ep1",
                "propp_functions": ["villainy", "struggle", "victory", "liquidation"],
            }
        ]
        results = ProppSequenceValidator.validate_episodes(episodes)
        assert len(results) == 1
        assert results[0].passed is True

    def test_multiple_episodes_tracks_titles(self):
        episodes = [
            {
                "title": "Ep1",
                "propp_functions": ["villainy", "struggle", "victory", "liquidation"],
            },
            {
                "title": "Ep2",
                "propp_functions": ["struggle"],
            },
        ]
        results = ProppSequenceValidator.validate_episodes(episodes)
        assert len(results) == 2
        assert results[0].passed is True
        assert results[1].passed is False

    def test_missing_propp_functions_field(self):
        episodes = [{"title": "Ep1"}]
        results = ProppSequenceValidator.validate_episodes(episodes)
        assert len(results) == 1
        assert results[0].sequence == []

    def test_empty_episodes_list(self):
        results = ProppSequenceValidator.validate_episodes([])
        assert results == []


class TestCoherenceEngineIntegration:
    """Test that the FabulaCoherenceEngine's propp_sequence check works."""

    def test_propp_check_passes(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine
        episodes = [
            {
                "title": "Ep1",
                "propp_functions": ["villainy", "struggle", "victory", "liquidation"],
            }
        ]
        check = FabulaCoherenceEngine.check_propp_sequence(episodes)
        assert check.passed is True
        assert check.name == "propp_sequence"

    def test_propp_check_skips_empty_list(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine
        check = FabulaCoherenceEngine.check_propp_sequence([])
        assert check.passed is True  # backward compat: no data = pass

    def test_propp_check_skips_no_functions(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine
        episodes = [{"title": "Ep1", "propp_functions": []}]
        check = FabulaCoherenceEngine.check_propp_sequence(episodes)
        assert check.passed is True

    def test_propp_check_fails_missing_core(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine
        episodes = [
            {
                "title": "Ep1",
                "propp_functions": ["absentation"],
            }
        ]
        check = FabulaCoherenceEngine.check_propp_sequence(episodes)
        assert check.passed is False
        assert any("inciting" in v.lower() for v in check.violations)

    def test_run_all_checks_includes_propp(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine
        report = FabulaCoherenceEngine.run_all_checks(
            events=[], scenes=[], episodes=[]
        )
        check_names = [c.name for c in report.checks]
        assert "propp_sequence" in check_names
        assert len(report.checks) == 10
