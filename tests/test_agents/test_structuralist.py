"""Unit tests for the Structuralist agent."""

from src.agents.base import AgentContext
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.structuralist import Structuralist
from src.agents.store import reset_store
from src.contracts.models import (
    StoryContract, CharacterContract, SceneContract, EpisodeContract,
    GreimasSceneDiagnostic,
)
from uuid import uuid4


class TestStructuralist:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = Structuralist()
        ctx = AgentContext(workflow_id="00", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_analyze_premise_updates_story(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "message": "Analyzed", '
            '"contract_data": {"subject_id": "abc", "object_of_value_description": "Freedom"}}'
        )
        set_llm(mock)
        agent = Structuralist()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="analyze_premise")
        result = agent.execute(ctx)
        assert result.success is True
        story = agent.list_contracts("story")[0]
        assert story.subject_id == "abc"
        assert story.object_of_value_description == "Freedom"

    def test_analyze_premise_llm_failure(self):
        mock = MockLLMProvider(
            fallback='{"success": false, "errors": ["LLM error"]}'
        )
        set_llm(mock)
        agent = Structuralist()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="analyze_premise")
        result = agent.execute(ctx)
        assert result.success is False

    def test_analyze_premise_no_contract_data(self):
        mock = MockLLMProvider(
            fallback='{"success": false}'
        )
        set_llm(mock)
        agent = Structuralist()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="analyze_premise")
        result = agent.execute(ctx)
        assert result.success is False

    def test_select_backbone_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = Structuralist()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="select_backbone")
        result = agent.execute(ctx)
        assert result.success is True

    def test_build_fabula_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = Structuralist()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("character", CharacterContract(name="A"))
        ctx = AgentContext(workflow_id="00", step_id="build_fabula")
        result = agent.execute(ctx)
        assert result.success is True

    def test_build_fabula_missing_characters(self):
        agent = Structuralist()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="build_fabula")
        result = agent.execute(ctx)
        assert result.success is False
        assert "Missing prerequisites" in result.errors[0]

    def test_check_constraints_missing_prerequisites(self):
        agent = Structuralist()
        ctx = AgentContext(workflow_id="00", step_id="check_constraints")
        result = agent.execute(ctx)
        assert result.success is False

    def test_check_constraints_passes(self):
        agent = Structuralist()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("character", CharacterContract(name="A"))
        from src.contracts.models import ConflictLoad, Intensity
        sc = SceneContract(setting_location="loc", chapter_id=uuid4())
        sc.greimas_diagnostic = GreimasSceneDiagnostic(
            state_before="peace", action_occurs="fights",
            state_after="wounded", value_object_change="transferred",
            future_action_possible_or_blocked="next",
        )
        sc.conflict_load = ConflictLoad(
            interpersonal=Intensity.HIGH, internal=Intensity.MEDIUM,
        )
        agent.store.put("scene", sc)
        agent.store.put("episode", EpisodeContract(title="E1"))
        ctx = AgentContext(workflow_id="00", step_id="check_constraints")
        result = agent.execute(ctx)
        assert result.success is True

    def test_check_constraints_no_scenes(self):
        agent = Structuralist()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("character", CharacterContract(name="A"))
        ctx = AgentContext(workflow_id="00", step_id="check_constraints")
        result = agent.execute(ctx)
        assert result.success is True
