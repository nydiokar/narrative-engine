"""Unit tests for the Critic agent (Hard Gate, Soft Gate, Greimas diagnostics)."""

from unittest.mock import patch

from src.agents.base import AgentContext
from src.agents.critic import Critic
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.store import reset_store
from src.contracts.models import (
    StoryContract, EpisodeContract, CharacterContract, SceneContract,
    GreimasSceneDiagnostic, ConflictLoad, Intensity,
)
from uuid import uuid4


class TestCritic:
    def setup_method(self):
        reset_store()
        reset_llm()

    def _seed_hard_gate(self, critic: Critic) -> None:
        sid = "00000000-0000-0000-0000-000000000001"
        critic.store.put("story", StoryContract(id=sid, title="T", premise="P"))
        critic.store.put("episode", EpisodeContract(title="E1"))
        critic.store.put("character", CharacterContract(name="Alice"))
        sc = SceneContract(setting_location="loc", chapter_id=uuid4())
        sc.greimas_diagnostic = GreimasSceneDiagnostic(
            state_before="peace",
            action_occurs="fights",
            state_after="wounded",
            value_object_change="transferred",
            future_action_possible_or_blocked="next",
            diagnostic_pass=True,
        )
        sc.conflict_load = ConflictLoad(
            interpersonal=Intensity.HIGH, internal=Intensity.MEDIUM,
        )
        critic.store.put("scene", sc)

    def test_unknown_step_returns_error(self):
        agent = Critic()
        ctx = AgentContext(workflow_id="00", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_hard_gate_passes(self):
        agent = Critic()
        self._seed_hard_gate(agent)
        ctx = AgentContext(workflow_id="05", step_id="run_hard_gate")
        result = agent.execute(ctx)
        assert result.success is True
        assert "PASS" in result.message

    def test_hard_gate_fails_with_no_data(self):
        agent = Critic()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("episode", EpisodeContract(title="E1"))
        agent.store.put("character", CharacterContract(name="Alice"))
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="05", step_id="run_hard_gate")
        result = agent.execute(ctx)
        assert result.success is False
        assert "FAIL" in result.message

    def test_hard_gate_missing_prerequisites(self):
        agent = Critic()
        ctx = AgentContext(workflow_id="05", step_id="run_hard_gate")
        result = agent.execute(ctx)
        assert result.success is False
        assert "Missing prerequisites" in result.errors[0]

    def test_soft_gate_with_llm_scores(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contract_data": {'
            '"dimension_scores": {"genre_fit": 8, "thematic_clarity": 7, '
            '"conflict_density": 6, "relationship_tension": 5, '
            '"scene_level_purpose": 7, "suspense_curiosity_surprise": 6, '
            '"emotional_transport": 6, "novelty": 7, '
            '"prose_distinctiveness": 5}}}'
        )
        set_llm(mock)
        agent = Critic()
        self._seed_hard_gate(agent)
        ctx = AgentContext(workflow_id="05", step_id="run_soft_gate")
        result = agent.execute(ctx)
        assert result.success is True
        assert "PASS" in result.message

    def test_soft_gate_without_llm_scores_uses_fallback(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contract_data": {}}'
        )
        set_llm(mock)
        agent = Critic()
        self._seed_hard_gate(agent)
        ctx = AgentContext(workflow_id="05", step_id="run_soft_gate")
        result = agent.execute(ctx)
        assert result.success is True
        assert "PASS" in result.message

    def test_soft_gate_with_llm_failure(self):
        mock = MockLLMProvider(fallback='{"success": false}')
        set_llm(mock)
        agent = Critic()
        self._seed_hard_gate(agent)
        ctx = AgentContext(workflow_id="05", step_id="run_soft_gate")
        result = agent.execute(ctx)
        assert result.success is True

    def test_greimas_diagnostics_with_cliches(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contract_data": {'
            '"cliche_signals": [{"name": "chosen_one", "severity": 2}]}}'
        )
        set_llm(mock)
        agent = Critic()
        self._seed_hard_gate(agent)
        ctx = AgentContext(workflow_id="05", step_id="run_greimas_diagnostics")
        result = agent.execute(ctx)
        assert result.success is True
        assert "Cliché score" in result.message

    def test_greimas_diagnostics_without_cliches(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contract_data": {}}'
        )
        set_llm(mock)
        agent = Critic()
        self._seed_hard_gate(agent)
        ctx = AgentContext(workflow_id="05", step_id="run_greimas_diagnostics")
        result = agent.execute(ctx)
        assert result.success is True

    def test_greimas_diagnostics_llm_failure(self):
        mock = MockLLMProvider(fallback='{"success": false}')
        set_llm(mock)
        agent = Critic()
        self._seed_hard_gate(agent)
        ctx = AgentContext(workflow_id="05", step_id="run_greimas_diagnostics")
        result = agent.execute(ctx)
        assert result.success is True
