"""Unit tests for World Researcher agent."""

from src.agents.base import AgentContext
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.store import reset_store
from src.agents.world_researcher import WorldResearcher


class TestWorldResearcher:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = WorldResearcher()
        ctx = AgentContext(workflow_id="00", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_set_world_axes_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = WorldResearcher()
        ctx = AgentContext(workflow_id="00", step_id="set_world_axes")
        result = agent.execute(ctx)
        assert result.success is True

    def test_assign_settings_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = WorldResearcher()
        ctx = AgentContext(workflow_id="03", step_id="assign_settings")
        result = agent.execute(ctx)
        assert result.success is True
