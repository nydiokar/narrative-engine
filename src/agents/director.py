"""Director — pipeline execution orchestrator.

Runs workflows by dispatching to the correct agent sequence.
Not a BaseAgent itself — it orchestrates agents.

Medium-agnostic: workflows 00-03 (structure) are identical across
mediums. Workflows 04-06 (rendering) differ by medium. Workflow 07
(critique) is identical.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from logging import Logger
from typing import Any

from src.agents.base import AgentContext, AgentResult
from src.agents.store import ContractStore, get_store
from src.contracts.models import Medium


@dataclass
class WorkflowStep:
    agent_role: str
    step_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


# ── Shared structure workflows (identical across all mediums) ────────────

_SHARED_WORKFLOWS: dict[str, list[WorkflowStep]] = {
    "00-brief-and-taxonomy": [
        WorkflowStep("theme_specialist", "select_themes"),
        WorkflowStep("theme_specialist", "select_genre"),
        WorkflowStep("world_researcher", "set_world_axes"),
        WorkflowStep("character_architect", "prepare_layers"),
        WorkflowStep("showrunner", "approve_brief"),
    ],
    "01-seed-to-premise": [
        WorkflowStep("showrunner", "review_brief"),
        WorkflowStep("structuralist", "analyze_premise"),
        WorkflowStep("structuralist", "select_backbone"),
        WorkflowStep("character_architect", "draft_protagonists"),
        WorkflowStep("showrunner", "approve_premise"),
    ],
    "02-premise-to-structure": [
        WorkflowStep("structuralist", "build_fabula"),
        WorkflowStep("structuralist", "check_constraints"),
        WorkflowStep("theme_specialist", "validate_thematic_fit"),
        WorkflowStep("showrunner", "approve_structure"),
    ],
    "03-structure-to-episodes": [
        WorkflowStep("outline_planner", "segment_fabula"),
        WorkflowStep("chapter_planner", "divide_episodes"),
        WorkflowStep("character_architect", "refine_arcs"),
        WorkflowStep("world_researcher", "assign_settings"),
        WorkflowStep("showrunner", "approve_episodes"),
    ],
    "07-critique-and-revision": [
        WorkflowStep("critic", "run_hard_gate"),
        WorkflowStep("critic", "run_soft_gate"),
        WorkflowStep("critic", "run_greimas_diagnostics"),
        WorkflowStep("revision_agent", "apply_revisions"),
        WorkflowStep("showrunner", "approve_final"),
    ],
}

# ── Book-specific rendering workflows ────────────────────────────────────

_BOOK_WORKFLOWS: dict[str, list[WorkflowStep]] = {
    "04-episodes-to-scenes": [
        WorkflowStep("character_simulator", "enact_episode"),
        WorkflowStep("dialogue_specialist", "plan_speech_acts"),
        WorkflowStep("scene_writer", "render_prose"),
        WorkflowStep("scene_writer", "run_greimas_diagnostic"),
        WorkflowStep("continuity_editor", "check_consistency"),
    ],
    "05-scenes-to-draft": [
        WorkflowStep("scene_writer", "finalize_prose"),
        WorkflowStep("continuity_editor", "final_check"),
        WorkflowStep("showrunner", "assemble_draft"),
    ],
    "06-editorial-passes": [
        WorkflowStep("developmental_editor", "evaluate_draft"),
        WorkflowStep("revision_agent", "apply_structural_changes"),
        WorkflowStep("line_editor", "refine_prose"),
        WorkflowStep("revision_agent", "apply_line_changes"),
        WorkflowStep("copy_editor", "check_consistency"),
        WorkflowStep("revision_agent", "apply_copy_changes"),
        WorkflowStep("proofreader", "final_check"),
    ],
}

# ── Animation-specific rendering workflows ───────────────────────────────
# Animation discourse: visual scene descriptions + dialogue, storyboard
# framing, no prose editing (script edit instead).

_ANIMATION_WORKFLOWS: dict[str, list[WorkflowStep]] = {
    "04-episodes-to-scenes": [
        WorkflowStep("character_simulator", "enact_episode"),
        WorkflowStep("dialogue_specialist", "plan_speech_acts"),
        WorkflowStep("scene_writer", "render_visual_scene"),
        WorkflowStep("scene_writer", "run_greimas_diagnostic"),
        WorkflowStep("continuity_editor", "check_consistency"),
    ],
    "05-scenes-to-draft": [
        WorkflowStep("scene_writer", "finalize_script"),
        WorkflowStep("continuity_editor", "final_check"),
        WorkflowStep("showrunner", "assemble_script"),
    ],
    "06-editorial-passes": [
        WorkflowStep("developmental_editor", "evaluate_draft"),
        WorkflowStep("revision_agent", "apply_structural_changes"),
        WorkflowStep("script_editor", "refine_script"),
        WorkflowStep("revision_agent", "apply_script_changes"),
        WorkflowStep("continuity_editor", "check_consistency"),
    ],
}

# ── Movie (live-action) rendering workflows ──────────────────────────────
# Very close to animation — visual scene descriptions, blocking notes,
# dialogue. Differences are in framing language (cinematic vs animated).

_MOVIE_WORKFLOWS: dict[str, list[WorkflowStep]] = {
    "04-episodes-to-scenes": [
        WorkflowStep("character_simulator", "enact_episode"),
        WorkflowStep("dialogue_specialist", "plan_speech_acts"),
        WorkflowStep("scene_writer", "render_cinematic_scene"),
        WorkflowStep("scene_writer", "run_greimas_diagnostic"),
        WorkflowStep("continuity_editor", "check_consistency"),
    ],
    "05-scenes-to-draft": [
        WorkflowStep("scene_writer", "finalize_screenplay"),
        WorkflowStep("continuity_editor", "final_check"),
        WorkflowStep("showrunner", "assemble_screenplay"),
    ],
    "06-editorial-passes": [
        WorkflowStep("developmental_editor", "evaluate_draft"),
        WorkflowStep("revision_agent", "apply_structural_changes"),
        WorkflowStep("script_editor", "refine_script"),
        WorkflowStep("revision_agent", "apply_script_changes"),
        WorkflowStep("continuity_editor", "check_consistency"),
    ],
}

# ── Series (episodic TV/streaming) rendering workflows ───────────────────

_SERIES_WORKFLOWS: dict[str, list[WorkflowStep]] = {
    "04-episodes-to-scenes": [
        WorkflowStep("character_simulator", "enact_episode"),
        WorkflowStep("dialogue_specialist", "plan_speech_acts"),
        WorkflowStep("scene_writer", "render_television_scene"),
        WorkflowStep("scene_writer", "run_greimas_diagnostic"),
        WorkflowStep("continuity_editor", "check_consistency"),
    ],
    "05-scenes-to-draft": [
        WorkflowStep("scene_writer", "finalize_teleplay"),
        WorkflowStep("continuity_editor", "final_check"),
        WorkflowStep("showrunner", "assemble_teleplay"),
    ],
    "06-editorial-passes": [
        WorkflowStep("developmental_editor", "evaluate_draft"),
        WorkflowStep("revision_agent", "apply_structural_changes"),
        WorkflowStep("script_editor", "refine_script"),
        WorkflowStep("revision_agent", "apply_script_changes"),
        WorkflowStep("continuity_editor", "check_consistency"),
    ],
}

# ── Registry lookup ──────────────────────────────────────────────────────

_MEDIUM_REGISTRIES: dict[Medium, dict[str, list[WorkflowStep]]] = {
    Medium.BOOK: _BOOK_WORKFLOWS,
    Medium.ANIMATION: _ANIMATION_WORKFLOWS,
    Medium.MOVIE: _MOVIE_WORKFLOWS,
    Medium.SERIES: _SERIES_WORKFLOWS,
}

# Default fallback for game, audio_drama — use book's editorial structure
# but animation's scene structure (visual/audio description + dialogue).
_MEDIUM_REGISTRIES.setdefault(Medium.GAME, _ANIMATION_WORKFLOWS)
_MEDIUM_REGISTRIES.setdefault(Medium.AUDIO_DRAMA, _ANIMATION_WORKFLOWS)

# All workflow IDs sorted (for run_full_pipeline ordering)
_ALL_WORKFLOW_IDS = ["00-brief-and-taxonomy", "01-seed-to-premise",
                      "02-premise-to-structure", "03-structure-to-episodes",
                      "04-episodes-to-scenes", "05-scenes-to-draft",
                      "06-editorial-passes", "07-critique-and-revision"]


def get_registry(medium: Medium = Medium.BOOK) -> dict[str, list[WorkflowStep]]:
    """Return the merged workflow registry for the given medium.

    Structure workflows (00–03, 07) are shared across all mediums.
    Rendering workflows (04–06) are medium-specific.
    """
    medium_workflows = _MEDIUM_REGISTRIES.get(medium, _BOOK_WORKFLOWS)
    merged = dict(_SHARED_WORKFLOWS)
    merged.update(medium_workflows)
    return merged


class Director:
    """Orchestrates the narrative pipeline — dispatches agents per workflow.

    Medium-agnostic core: selects the correct workflow registry based on
    the story contract's medium field at runtime.
    """

    def __init__(
        self,
        agents: dict[str, BaseAgent],
        store: ContractStore | None = None,
        logger: Logger | None = None,
        medium: Medium = Medium.BOOK,
    ) -> None:
        self.agents = agents
        self.store = store or get_store()
        self.logger = logger
        self.medium = medium
        self.registry: dict[str, list[WorkflowStep]] = get_registry(medium)
        self.execution_log: list[dict[str, Any]] = []

    def log(self, message: str) -> None:
        if self.logger:
            self.logger.info(message)

    def run_workflow(self, workflow_id: str) -> list[AgentResult]:
        steps = self.registry.get(workflow_id)
        if not steps:
            msg = f"Unknown workflow: {workflow_id}"
            raise ValueError(msg)

        self.log(f"Starting workflow: {workflow_id}")
        results: list[AgentResult] = []

        for step in steps:
            agent = self.agents.get(step.agent_role)
            if not agent:
                msg = f"No agent registered for '{step.agent_role}' — required by workflow {workflow_id}"
                self.log(f"  ERROR: {msg}")
                results.append(AgentResult(success=False, errors=[msg]))
                self.execution_log.append({
                    "workflow": workflow_id,
                    "agent": step.agent_role,
                    "step": step.step_id,
                    "success": False,
                    "message": msg,
                })
                break

            context = AgentContext(
                workflow_id=workflow_id,
                step_id=step.step_id,
                metadata={
                    **(step.metadata or {}),
                    "medium": self.medium.value,
                },
            )

            self.log(f"  Dispatching {step.agent_role}.{step.step_id}")
            result = agent.execute(context)
            results.append(result)
            self.execution_log.append({
                "workflow": workflow_id,
                "agent": step.agent_role,
                "step": step.step_id,
                "success": result.success,
                "message": result.message,
            })

            if not result.success:
                self.log(f"  Step failed: {result.message}")
                if result.errors:
                    for err in result.errors:
                        self.log(f"    Error: {err}")
                break

        return results

    def run_full_pipeline(self) -> dict[str, list[AgentResult]]:
        pipeline_results: dict[str, list[AgentResult]] = {}
        for wid in _ALL_WORKFLOW_IDS:
            if wid in self.registry:
                results = self.run_workflow(wid)
                pipeline_results[wid] = results
        return pipeline_results
