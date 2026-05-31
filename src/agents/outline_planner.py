"""Outline Planner — segments fabula into episodes and acts."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CanonicalPhase, EpisodeContract, GreimasEpisodeTracking


class OutlinePlanner(BaseAgent):
    """Groups events into acts and episodes with narrative program assignments."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="outline_planner", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        return ["story", "character"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )

        if context.step_id == "segment_fabula":
            return self._segment_fabula(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _segment_fabula(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)

        contracts_data = result.get("contracts_data", [])
        if not contracts_data:
            fallback_phases = [
                CanonicalPhase.MANIPULATION,
                CanonicalPhase.COMPETENCE,
                CanonicalPhase.PERFORMANCE,
            ]
            fallback = []
            for i, phase in enumerate(fallback_phases):
                fallback.append({
                    "sequence_number": i,
                    "title": f"Act {i + 1}",
                    "summary": f"Core narrative arc segment {i + 1}",
                    "canonical_phase": phase.value,
                    "greimas_tracking": {
                        "subject": "",
                        "object_of_value": "",
                        "current_state": "initial",
                        "desired_transformation": "to be determined",
                        "opponent": "",
                        "opponent_value_logic": "",
                        "helper": "",
                        "action_type": "",
                        "resulting_state": "",
                        "sanction_or_judgment": "",
                        "contribution_to_whole_fabula": "",
                    },
                })
            contracts_data = fallback

        artifacts = []
        for ep_data in contracts_data:
            try:
                ep = EpisodeContract(**ep_data)
                eid = self.write_contract("episode", ep)
                artifacts.append(eid)
            except Exception as e:
                return AgentResult(
                    success=False,
                    errors=[f"Invalid episode data: {e}"],
                )

        return AgentResult(
            success=True,
            message=f"Fabula segmented into {len(artifacts)} episodes",
            artifacts=artifacts,
        )
