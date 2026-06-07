"""Unit tests for Outline Planner and Chapter Planner agents."""

from src.agents.base import AgentContext
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.store import reset_store
from src.agents.outline_planner import OutlinePlanner
from src.agents.chapter_planner import ChapterPlanner
from src.contracts.models import StoryContract, CharacterContract, EpisodeContract


class TestOutlinePlanner:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = OutlinePlanner()
        ctx = AgentContext(workflow_id="00", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_segment_fabula_llm_returns_data(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contracts_data": ['
            '{"title": "The Beginning", "summary": "Start", '
            '"sequence_number": 0, "canonical_phase": "manipulation"}]}'
        )
        set_llm(mock)
        agent = OutlinePlanner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("character", CharacterContract(name="A"))
        ctx = AgentContext(workflow_id="00", step_id="segment_fabula")
        result = agent.execute(ctx)
        assert result.success is True
        assert "1 episodes" in result.message
        episodes = agent.list_contracts("episode")
        assert len(episodes) == 1

    def test_segment_fabula_uses_fallback_when_no_data(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contracts_data": []}'
        )
        set_llm(mock)
        agent = OutlinePlanner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("character", CharacterContract(name="A"))
        ctx = AgentContext(workflow_id="00", step_id="segment_fabula")
        result = agent.execute(ctx)
        assert result.success is True
        episodes = agent.list_contracts("episode")
        assert len(episodes) == 4

    def test_segment_fabula_missing_prerequisites(self):
        agent = OutlinePlanner()
        ctx = AgentContext(workflow_id="00", step_id="segment_fabula")
        result = agent.execute(ctx)
        assert result.success is False

    def test_segment_fabula_normalizes_phase(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contracts_data": ['
            '{"title": "E1", "summary": "S", '
            '"canonical_phase": "MANIPULATION"}]}'
        )
        set_llm(mock)
        agent = OutlinePlanner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("character", CharacterContract(name="A"))
        ctx = AgentContext(workflow_id="00", step_id="segment_fabula")
        agent.execute(ctx)
        ep = agent.list_contracts("episode")[0]
        assert ep.canonical_phase == "manipulation"


class TestChapterPlanner:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = ChapterPlanner()
        ctx = AgentContext(workflow_id="00", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_divide_episodes_with_llm_data(self):
        ep = EpisodeContract(title="E1")
        mock = MockLLMProvider(
            fallback='{"success": true, "contracts_data": ['
            '{"episode_id": "' + str(ep.id) + '", '
            '"sequence_number": 0, "title": "Ch1"}]}'
        )
        set_llm(mock)
        agent = ChapterPlanner()
        agent.store.put("episode", ep)
        ctx = AgentContext(workflow_id="04", step_id="divide_episodes")
        result = agent.execute(ctx)
        assert result.success is True
        assert "1 chapters" in result.message

    def test_divide_episodes_uses_fallback_when_no_data(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contracts_data": []}'
        )
        set_llm(mock)
        agent = ChapterPlanner()
        agent.store.put("episode", EpisodeContract(title="E1"))
        ctx = AgentContext(workflow_id="04", step_id="divide_episodes")
        result = agent.execute(ctx)
        assert result.success is True
        chapters = agent.list_contracts("chapter")
        # Fallback creates 3 chapters per episode
        assert len(chapters) == 3

    def test_divide_episodes_multiple_episodes(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = ChapterPlanner()
        agent.store.put("episode", EpisodeContract(title="E1"))
        agent.store.put("episode", EpisodeContract(title="E2"))
        ctx = AgentContext(workflow_id="04", step_id="divide_episodes")
        result = agent.execute(ctx)
        assert result.success is True
        chapters = agent.list_contracts("chapter")
        # 2 episodes x 3 chapters each
        assert len(chapters) == 6
