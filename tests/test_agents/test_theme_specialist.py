"""Unit tests for Theme Specialist agent."""

from src.agents.base import AgentContext
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.store import reset_store
from src.agents.theme_specialist import ThemeSpecialist
from src.contracts.models import StoryContract


class TestThemeSpecialist:
    def setup_method(self):
        reset_store()
        reset_llm()

    def test_unknown_step_returns_error(self):
        agent = ThemeSpecialist()
        ctx = AgentContext(workflow_id="00", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_select_themes_creates_theme_contract(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "message": "Themes picked", '
            '"contract_data": {"primary_themes": [{"name": "justice", "question": "?"}]}}'
        )
        set_llm(mock)
        agent = ThemeSpecialist()
        agent.store.put("story", StoryContract(title="Test", premise="A test premise"))
        ctx = AgentContext(workflow_id="00", step_id="select_themes")
        result = agent.execute(ctx)
        assert result.success is True
        themes = agent.list_contracts("theme")
        assert len(themes) == 1
        assert themes[0].primary_themes[0]["name"] == "justice"

    def test_select_themes_fallback_when_no_contract_data(self):
        mock = MockLLMProvider()
        set_llm(mock)
        agent = ThemeSpecialist()
        agent.store.put("story", StoryContract(title="Test", premise="A test premise"))
        ctx = AgentContext(workflow_id="00", step_id="select_themes")
        result = agent.execute(ctx)
        assert result.success is True
        themes = agent.list_contracts("theme")
        assert len(themes) == 1
        assert "freedom" in themes[0].primary_themes[0]["name"]

    def test_select_themes_fallback_when_contract_data_invalid(self):
        mock = MockLLMProvider(fallback='not valid')
        set_llm(mock)
        agent = ThemeSpecialist()
        agent.store.put("story", StoryContract(title="Test", premise="A test premise"))
        ctx = AgentContext(workflow_id="00", step_id="select_themes")
        result = agent.execute(ctx)
        assert result.success is True
        themes = agent.list_contracts("theme")
        assert len(themes) == 1

    def test_select_genre_updates_story(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contract_data": '
            '{"primary_bisac": "FIC030000"}}'
        )
        set_llm(mock)
        agent = ThemeSpecialist()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="select_genre")
        result = agent.execute(ctx)
        assert result.success is True
        story = agent.list_contracts("story")[0]
        assert story.genre.primary_bisac == "FIC030000"

    def test_select_genre_default_when_no_data(self):
        mock = MockLLMProvider()
        set_llm(mock)
        agent = ThemeSpecialist()
        agent.store.put("story", StoryContract(title="T", premise="P"))
        ctx = AgentContext(workflow_id="00", step_id="select_genre")
        result = agent.execute(ctx)
        assert result.success is True
        story = agent.list_contracts("story")[0]
        assert story.genre.primary_bisac == "FIC009000"

    def test_validate_thematic_fit_success(self):
        mock = MockLLMProvider(fallback='{"success": true}')
        set_llm(mock)
        agent = ThemeSpecialist()
        agent.store.put("story", StoryContract(title="Test", premise="A test premise"))
        ctx = AgentContext(workflow_id="00", step_id="validate_thematic_fit")
        result = agent.execute(ctx)
        assert result.success is True

    def test_validate_thematic_fit_failure(self):
        mock = MockLLMProvider(fallback='{"success": false}')
        set_llm(mock)
        agent = ThemeSpecialist()
        agent.store.put("story", StoryContract(title="Test", premise="A test premise"))
        ctx = AgentContext(workflow_id="00", step_id="validate_thematic_fit")
        result = agent.execute(ctx)
        assert result.success is False
