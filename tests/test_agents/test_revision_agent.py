"""Unit tests for the Revision Agent."""

from uuid import uuid4

from src.agents.base import AgentContext
from src.agents.llm import MockLLMProvider, set_llm, reset_llm
from src.agents.revision_agent import RevisionAgent
from src.agents.store import reset_store
from src.contracts.models import CritiqueContract, SceneContract, StoryContract


class TestRevisionAgent:
    def setup_method(self):
        reset_store()
        reset_llm()

    def _make_agent(self, fallback: str = '{"success": true, "contract_data": {"changes": []}}') -> RevisionAgent:
        mock = MockLLMProvider(fallback=fallback)
        set_llm(mock)
        return RevisionAgent()

    def _make_agent_with_changes(self) -> tuple[RevisionAgent, str]:
        scene = SceneContract(setting_location="test", chapter_id=uuid4())
        cid = str(scene.id)
        change_payload = (
            '{"success": true, "contract_data": {"changes": ['
            f'{{"type": "scene", "contract_id": "{cid}", '
            '"field": "content", "new_value": "Revised prose."}'
            "]}}"
        )
        agent = self._make_agent(fallback=change_payload)
        agent.store.put("scene", scene, agent="test")
        return agent, cid

    def _make_agent_with_failing_llm(self) -> RevisionAgent:
        return self._make_agent(
            fallback='{"success": false, "message": "LLM error", "errors": ["Failed"]}'
        )

    def test_unknown_step_returns_error(self):
        agent = self._make_agent()
        ctx = AgentContext(workflow_id="00", step_id="nonexistent")
        result = agent.execute(ctx)
        assert result.success is False
        assert any("Unknown step" in e for e in (result.errors or []))

    def test_apply_structural_changes_success(self):
        agent, cid = self._make_agent_with_changes()
        ctx = AgentContext(workflow_id="06", step_id="apply_structural_changes")
        result = agent.execute(ctx)
        assert result.success is True
        assert "modified" in result.message
        scene = agent.read_contract("scene", cid)
        assert scene is not None
        assert scene.content == "Revised prose."

    def test_apply_structural_changes_llm_failure(self):
        agent = self._make_agent_with_failing_llm()
        ctx = AgentContext(workflow_id="06", step_id="apply_structural_changes")
        result = agent.execute(ctx)
        assert result.success is False
        assert result.success is False

    def test_apply_line_changes_success(self):
        agent, cid = self._make_agent_with_changes()
        ctx = AgentContext(workflow_id="06", step_id="apply_line_changes")
        result = agent.execute(ctx)
        assert result.success is True
        scene = agent.read_contract("scene", cid)
        assert scene.content == "Revised prose."

    def test_apply_copy_changes_success(self):
        agent, cid = self._make_agent_with_changes()
        ctx = AgentContext(workflow_id="06", step_id="apply_copy_changes")
        result = agent.execute(ctx)
        assert result.success is True
        scene = agent.read_contract("scene", cid)
        assert scene.content == "Revised prose."

    def test_apply_script_changes_success(self):
        agent, cid = self._make_agent_with_changes()
        ctx = AgentContext(workflow_id="06", step_id="apply_script_changes")
        result = agent.execute(ctx)
        assert result.success is True

    def test_apply_revisions_passes(self):
        agent = self._make_agent()
        agent.store.put("story", StoryContract(title="Test", premise="Test"))
        agent.store.put(
            "critique",
            CritiqueContract(
                target_id=uuid4(), target_type="story_draft", verdict="pass"
            ),
        )
        ctx = AgentContext(workflow_id="07", step_id="apply_revisions")
        result = agent.execute(ctx)
        assert result.success is True

    def test_apply_revisions_fails_on_hard_gate_failure(self):
        agent = self._make_agent()
        agent.store.put("story", StoryContract(title="Test", premise="Test"))
        agent.store.put(
            "critique",
            CritiqueContract(
                target_id=uuid4(), target_type="story_draft", verdict="fail"
            ),
        )
        ctx = AgentContext(workflow_id="07", step_id="apply_revisions")
        result = agent.execute(ctx)
        assert result.success is False

    def test_apply_revisions_no_critique_proceeds(self):
        agent = self._make_agent()
        ctx = AgentContext(workflow_id="07", step_id="apply_revisions")
        result = agent.execute(ctx)
        assert result.success is True

    def test_apply_revisions_applies_changes(self):
        agent, cid = self._make_agent_with_changes()
        agent.store.put(
            "critique",
            CritiqueContract(
                target_id=uuid4(), target_type="story_draft", verdict="pass"
            ),
        )
        ctx = AgentContext(workflow_id="07", step_id="apply_revisions")
        result = agent.execute(ctx)
        assert result.success is True
        scene = agent.read_contract("scene", cid)
        assert scene.content == "Revised prose."
