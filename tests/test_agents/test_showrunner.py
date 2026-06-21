"""Unit tests for the Showrunner agent."""

from src.agents.base import AgentContext
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.showrunner import Showrunner
from src.agents.store import reset_store
from src.contracts.models import (
    StoryContract, CharacterContract, EpisodeContract, ChapterContract,
    SceneContract, CritiqueContract, ThemeContract, DiscourseContract,
)
from uuid import uuid4


class TestShowrunner:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = Showrunner()
        ctx = AgentContext(workflow_id="00", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_review_brief_success(self):
        mock = MockLLMProvider(fallback='{"success": true, "message": "Reviewed"}')
        set_llm(mock)
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="review_brief")
        result = agent.execute(ctx)
        assert result.success is True

    def test_approve_brief_fails_without_premise(self):
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise=""))
        ctx = AgentContext(workflow_id="00", step_id="approve_brief")
        result = agent.execute(ctx)
        assert result.success is False
        assert "no premise" in result.errors[0].lower()

    def test_approve_brief_success(self):
        mock = MockLLMProvider(fallback='{"success": true, "message": "Approved"}')
        set_llm(mock)
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="approve_brief")
        result = agent.execute(ctx)
        assert result.success is True

    def test_approve_premise_success(self):
        mock = MockLLMProvider(fallback='{"success": true, "message": "Approved"}')
        set_llm(mock)
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("character", CharacterContract(name="A"))
        ctx = AgentContext(workflow_id="01", step_id="approve_premise")
        result = agent.execute(ctx)
        assert result.success is True

    def test_approve_premise_missing_characters(self):
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="01", step_id="approve_premise")
        result = agent.execute(ctx)
        assert result.success is False

    def test_approve_structure_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("character", CharacterContract(name="A"))
        agent.store.put("theme", ThemeContract())
        ctx = AgentContext(workflow_id="02", step_id="approve_structure")
        result = agent.execute(ctx)
        assert result.success is True

    def test_approve_episodes_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = Showrunner()
        phases = ["manipulation", "competence", "performance", "sanction"]
        eps = [EpisodeContract(title=f"E{i+1}-{p}", canonical_phase=p) for i, p in enumerate(phases)]
        agent.store.put("story", StoryContract(title="T", premise="P"))
        for ep in eps:
            agent.store.put("episode", ep)
            agent.store.put("chapter", ChapterContract(episode_id=ep.id, title=f"C-{ep.title}"))
        ctx = AgentContext(workflow_id="04", step_id="approve_episodes")
        result = agent.execute(ctx)
        assert result.success is True

    def test_approve_episodes_missing_phases(self):
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("episode", EpisodeContract(title="E1"))
        ctx = AgentContext(workflow_id="04", step_id="approve_episodes")
        result = agent.execute(ctx)
        assert result.success is False

    def test_assemble_draft_success(self):
        mock = MockLLMProvider(fallback='{"success": true, "message": "Assembled"}')
        set_llm(mock)
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="05", step_id="assemble_draft")
        result = agent.execute(ctx)
        assert result.success is True

    def test_assemble_script_counts_scenes(self):
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        agent.store.put("scene", SceneContract(setting_location="loc2", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="05", step_id="assemble_script")
        result = agent.execute(ctx)
        assert result.success is True
        assert "2 scenes" in result.message

    def test_assemble_screenplay_success(self):
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="05", step_id="assemble_screenplay")
        result = agent.execute(ctx)
        assert result.success is True

    def test_assemble_teleplay_success(self):
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="05", step_id="assemble_teleplay")
        result = agent.execute(ctx)
        assert result.success is True

    def test_approve_final_hard_gate_fail_rejects(self):
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("critique", CritiqueContract(
            reviewer="critic", verdict="fail", target_type="story_draft", summary="Fail"
        ))
        ctx = AgentContext(workflow_id="06", step_id="approve_final")
        result = agent.execute(ctx)
        assert result.success is False
        assert "rejected" in result.errors[0].lower()

    def test_approve_final_all_contracts_present(self):
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("theme", ThemeContract())
        agent.store.put("character", CharacterContract(name="A"))
        agent.store.put("episode", EpisodeContract(title="E1"))
        agent.store.put("chapter", ChapterContract(title="C1"))
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        agent.store.put("critique", CritiqueContract(
            reviewer="critic", verdict="pass", target_type="story_draft", summary="Pass"
        ))
        agent.store.put("discourse", DiscourseContract())
        ctx = AgentContext(workflow_id="06", step_id="approve_final")
        result = agent.execute(ctx)
        assert result.success is True

    def test_approve_final_missing_contracts(self):
        agent = Showrunner()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="06", step_id="approve_final")
        result = agent.execute(ctx)
        assert result.success is False
        assert "Missing contracts" in result.errors[0]
