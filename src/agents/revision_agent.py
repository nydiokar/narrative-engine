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
        if context.step_id == "apply_script_changes":
            return self._apply_script_changes(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _apply_structural_changes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Structural changes applied"),
            errors=result.get("errors", []),
        )

    def _apply_line_changes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Line edit changes applied"),
            errors=result.get("errors", []),
        )

    def _apply_copy_changes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Copy edit changes applied"),
            errors=result.get("errors", []),
        )

    def _apply_script_changes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Script edit changes applied"),
            errors=result.get("errors", []),
        )

    def _apply_revisions(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        critiques = self.list_contracts("critique")
        if critiques:
            c = critiques[0]
            if getattr(c, "verdict", "") == "fail":
                return AgentResult(
                    success=False,
                    message=result.get("message", "Revisions needed — hard gate failures remain"),
                    errors=result.get("errors", []),
                )
        return AgentResult(
            success=True,
            message=result.get("message", "All revisions applied"),
            errors=result.get("errors", []),
        )
