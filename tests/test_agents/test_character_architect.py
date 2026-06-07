"""Unit tests for Character Architect agent."""

from src.agents.base import AgentContext
from src.agents.character_architect import CharacterArchitect
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.store import reset_store
from src.contracts.models import StoryContract, CharacterContract, EpisodeContract


class TestCharacterArchitect:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = CharacterArchitect()
        ctx = AgentContext(workflow_id="00", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_prepare_layers(self):
        agent = CharacterArchitect()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="prepare_layers")
        result = agent.execute(ctx)
        assert result.success is True

    def test_draft_protagonists_creates_character(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contract_data": '
            '{"name": "Frodo", "description": "A hobbit", '
            '"actant_roles": ["subject"], '
            '"core_desires": ["peace"], "core_fears": ["darkness"]}}'
        )
        set_llm(mock)
        agent = CharacterArchitect()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="draft_protagonists")
        result = agent.execute(ctx)
        assert result.success is True
        chars = agent.list_contracts("character")
        assert len(chars) == 1
        assert chars[0].name == "Frodo"

    def test_draft_protagonists_fallback_when_no_name(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contract_data": {"name": ""}}'
        )
        set_llm(mock)
        agent = CharacterArchitect()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="draft_protagonists")
        result = agent.execute(ctx)
        assert result.success is True
        chars = agent.list_contracts("character")
        assert chars[0].name == "Protagonist"

    def test_draft_protagonists_fallback_when_no_contract_data(self):
        mock = MockLLMProvider()
        set_llm(mock)
        agent = CharacterArchitect()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="draft_protagonists")
        result = agent.execute(ctx)
        assert result.success is True
        chars = agent.list_contracts("character")
        assert chars[0].name == "Protagonist"

    def test_draft_protagonists_sets_subject_id_on_story(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contract_data": {"name": "Frodo"}}'
        )
        set_llm(mock)
        agent = CharacterArchitect()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="draft_protagonists")
        agent.execute(ctx)
        story = agent.list_contracts("story")[0]
        chars = agent.list_contracts("character")
        assert story.subject_id == str(chars[0].id)

    def test_refine_arcs_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = CharacterArchitect()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        agent.store.put("character", CharacterContract(name="A"))
        agent.store.put("episode", EpisodeContract(title="E1"))
        ctx = AgentContext(workflow_id="04", step_id="refine_arcs")
        result = agent.execute(ctx)
        assert result.success is True

    def test_refine_arcs_missing_prerequisites(self):
        agent = CharacterArchitect()
        ctx = AgentContext(workflow_id="04", step_id="refine_arcs")
        result = agent.execute(ctx)
        assert result.success is False
