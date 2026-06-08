"""Unit tests for thin editorial agents."""

from uuid import uuid4

from src.agents.base import AgentContext
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.store import reset_store
from src.agents.developmental_editor import DevelopmentalEditor
from src.agents.line_editor import LineEditor
from src.agents.copy_editor import CopyEditor
from src.agents.proofreader import Proofreader
from src.contracts.models import ChapterContract, EpisodeContract, SceneContract, StoryContract


class TestDevelopmentalEditor:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = DevelopmentalEditor()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("episode", EpisodeContract(title="E1"))
        agent.store.put("chapter", ChapterContract(title="Ch1"))
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="06", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_evaluate_draft_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = DevelopmentalEditor()
        agent.store.put("story", StoryContract(title="The Saga", premise="P"))
        agent.store.put("episode", EpisodeContract(title="E1"))
        agent.store.put("chapter", ChapterContract(title="Ch1"))
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="06", step_id="evaluate_draft")
        result = agent.execute(ctx)
        assert result.success is True
        assert "Saga" in result.message

    def test_evaluate_draft_without_story(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = DevelopmentalEditor()
        agent.store.put("episode", EpisodeContract(title="E1"))
        agent.store.put("chapter", ChapterContract(title="Ch1"))
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="06", step_id="evaluate_draft")
        result = agent.execute(ctx)
        assert result.success is True
        assert "edit complete" in result.message

    def test_evaluate_draft_llm_failure(self):
        mock = MockLLMProvider(fallback='{"success": false}')
        set_llm(mock)
        agent = DevelopmentalEditor()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("episode", EpisodeContract(title="E1"))
        agent.store.put("chapter", ChapterContract(title="Ch1"))
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="06", step_id="evaluate_draft")
        result = agent.execute(ctx)
        assert result.success is False


class TestLineEditor:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = LineEditor()
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="06", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_refine_prose_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = LineEditor()
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="06", step_id="refine_prose")
        result = agent.execute(ctx)
        assert result.success is True

    def test_refine_prose_llm_failure(self):
        mock = MockLLMProvider(fallback='{"success": false}')
        set_llm(mock)
        agent = LineEditor()
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="06", step_id="refine_prose")
        result = agent.execute(ctx)
        assert result.success is False


class TestCopyEditor:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = CopyEditor()
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="06", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_check_consistency_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = CopyEditor()
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="06", step_id="check_consistency")
        result = agent.execute(ctx)
        assert result.success is True


class TestProofreader:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = Proofreader()
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        agent.store.put("chapter", ChapterContract(title="Ch1"))
        ctx = AgentContext(workflow_id="06", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_final_check_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = Proofreader()
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        agent.store.put("chapter", ChapterContract(title="Ch1"))
        ctx = AgentContext(workflow_id="06", step_id="final_check")
        result = agent.execute(ctx)
        assert result.success is True
