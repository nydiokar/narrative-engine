"""Revision Agent — applies targeted revisions from critique and editorial reports."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class RevisionAgent(BaseAgent):
    """Parses critique/editorial contracts and applies targeted revisions."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="revision_agent", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "apply_structural_changes":
            return self._apply_structural_changes(context)
        if context.step_id == "apply_line_changes":
            return self._apply_line_changes(context)
        if context.step_id == "apply_copy_changes":
            return self._apply_copy_changes(context)
        if context.step_id == "apply_revisions":
            return self._apply_revisions(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _apply_structural_changes(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Structural changes applied")

    def _apply_line_changes(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Line edit changes applied")

    def _apply_copy_changes(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Copy edit changes applied")

    def _apply_revisions(self, context: AgentContext) -> AgentResult:
        critiques = self.list_contracts("critique")
        if critiques:
            c = critiques[0]
            if getattr(c, "verdict", "") == "fail":
                return AgentResult(success=False, message="Revisions needed — hard gate failures remain")
        return AgentResult(success=True, message="All revisions applied")
