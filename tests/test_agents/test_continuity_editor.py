"""Unit tests for the Continuity Editor agent."""

from uuid import uuid4

from src.agents.base import AgentContext
from src.agents.continuity_editor import ContinuityEditor
from src.agents.store import reset_store
from src.contracts.models import (
    ConflictLoad,
    EpisodeContract,
    GreimasSceneDiagnostic,
    Intensity,
    SceneContract,
    StoryContract,
)


class TestContinuityEditor:
    def setup_method(self):
        reset_store()

    def _make_scene(self, value_change: str, conflict: Intensity | None = None) -> SceneContract:
        sc = SceneContract(setting_location="test", chapter_id=uuid4())
        sc.greimas_diagnostic = GreimasSceneDiagnostic(
            state_before="peace",
            action_occurs="fights",
            state_after="wounded",
            value_object_change=value_change,
            diagnostic_pass=True,
        )
        if conflict:
            sc.conflict_load = ConflictLoad(interpersonal=conflict)
        return sc

    def test_check_consistency_passes(self):
        editor = ContinuityEditor()
        store = editor.store
        store.put("story", StoryContract(title="Test", premise="Test"))
        store.put("episode", EpisodeContract(title="E1"))
        sc = self._make_scene("acquired", Intensity.HIGH)
        store.put("scene", sc)
        ctx = AgentContext(workflow_id="04", step_id="check_consistency")
        result = editor.execute(ctx)
        assert result.success is True
        assert result.message == "Continuity check passed"

    def test_check_consistency_fails_on_bad_scenes(self):
        editor = ContinuityEditor()
        store = editor.store
        store.put("story", StoryContract(title="Test", premise="Test"))
        store.put("episode", EpisodeContract(title="E1"))
        sc = self._make_scene("none", None)
        store.put("scene", sc)
        ctx = AgentContext(workflow_id="04", step_id="check_consistency")
        result = editor.execute(ctx)
        assert result.success is False

    def test_unknown_step_returns_error(self):
        editor = ContinuityEditor()
        ctx = AgentContext(workflow_id="00", step_id="nonexistent")
        result = editor.execute(ctx)
        assert result.success is False
        assert any("Unknown step" in e for e in (result.errors or []))

    def test_final_check_passes(self):
        editor = ContinuityEditor()
        ctx = AgentContext(workflow_id="05", step_id="final_check")
        result = editor.execute(ctx)
        assert result.success is True
        assert result.message == "Final continuity check passed"
