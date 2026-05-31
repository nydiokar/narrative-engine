"""Integration tests for representative agents and the Director."""

from uuid import uuid4

import pytest

from src.agents.base import AgentContext
from src.agents.chapter_planner import ChapterPlanner
from src.agents.character_architect import CharacterArchitect
from src.agents.critic import Critic
from src.agents.director import WORKFLOW_REGISTRY, Director
from src.agents.outline_planner import OutlinePlanner
from src.agents.scene_writer import SceneWriter
from src.agents.showrunner import Showrunner
from src.agents.structuralist import Structuralist
from src.agents.theme_specialist import ThemeSpecialist
from src.agents.store import reset_store
from src.contracts.models import StoryContract


class TestIndividualAgents:
    def setup_method(self):
        reset_store()

    def test_showrunner_approve_brief(self):
        sr = Showrunner()
        store = sr.store
        store.put("story", StoryContract(title="Test", premise="A test premise"))
        ctx = AgentContext(workflow_id="00", step_id="approve_brief")
        result = sr.execute(ctx)
        assert result.success is True

    def test_showrunner_rejects_no_premise(self):
        sr = Showrunner()
        store = sr.store
        store.put("story", StoryContract(title="Empty", premise=""))
        ctx = AgentContext(workflow_id="00", step_id="approve_brief")
        result = sr.execute(ctx)
        assert result.success is False

    def test_outline_planner_creates_episodes(self):
        planner = OutlinePlanner()
        ctx = AgentContext(workflow_id="03", step_id="segment_fabula")
        result = planner.execute(ctx)
        assert result.success is True
        assert len(result.artifacts) == 3

    def test_chapter_planner_creates_chapters(self):
        planner = OutlinePlanner()
        planner.execute(AgentContext(workflow_id="03", step_id="segment_fabula"))

        cp = ChapterPlanner()
        ctx = AgentContext(workflow_id="03", step_id="divide_episodes")
        result = cp.execute(ctx)
        assert result.success is True
        chapters = cp.list_contracts("chapter")
        assert len(chapters) == 9  # 3 episodes * 3 chapters

    def test_scene_writer_renders_prose(self):
        planner = OutlinePlanner()
        planner.execute(AgentContext(workflow_id="03", step_id="segment_fabula"))
        cp = ChapterPlanner()
        cp.execute(AgentContext(workflow_id="03", step_id="divide_episodes"))

        sw = SceneWriter()
        ctx = AgentContext(workflow_id="04", step_id="render_prose")
        result = sw.execute(ctx)
        assert result.success is True
        scenes = sw.list_contracts("scene")
        assert len(scenes) == 18  # 9 chapters * 2 scenes

    def test_structuralist_checks_empty(self):
        s = Structuralist()
        ctx = AgentContext(workflow_id="02", step_id="check_constraints")
        result = s.execute(ctx)
        assert result.success is True  # empty = pass

    def test_theme_specialist_selects_themes(self):
        ts = ThemeSpecialist()
        ctx = AgentContext(workflow_id="00", step_id="select_themes")
        result = ts.execute(ctx)
        assert result.success is True
        themes = ts.list_contracts("theme")
        assert len(themes) == 1

    def test_critic_hard_gate_passes_empty(self):
        c = Critic()
        ctx = AgentContext(workflow_id="07", step_id="run_hard_gate")
        result = c.execute(ctx)
        assert result.success is True

    def test_unknown_step(self):
        sr = Showrunner()
        ctx = AgentContext(workflow_id="99", step_id="nonexistent")
        result = sr.execute(ctx)
        assert result.success is False


class TestDirector:
    def setup_method(self):
        reset_store()

    def _minimal_registry(self):
        from src.agents.base import BaseAgent
        store = __import__('src.agents.store', fromlist=['get_store']).get_store()
        common = {"store": store}

        class StubAgent(BaseAgent):
            def __init__(self, role, **kw):
                super().__init__(role=role, **kw)
            def execute(self, ctx):
                return type('Result', (), {'success': True, 'message': 'ok', 'artifacts': [], 'errors': []})()

        agents = {}
        for wid, steps in WORKFLOW_REGISTRY.items():
            for step in steps:
                if step.agent_role not in agents:
                    agents[step.agent_role] = StubAgent(role=step.agent_role, **common)
        return agents

    def test_workflow_registry_has_all_stages(self):
        assert "00-brief-and-taxonomy" in WORKFLOW_REGISTRY
        assert "01-seed-to-premise" in WORKFLOW_REGISTRY
        assert "02-premise-to-structure" in WORKFLOW_REGISTRY
        assert "03-structure-to-episodes" in WORKFLOW_REGISTRY
        assert "04-episodes-to-scenes" in WORKFLOW_REGISTRY
        assert "05-scenes-to-draft" in WORKFLOW_REGISTRY
        assert "06-editorial-passes" in WORKFLOW_REGISTRY
        assert "07-critique-and-revision" in WORKFLOW_REGISTRY

    def test_director_runs_workflow(self):
        agents = self._minimal_registry()
        director = Director(agents)
        results = director.run_workflow("00-brief-and-taxonomy")
        assert len(results) > 0
        assert all(r.success for r in results)

    def test_director_unknown_workflow(self):
        director = Director({})
        with pytest.raises(ValueError, match="Unknown workflow"):
            director.run_workflow("99-nonexistent")

    def test_director_full_pipeline(self):
        agents = self._minimal_registry()
        director = Director(agents)
        results = director.run_full_pipeline()
        assert len(results) == 8
        for wid, steps in results.items():
            assert all(r.success for r in steps)
