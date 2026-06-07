"""Integration tests for representative agents and the Director."""

from uuid import uuid4

import pytest

from src.agents.base import AgentContext
from src.agents.chapter_planner import ChapterPlanner
from src.agents.character_architect import CharacterArchitect
from src.agents.critic import Critic
from src.agents.director import Director, get_registry
from src.contracts.models import Medium
from src.agents.outline_planner import OutlinePlanner
from src.agents.scene_writer import SceneWriter
from src.agents.showrunner import Showrunner
from src.agents.structuralist import Structuralist
from src.agents.theme_specialist import ThemeSpecialist
from src.agents.store import ContractStore, reset_store
from src.contracts.models import CharacterContract, ConflictLoad, EpisodeContract, Intensity, SceneContract, StoryContract
from src.engine.config import get_settings


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
        store = planner.store
        store.put("story", StoryContract(title="Test", premise="A test premise"))
        store.put("character", CharacterContract(name="Hero", description="Main character"))
        ctx = AgentContext(workflow_id="03", step_id="segment_fabula")
        result = planner.execute(ctx)
        assert result.success is True
        assert len(result.artifacts) == 3

    def test_chapter_planner_creates_chapters(self):
        store = ContractStore()
        planner = OutlinePlanner(store=store)
        store.put("story", StoryContract(title="Test", premise="A test premise"))
        store.put("character", CharacterContract(name="Hero", description="Main character"))
        planner.execute(AgentContext(workflow_id="03", step_id="segment_fabula"))

        cp = ChapterPlanner(store=store)
        ctx = AgentContext(workflow_id="03", step_id="divide_episodes")
        result = cp.execute(ctx)
        assert result.success is True
        chapters = cp.list_contracts("chapter")
        assert len(chapters) == 9  # 3 episodes * 3 chapters

    def test_scene_writer_renders_prose(self):
        sw = SceneWriter()
        store = sw.store
        store.put("story", StoryContract(title="Test", premise="A test premise"))
        store.put("character", CharacterContract(name="Hero", description="Main character"))
        planner = OutlinePlanner(store=store)
        planner.execute(AgentContext(workflow_id="03", step_id="segment_fabula"))
        cp = ChapterPlanner(store=store)
        cp.execute(AgentContext(workflow_id="03", step_id="divide_episodes"))

        ctx = AgentContext(workflow_id="04", step_id="render_prose")
        result = sw.execute(ctx)
        assert result.success is True
        scenes = sw.list_contracts("scene")
        assert len(scenes) == 18  # 9 chapters * 2 scenes

    def test_structuralist_checks_empty(self):
        s = Structuralist()
        store = s.store
        store.put("story", StoryContract(title="Test", premise="A test premise"))
        store.put("character", CharacterContract(name="Hero", description="Main character"))
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
        store = c.store
        store.put("story", StoryContract(title="Test", premise="A test premise"))
        store.put("character", CharacterContract(name="Hero"))
        store.put("episode", EpisodeContract(title="E1"))
        sc = SceneContract(setting_location="test", chapter_id=uuid4())
        sc.greimas_diagnostic.value_object_change = "transferred"
        sc.conflict_load = ConflictLoad(
            interpersonal=Intensity.MEDIUM,
        )
        store.put("scene", sc)
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

        registry = get_registry(Medium.BOOK)
        agents = {}
        for wid, steps in registry.items():
            for step in steps:
                if step.agent_role not in agents:
                    agents[step.agent_role] = StubAgent(role=step.agent_role, **common)
        return agents

    def test_workflow_registry_has_all_stages(self):
        registry = get_registry(Medium.BOOK)
        assert "00-brief-and-taxonomy" in registry
        assert "01-seed-to-premise" in registry
        assert "02-premise-to-structure" in registry
        assert "03-structure-to-episodes" in registry
        assert "04-episodes-to-scenes" in registry
        assert "05-scenes-to-draft" in registry
        assert "06-editorial-passes" in registry
        assert "07-critique-and-revision" in registry

    def test_director_runs_workflow(self):
        agents = self._minimal_registry()
        director = Director(agents)
        results = director.run_workflow("00-brief-and-taxonomy")
        assert len(results) > 0
        assert all(r.success for r in results)

    def test_medium_registries_differ_at_rendering_layer(self):
        book = get_registry(Medium.BOOK)
        animation = get_registry(Medium.ANIMATION)
        movie = get_registry(Medium.MOVIE)

        # Structure workflows are identical
        assert book["00-brief-and-taxonomy"] == animation["00-brief-and-taxonomy"]
        assert book["01-seed-to-premise"] == animation["01-seed-to-premise"]
        assert book["02-premise-to-structure"] == animation["02-premise-to-structure"]
        assert book["03-structure-to-episodes"] == animation["03-structure-to-episodes"]
        assert book["07-critique-and-revision"] == animation["07-critique-and-revision"]

        # Rendering workflows differ
        assert book["04-episodes-to-scenes"] != animation["04-episodes-to-scenes"]
        assert book["05-scenes-to-draft"] != animation["05-scenes-to-draft"]
        assert book["06-editorial-passes"] != animation["06-editorial-passes"]

        # Animation and movie share scene structure but differ in step names
        animation_scene_steps = {s.step_id for s in animation["04-episodes-to-scenes"]}
        movie_scene_steps = {s.step_id for s in movie["04-episodes-to-scenes"]}
        assert animation_scene_steps != movie_scene_steps

    def test_director_medium_routes_correct_registry(self):
        book_director = Director({}, medium=Medium.BOOK)
        anim_director = Director({}, medium=Medium.ANIMATION)
        assert "06-editorial-passes" in book_director.registry
        assert "06-editorial-passes" in anim_director.registry
        assert book_director.registry["06-editorial-passes"] != anim_director.registry["06-editorial-passes"]

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
