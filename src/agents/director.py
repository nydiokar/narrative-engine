"""Director — pipeline execution orchestrator.

Runs workflows by dispatching to the correct agent sequence.
Not a BaseAgent itself — it orchestrates agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from logging import Logger
from typing import Any

from src.agents.base import AgentContext, AgentResult
from src.agents.store import ContractStore, get_store


@dataclass
class WorkflowStep:
    agent_role: str
    step_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


WORKFLOW_REGISTRY: dict[str, list[WorkflowStep]] = {
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
    "07-critique-and-revision": [
        WorkflowStep("critic", "run_hard_gate"),
        WorkflowStep("critic", "run_soft_gate"),
        WorkflowStep("critic", "run_greimas_diagnostics"),
        WorkflowStep("revision_agent", "apply_revisions"),
        WorkflowStep("showrunner", "approve_final"),
    ],
}


class Director:
    """Orchestrates the narrative pipeline — dispatches agents per workflow."""

    def __init__(
        self,
        agents: dict[str, BaseAgent],
        store: ContractStore | None = None,
        logger: Logger | None = None,
    ) -> None:
        self.agents = agents
        self.store = store or get_store()
        self.logger = logger
        self.execution_log: list[dict[str, Any]] = []

    def log(self, message: str) -> None:
        if self.logger:
            self.logger.info(message)

    def run_workflow(self, workflow_id: str) -> list[AgentResult]:
        steps = WORKFLOW_REGISTRY.get(workflow_id)
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
                metadata=step.metadata,
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
        for wid in sorted(WORKFLOW_REGISTRY.keys()):
            results = self.run_workflow(wid)
            pipeline_results[wid] = results
        return pipeline_results
