"""Unit tests for the Character Simulator agent."""

from src.agents.base import AgentContext
from src.agents.character_simulator import CharacterSimulator
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.store import reset_store


class TestCharacterSimulator:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = CharacterSimulator()
        ctx = AgentContext(workflow_id="04", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_enact_episode_success(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "message": "Characters simulated"}'
        )
        set_llm(mock)
        agent = CharacterSimulator()
        ctx = AgentContext(workflow_id="04", step_id="enact_episode")
        result = agent.execute(ctx)
        assert result.success is True
        assert "Characters simulated" in result.message

    def test_enact_episode_llm_failure(self):
        mock = MockLLMProvider(
            fallback='{"success": false, "errors": ["LLM failed"]}'
        )
        set_llm(mock)
        agent = CharacterSimulator()
        ctx = AgentContext(workflow_id="04", step_id="enact_episode")
        result = agent.execute(ctx)
        assert result.success is False

    def test_enact_episode_returns_character_artifacts(self):
        from src.contracts.models import CharacterContract
        mock = MockLLMProvider(
            fallback='{"success": true, "message": "Done"}'
        )
        set_llm(mock)
        agent = CharacterSimulator()
        c1 = CharacterContract(name="Alice")
        c2 = CharacterContract(name="Bob")
        agent.store.put("character", c1)
        agent.store.put("character", c2)
        ctx = AgentContext(workflow_id="04", step_id="enact_episode")
        result = agent.execute(ctx)
        assert result.success is True
        assert len(result.artifacts) == 2
