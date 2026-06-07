"""Unit tests for Script Editor agent."""

from src.agents.base import AgentContext
from src.agents.script_editor import ScriptEditor
from src.agents.store import reset_store
from src.contracts.models import SceneContract, GreimasSceneDiagnostic
from uuid import uuid4


class TestScriptEditor:
    def setup_method(self):
        reset_store()

    def test_unknown_step_returns_error(self):
        agent = ScriptEditor()
        ctx = AgentContext(workflow_id="06", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False

    def test_refine_script_success(self):
        agent = ScriptEditor()
        sc = SceneContract(setting_location="loc", chapter_id=uuid4(), content="Some text")
        sc.greimas_diagnostic = GreimasSceneDiagnostic(
            state_before="peace", action_occurs="fights",
            state_after="wounded", value_object_change="transferred",
            future_action_possible_or_blocked="next",
        )
        agent.store.put("scene", sc)
        ctx = AgentContext(workflow_id="06", step_id="refine_script")
        result = agent.execute(ctx)
        assert result.success is True

    def test_refine_script_missing_prerequisites(self):
        agent = ScriptEditor()
        ctx = AgentContext(workflow_id="06", step_id="refine_script")
        result = agent.execute(ctx)
        assert result.success is False
        assert "Missing prerequisites" in result.errors[0]

    def test_refine_script_flags_missing_fields(self):
        agent = ScriptEditor()
        sc = SceneContract(setting_location="loc", chapter_id=uuid4())
        agent.store.put("scene", sc)
        ctx = AgentContext(workflow_id="06", step_id="refine_script")
        result = agent.execute(ctx)
        assert result.success is True
        assert "issue(s)" in result.message

    def test_refine_script_missing_prerequisites(self):
        agent = ScriptEditor()
        ctx = AgentContext(workflow_id="06", step_id="refine_script")
        result = agent.execute(ctx)
        assert result.success is False
