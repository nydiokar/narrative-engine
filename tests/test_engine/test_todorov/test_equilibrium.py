"""Tests for Todorov equilibrium validation."""
from src.engine.todorov import (
    TodorovPhase,
    TodorovValidator,
)


class TestTodorovPhaseEnum:
    def test_five_phases(self):
        assert len(TodorovPhase) == 5

    def test_values(self):
        assert TodorovPhase.EQUILIBRIUM.value == "equilibrium"
        assert TodorovPhase.DISRUPTION.value == "disruption"
        assert TodorovPhase.RECOGNITION.value == "recognition"
        assert TodorovPhase.REPAIR.value == "repair"
        assert TodorovPhase.NEW_EQUILIBRIUM.value == "new_equilibrium"


class TestValidateSequence:
    def test_full_arc_passes(self):
        result = TodorovValidator.validate_sequence([
            TodorovPhase.EQUILIBRIUM,
            TodorovPhase.DISRUPTION,
            TodorovPhase.RECOGNITION,
            TodorovPhase.REPAIR,
            TodorovPhase.NEW_EQUILIBRIUM,
        ])
        assert result.passed is True
        assert result.violations == []

    def test_partial_forward_arc_passes(self):
        result = TodorovValidator.validate_sequence([
            TodorovPhase.EQUILIBRIUM,
            TodorovPhase.DISRUPTION,
        ])
        assert result.passed is True

    def test_single_phase_passes(self):
        result = TodorovValidator.validate_sequence([
            TodorovPhase.DISRUPTION,
        ])
        assert result.passed is True

    def test_empty_sequence_fails(self):
        result = TodorovValidator.validate_sequence([])
        assert result.passed is False
        assert any("Empty" in v for v in result.violations)

    def test_regression_fails(self):
        result = TodorovValidator.validate_sequence([
            TodorovPhase.DISRUPTION,
            TodorovPhase.EQUILIBRIUM,
        ])
        assert result.passed is False
        assert any("regression" in v for v in result.violations)

    def test_disruption_missing_when_later_phase_fails(self):
        result = TodorovValidator.validate_sequence([
            TodorovPhase.EQUILIBRIUM,
            TodorovPhase.REPAIR,
        ])
        assert result.passed is False
        assert any("disruption" in v for v in result.violations)

    def test_disruption_not_required_with_early_phases_only(self):
        result = TodorovValidator.validate_sequence([
            TodorovPhase.EQUILIBRIUM,
        ])
        assert result.passed is True

    def test_minimal_arc_passes(self):
        result = TodorovValidator.validate_sequence([
            TodorovPhase.EQUILIBRIUM,
            TodorovPhase.DISRUPTION,
            TodorovPhase.NEW_EQUILIBRIUM,
        ])
        assert result.passed is True


class TestValidateEpisodes:
    def test_valid_sequence(self):
        episodes = [
            {"title": "Ep1", "sequence_number": 0, "todorov_phase": "equilibrium"},
            {"title": "Ep2", "sequence_number": 1, "todorov_phase": "disruption"},
            {"title": "Ep3", "sequence_number": 2, "todorov_phase": "new_equilibrium"},
        ]
        result = TodorovValidator.validate_episodes(episodes)
        assert result.passed is True

    def test_regression_across_episodes(self):
        episodes = [
            {"title": "Ep1", "sequence_number": 0, "todorov_phase": "disruption"},
            {"title": "Ep2", "sequence_number": 1, "todorov_phase": "equilibrium"},
        ]
        result = TodorovValidator.validate_episodes(episodes)
        assert result.passed is False
        assert any("regression" in v for v in result.violations)

    def test_missing_disruption(self):
        episodes = [
            {"title": "Ep1", "sequence_number": 0, "todorov_phase": "equilibrium"},
            {"title": "Ep2", "sequence_number": 1, "todorov_phase": "repair"},
        ]
        result = TodorovValidator.validate_episodes(episodes)
        assert result.passed is False
        assert any("disruption" in v for v in result.violations)

    def test_no_todorov_phases_skips(self):
        episodes = [
            {"title": "Ep1", "sequence_number": 0, "canonical_phase": "manipulation"},
            {"title": "Ep2", "sequence_number": 1, "canonical_phase": "competence"},
        ]
        result = TodorovValidator.validate_episodes(episodes)
        assert result.passed is True
        assert result.violations == []

    def test_some_episodes_without_phase_skips_them(self):
        episodes = [
            {"title": "Ep1", "todorov_phase": "equilibrium"},
            {"title": "Ep2", "canonical_phase": "competence"},
            {"title": "Ep3", "todorov_phase": "disruption"},
        ]
        result = TodorovValidator.validate_episodes(episodes)
        assert result.passed is True

    def test_empty_episodes_passes(self):
        result = TodorovValidator.validate_episodes([])
        assert result.passed is True

    def test_unknown_phase_reported(self):
        episodes = [
            {"title": "Ep1", "todorov_phase": "bogus"},
        ]
        result = TodorovValidator.validate_episodes(episodes)
        assert result.passed is False
        assert any("Unknown" in v for v in result.violations)


class TestCoherenceEngineIntegration:
    def test_check_passes_with_valid_phases(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine
        episodes = [
            {"title": "Ep1", "todorov_phase": "equilibrium"},
            {"title": "Ep2", "todorov_phase": "disruption"},
            {"title": "Ep3", "todorov_phase": "new_equilibrium"},
        ]
        check = FabulaCoherenceEngine.check_todorov_equilibrium(episodes)
        assert check.passed is True
        assert check.name == "todorov_equilibrium"

    def test_check_skips_empty_episodes(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine
        check = FabulaCoherenceEngine.check_todorov_equilibrium([])
        assert check.passed is True

    def test_check_fails_on_regression(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine
        episodes = [
            {"title": "Ep1", "todorov_phase": "repair"},
            {"title": "Ep2", "todorov_phase": "equilibrium"},
        ]
        check = FabulaCoherenceEngine.check_todorov_equilibrium(episodes)
        assert check.passed is False
        assert any("regression" in v for v in check.violations)

    def test_run_all_checks_includes_todorov(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine
        report = FabulaCoherenceEngine.run_all_checks(
            events=[], scenes=[], episodes=[]
        )
        check_names = [c.name for c in report.checks]
        assert "todorov_equilibrium" in check_names
        assert len(report.checks) == 11
