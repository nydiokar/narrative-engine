"""World Researcher — defines worldbuilding dimensions and rules."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class WorldResearcher(BaseAgent):
    """Establishes world axes, rules, and setting assignments per episode."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="world_researcher", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "set_world_axes":
            return self._set_world_axes(context)
        if context.step_id == "assign_settings":
            return self._assign_settings(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _set_world_axes(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="World axes defined")

    def _assign_settings(self, context: AgentContext) -> AgentResult:
        episodes = self.list_contracts("episode")
        return AgentResult(
            success=True,
            message=f"Settings assigned to {len(episodes)} episodes",
        )
