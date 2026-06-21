"""Integration tests for the full 8-workflow pipeline end to end."""

import pytest

from src.agents.director import get_registry
from src.agents.llm import reset_llm, set_llm, MockLLMProvider
from src.agents.store import get_store, reset_store
from src.contracts.models import Medium, StoryContract
from src.pipeline.orchestrator import PipelineOrchestrator, default_agent_registry


class TestFullPipeline:
    def setup_method(self):
        reset_store()
        reset_llm()  # uses default MockLLMProvider with valid JSON fallback

    def _seed_story(self, title: str = "The Crystal Key", premise: str = "A disgraced mage seeks redemption by unlocking a sealed archive that holds the key to stopping an encroaching blight.") -> str:
        store = get_store()
        story = StoryContract(title=title, premise=premise)
        return store.put("story", story)

    # ── Happy path: full pipeline ─────────────────────────────────────

    def test_full_pipeline_runs_all_workflows(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        results = orchestrator.run()

        assert len(results) == 8
        for wid, steps in results.items():
            assert all(r.success for r in steps), f"Workflow {wid} failed: {[r.message for r in steps if not r.success]}"

    def test_full_pipeline_accumulates_contracts(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        orchestrator.run()

        store = get_store()
        all_items = store.list_all()
        assert "story" in all_items, "No story contract"
        assert "theme" in all_items, "No theme contract"
        assert "character" in all_items, "No character contract"
        assert "episode" in all_items, "No episode contract"
        assert "chapter" in all_items, "No chapter contract"
        assert "scene" in all_items, "No scene contract"
        assert "critique" in all_items, "No critique contract"

        story = all_items["story"][0]
        assert story.status == "seed"
        assert len(all_items["episode"]) == 4
        assert len(all_items["chapter"]) == 12
        assert len(all_items["scene"]) == 36

    def test_pipeline_updates_story_genre(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        orchestrator.run_workflow("00-brief-and-taxonomy")

        store = get_store()
        story = store.list_by_type("story")[0]
        assert story.genre.primary_bisac == "FIC009000"
        assert story.genre.secondary_bisac == ["FIC009020"]

    def test_pipeline_produces_critique(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        orchestrator.run()

        store = get_store()
        critiques = store.list_by_type("critique")
        assert len(critiques) >= 1
        c = critiques[0]
        assert c.verdict in ("pass", "needs_revision", "fail")
        assert c.summary
        # Soft gate produces a composite score summary
        soft = next((x for x in critiques if "composite" in x.summary), None)
        assert soft is not None, f"No soft gate critique found among {len(critiques)} critiques"

    # ── Workflow-by-workflow verification ─────────────────────────────

    def test_workflow_00_brief_and_taxonomy(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        results = orchestrator.run_workflow("00-brief-and-taxonomy")

        assert len(results) == 5
        assert all(r.success for r in results)
        store = get_store()
        assert len(store.list_by_type("theme")) == 1

    def test_workflow_01_seed_to_premise(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        orchestrator.run_workflow("00-brief-and-taxonomy")
        results = orchestrator.run_workflow("01-seed-to-premise")

        assert len(results) == 5
        assert all(r.success for r in results)
        store = get_store()
        chars = store.list_by_type("character")
        assert len(chars) >= 1

    def test_workflow_02_premise_to_structure(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        for wid in ("00-brief-and-taxonomy", "01-seed-to-premise", "02-premise-to-structure"):
            results = orchestrator.run_workflow(wid)
            assert all(r.success for r in results), f"Workflow {wid} failed"

    def test_workflow_03_structure_to_episodes(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        for wid in ("00-brief-and-taxonomy", "01-seed-to-premise", "02-premise-to-structure", "03-structure-to-episodes"):
            results = orchestrator.run_workflow(wid)
            assert all(r.success for r in results), f"Workflow {wid} failed"

        store = get_store()
        assert len(store.list_by_type("episode")) == 4
        assert len(store.list_by_type("chapter")) == 12

    def test_workflow_04_episodes_to_scenes(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        for wid in ("00-brief-and-taxonomy", "01-seed-to-premise", "02-premise-to-structure", "03-structure-to-episodes", "04-episodes-to-scenes"):
            results = orchestrator.run_workflow(wid)
            assert all(r.success for r in results), f"Workflow {wid} failed"

        store = get_store()
        assert len(store.list_by_type("scene")) == 36

    def test_workflow_06_editorial_passes(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        for wid in ("00-brief-and-taxonomy", "01-seed-to-premise", "02-premise-to-structure", "03-structure-to-episodes", "04-episodes-to-scenes", "05-scenes-to-draft", "06-editorial-passes"):
            results = orchestrator.run_workflow(wid)
            assert all(r.success for r in results), f"Workflow {wid} failed"

    def test_workflow_07_critique_and_revision(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        for wid in ("00-brief-and-taxonomy", "01-seed-to-premise", "02-premise-to-structure", "03-structure-to-episodes", "04-episodes-to-scenes", "05-scenes-to-draft", "06-editorial-passes", "07-critique-and-revision"):
            results = orchestrator.run_workflow(wid)
            assert all(r.success for r in results), f"Workflow {wid} failed"

        store = get_store()
        critiques = store.list_by_type("critique")
        assert len(critiques) >= 1

    # ── Coherence engine verification ────────────────────────────────

    def test_hard_gate_receives_episodes_for_propp_and_todorov(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        for wid in ("00-brief-and-taxonomy", "01-seed-to-premise", "02-premise-to-structure", "03-structure-to-episodes"):
            orchestrator.run_workflow(wid)

        store = get_store()
        episodes = store.list_by_type("episode")
        assert len(episodes) == 4

        from src.engine.fabula.coherence import FabulaCoherenceEngine
        episodes_data = [e.model_dump(mode="json") for e in episodes if hasattr(e, "model_dump")]
        report = FabulaCoherenceEngine.run_all_checks(episodes=episodes_data)
        propp_check = [c for c in report.checks if c.name == "propp_sequence"][0]
        todorov_check = [c for c in report.checks if c.name == "todorov_equilibrium"][0]
        assert propp_check.passed is True
        assert todorov_check.passed is True

    def test_golem_events_generate_from_pipeline_story(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        orchestrator.run()

        store = get_store()
        story = store.list_by_type("story")[0]

        from src.engine.golem.generator import GolemEventGenerator
        events = GolemEventGenerator.generate_all_events(story=story)
        assert len(events) == 11

        golem_dicts = [e.to_dict() for e in events]
        for d in golem_dicts:
            assert d["goal"]
            assert d["action_type"]
            assert d["outcome"]
            assert d["perception"]
            assert d["internal_element"]

    def test_pipeline_scenes_pass_multiple_coherence_checks(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()
        orchestrator.run()

        store = get_store()
        scenes = store.list_by_type("scene")
        assert len(scenes) == 36

        from src.engine.fabula.coherence import FabulaCoherenceEngine
        scenes_data = [s.model_dump(mode="json") for s in scenes if hasattr(s, "model_dump")]

        events_data: list[dict] = []
        for i, scene in enumerate(scenes_data):
            diag = scene.get("greimas_diagnostic", {})
            if not diag:
                continue
            preds: list[str] = []
            if i > 0:
                prev_id = scenes_data[i - 1].get("id", "")
                if prev_id:
                    preds.append(str(prev_id))
            events_data.append({
                "id": str(scene.get("id", "")),
                "actant": "",
                "action": diag.get("action_occurs", ""),
                "state_before": diag.get("state_before", ""),
                "state_after": diag.get("state_after", ""),
                "value_object_change": diag.get("value_object_change", "none"),
                "modality_changes": scene.get("modality_changes", []),
                "unlocks": diag.get("future_action_possible_or_blocked", ""),
                "blocks": "",
                "causal_predecessors": preds,
            })

        assert len(events_data) > 0
        report = FabulaCoherenceEngine.run_all_checks(events=events_data, scenes=scenes_data)
        firing_checks = [c for c in report.checks if c.name in (
            "causal_soundness", "character_intentionality", "stakes_presence",
            "conflict_active", "event_necessity",
        )]
        passed_checks = [c for c in firing_checks if c.passed]
        assert len(passed_checks) >= 2, (
            f"Expected at least 2 coherence checks to fire with real data, "
            f"got {len(passed_checks)}: {[(c.name, c.passed, len(c.violations)) for c in firing_checks]}"
        )

    # ── Edge cases ────────────────────────────────────────────────────

    def test_missing_premise_fails_brief_approval(self):
        self._seed_story(premise="")
        orchestrator = PipelineOrchestrator()
        results = orchestrator.run_workflow("00-brief-and-taxonomy")
        approve_results = [r for r in results if not r.success]
        assert len(approve_results) >= 1
        assert any("premise" in (r.message or "").lower() or any("premise" in (e or "").lower() for e in r.errors) for r in approve_results)

    def test_pipeline_with_empty_registry_fails_gracefully(self):
        from src.agents.director import Director
        director = Director({})
        results = director.run_workflow("00-brief-and-taxonomy")
        assert len(results) == 1
        assert not results[0].success
        assert "No agent registered" in results[0].errors[0]

    def test_unknown_workflow_raises(self):
        orchestrator = PipelineOrchestrator()
        with pytest.raises(ValueError, match="Unknown workflow"):
            orchestrator.run_workflow("99-nonexistent")

    def test_workflow_registry_all_stages_present(self):
        expected = [
            "00-brief-and-taxonomy",
            "01-seed-to-premise",
            "02-premise-to-structure",
            "03-structure-to-episodes",
            "04-episodes-to-scenes",
            "05-scenes-to-draft",
            "06-editorial-passes",
            "07-critique-and-revision",
        ]
        for wid in expected:
            assert wid in get_registry(Medium.BOOK), f"Missing workflow: {wid}"
        assert len(get_registry(Medium.BOOK)) == 8

    def test_all_agent_modules_importable(self):
        from src.agents.showrunner import Showrunner
        from src.agents.script_editor import ScriptEditor
        from src.agents.theme_specialist import ThemeSpecialist
        from src.agents.structuralist import Structuralist
        from src.agents.character_architect import CharacterArchitect
        from src.agents.character_simulator import CharacterSimulator
        from src.agents.dialogue_specialist import DialogueSpecialist
        from src.agents.world_researcher import WorldResearcher
        from src.agents.outline_planner import OutlinePlanner
        from src.agents.chapter_planner import ChapterPlanner
        from src.agents.scene_writer import SceneWriter
        from src.agents.continuity_editor import ContinuityEditor
        from src.agents.critic import Critic
        from src.agents.developmental_editor import DevelopmentalEditor
        from src.agents.line_editor import LineEditor
        from src.agents.copy_editor import CopyEditor
        from src.agents.proofreader import Proofreader
        from src.agents.revision_agent import RevisionAgent
        assert Showrunner
        assert ScriptEditor
        assert ThemeSpecialist
        assert Structuralist
        assert CharacterArchitect
        assert CharacterSimulator
        assert DialogueSpecialist
        assert WorldResearcher
        assert OutlinePlanner
        assert ChapterPlanner
        assert SceneWriter
        assert ContinuityEditor
        assert Critic
        assert DevelopmentalEditor
        assert LineEditor
        assert CopyEditor
        assert Proofreader
        assert RevisionAgent

    def test_default_agent_registry_creates_all_agents(self):
        agents = default_agent_registry()
        assert len(agents) == 18  # 18 agents in the registry
        assert "showrunner" in agents
        assert "critic" in agents
        assert "revision_agent" in agents

    def test_director_execution_log(self):
        self._seed_story()
        from src.agents.director import Director
        agents = default_agent_registry()
        director = Director(agents)
        director.run_full_pipeline()

        workflow_ids = {e["workflow"] for e in director.execution_log}
        assert len(workflow_ids) == 8

        total_steps = len(director.execution_log)
        all_workflow_steps = set()
        for wid, steps in get_registry(Medium.BOOK).items():
            for step in steps:
                all_workflow_steps.add((wid, step.agent_role, step.step_id))

        logged_steps = set()
        for e in director.execution_log:
            logged_steps.add((e["workflow"], e["agent"], e["step"]))

        assert logged_steps.issubset(all_workflow_steps)
        assert len(logged_steps) > 0
        for (wid, agent, step) in logged_steps:
            assert step in (s.step_id for s in get_registry(Medium.BOOK)[wid]), f"Unexpected step {step} in {wid}"

    def test_each_workflow_step_produces_result(self):
        self._seed_story()
        orchestrator = PipelineOrchestrator()

        for wid in sorted(get_registry(Medium.BOOK).keys()):
            results = orchestrator.run_workflow(wid)
            expected_steps = len(get_registry(Medium.BOOK)[wid])
            assert len(results) == expected_steps, (
                f"Workflow {wid}: expected {expected_steps} results, got {len(results)}"
            )
            assert all(r.success for r in results), (
                f"Workflow {wid} failed: {[r.message for r in results if not r.success]}"
            )


class TestPipelineOrchestratorInit:
    def setup_method(self):
        reset_store()

    def test_orchestrator_default_init(self):
        orch = PipelineOrchestrator()
        assert orch.store is not None
        assert len(orch.agents) == 18
        assert orch.director is not None

    def test_orchestrator_with_custom_store(self):
        from src.agents.store import ContractStore
        store = ContractStore()
        orch = PipelineOrchestrator(store=store)
        assert orch.store is store

    def test_orchestrator_with_custom_agents(self):
        from src.agents.base import BaseAgent
        from src.agents.store import ContractStore

        class MinimalAgent(BaseAgent):
            def execute(self, ctx):
                from src.agents.base import AgentResult
                return AgentResult(success=True, message="ok")

        store = ContractStore()
        agents = {"showrunner": MinimalAgent(role="showrunner", store=store)}
        orch = PipelineOrchestrator(agents=agents, store=store)
        result = orch.run_workflow("00-brief-and-taxonomy")
        assert not result[0].success  # most steps fail due to missing agents
