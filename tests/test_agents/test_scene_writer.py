"""Unit tests for the Scene Writer agent."""

from src.agents.base import AgentContext
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.scene_writer import SceneWriter
from src.agents.store import reset_store
from src.contracts.models import StoryContract, ChapterContract, EpisodeContract


class TestSceneWriter:
    def setup_method(self):
        reset_store()
        reset_llm()

    def _seed_store(self, writer: SceneWriter) -> None:
        writer.store.put("story", StoryContract(title="Test", premise="Test"))
        ep = EpisodeContract(title="E1")
        writer.store.put("episode", ep)
        ch = ChapterContract(episode_id=ep.id, title="C1")
        writer.store.put("chapter", ch)

    def test_unknown_step_returns_error(self):
        writer = SceneWriter()
        ctx = AgentContext(workflow_id="00", step_id="nonexistent")
        result = writer.execute(ctx)
        assert result.success is False

    def test_render_scenes_llm_returns_data(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contracts_data": ['
            '{"setting_location": "The Forest", "sequence_number": 0, '
            '"chapter_id": "00000000-0000-0000-0000-000000000000", '
            '"greimas_diagnostic": {"state_before": "Lost", '
            '"action_occurs": "Searches", "state_after": "Found", '
            '"value_object_change": "discovered", '
            '"future_action_possible_or_blocked": "Next step"}}'
            "]}"
        )
        set_llm(mock)
        writer = SceneWriter()
        self._seed_store(writer)
        ctx = AgentContext(workflow_id="04", step_id="render_prose")
        result = writer.execute(ctx)
        assert result.success is True
        assert "1 scenes" in result.message
        scenes = writer.list_contracts("scene")
        assert len(scenes) == 1

    def test_render_scenes_uses_fallback_when_llm_returns_no_data(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contracts_data": []}'
        )
        set_llm(mock)
        writer = SceneWriter()
        self._seed_store(writer)
        ctx = AgentContext(workflow_id="04", step_id="render_prose")
        result = writer.execute(ctx)
        assert result.success is True
        scenes = writer.list_contracts("scene")
        # Fallback creates 3 scenes per chapter
        assert len(scenes) == 3

    def test_render_scenes_handles_llm_parse_failure(self):
        mock = MockLLMProvider(fallback="not valid json")
        set_llm(mock)
        writer = SceneWriter()
        self._seed_store(writer)
        ctx = AgentContext(workflow_id="04", step_id="render_prose")
        result = writer.execute(ctx)
        assert result.success is True
        scenes = writer.list_contracts("scene")
        assert len(scenes) == 3

    def test_render_scenes_normalizes_greimas_tracking(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "contracts_data": ['
            '{"setting_location": "Cave", "sequence_number": 0, '
            '"chapter_id": "00000000-0000-0000-0000-000000000000", '
            '"greimas_tracking": {"current_state": "Lost", '
            '"desired_transformation": "Explores", '
            '"resulting_state": "Found exit", '
            '"sanction_or_judgment": "Continues"}}'
            "]}"
        )
        set_llm(mock)
        writer = SceneWriter()
        self._seed_store(writer)
        ctx = AgentContext(workflow_id="04", step_id="render_prose")
        result = writer.execute(ctx)
        assert result.success is True
        scenes = writer.list_contracts("scene")
        assert len(scenes) == 1
        diag = scenes[0].greimas_diagnostic
        assert diag.state_before == "Lost"
        assert diag.state_after == "Found exit"

    def test_greimas_diagnostic_passes(self):
        writer = SceneWriter()
        from src.contracts.models import (
            SceneContract, GreimasSceneDiagnostic,
        )
        from uuid import uuid4
        sc = SceneContract(setting_location="test", chapter_id=uuid4())
        sc.greimas_diagnostic = GreimasSceneDiagnostic(
            state_before="peace",
            action_occurs="fights",
            state_after="wounded",
            value_object_change="transferred",
            future_action_possible_or_blocked="revenge now possible",
            diagnostic_pass=True,
        )
        writer.store.put("scene", sc)
        ctx = AgentContext(workflow_id="04", step_id="run_greimas_diagnostic")
        result = writer.execute(ctx)
        assert result.success is True
        assert "All scenes pass" in result.message

    def test_greimas_diagnostic_fails(self):
        writer = SceneWriter()
        from src.contracts.models import SceneContract
        from uuid import uuid4
        sc = SceneContract(setting_location="test", chapter_id=uuid4())
        writer.store.put("scene", sc)
        ctx = AgentContext(workflow_id="04", step_id="run_greimas_diagnostic")
        result = writer.execute(ctx)
        assert result.success is False

    def test_finalize_scenes_success(self):
        mock = MockLLMProvider(
            fallback='{"success": true, "message": "Finalized"}'
        )
        set_llm(mock)
        writer = SceneWriter()
        from src.contracts.models import SceneContract
        from uuid import uuid4
        writer.store.put("scene", SceneContract(setting_location="loc", chapter_id=uuid4()))
        ctx = AgentContext(workflow_id="05", step_id="finalize_prose")
        result = writer.execute(ctx)
        assert result.success is True

    def test_finalize_scenes_llm_failure(self):
        mock = MockLLMProvider(
            fallback='{"success": false, "message": "LLM error"}'
        )
        set_llm(mock)
        writer = SceneWriter()
        ctx = AgentContext(workflow_id="05", step_id="finalize_prose")
        result = writer.execute(ctx)
        assert result.success is False
