"""Unit tests for the Dialogue Specialist agent."""

from uuid import uuid4

from src.agents.base import AgentContext
from src.agents.dialogue_specialist import DialogueSpecialist
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.store import reset_store
from src.contracts.models import CharacterContract, SceneContract


class TestDialogueSpecialist:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = DialogueSpecialist()
        ctx = AgentContext(workflow_id="04", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_plan_speech_acts_success(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "message": "Speech acts planned"}'
        )
        set_llm(mock)
        agent = DialogueSpecialist()
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        agent.store.put("character", CharacterContract(name="Alice"))
        ctx = AgentContext(workflow_id="04", step_id="plan_speech_acts")
        result = agent.execute(ctx)
        assert result.success is True
        assert "Speech acts planned" in result.message

    def test_plan_speech_acts_llm_failure(self):
        mock = MockLLMProvider(
            fallback='{"success": false, "errors": ["LLM failed"]}'
        )
        set_llm(mock)
        agent = DialogueSpecialist()
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        agent.store.put("character", CharacterContract(name="Alice"))
        ctx = AgentContext(workflow_id="04", step_id="plan_speech_acts")
        result = agent.execute(ctx)
        assert result.success is False

    def test_plan_speech_acts_counts_scenes(self):
        mock = MockLLMProvider(
            fallback='{"success": true}'
        )
        set_llm(mock)
        agent = DialogueSpecialist()
        agent.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        agent.store.put("scene", SceneContract(setting_location="loc2", chapter_id=uuid4()))
        agent.store.put("character", CharacterContract(name="Alice"))
        ctx = AgentContext(workflow_id="04", step_id="plan_speech_acts")
        result = agent.execute(ctx)
        assert result.success is True
        assert "2 scenes" in result.message
