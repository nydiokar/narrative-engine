"""Outline Planner — segments fabula into episodes and acts."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import EpisodeContract


class OutlinePlanner(BaseAgent):
    """Groups events into acts and episodes with narrative program assignments."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="outline_planner", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "segment_fabula":
            return self._segment_fabula(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _segment_fabula(self, context: AgentContext) -> AgentResult:
        artifacts = []
        for i in range(3):
            ep = EpisodeContract(
                sequence_number=i,
                title=f"Act {i + 1}",
                summary=f"Core narrative arc segment {i + 1}",
            )
            eid = self.write_contract("episode", ep)
            artifacts.append(eid)
        return AgentResult(success=True, message="Fabula segmented into 3 episodes", artifacts=artifacts)
