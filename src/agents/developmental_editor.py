"""Developmental Editor — structural-level editorial pass."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class DevelopmentalEditor(BaseAgent):
    """Evaluates narrative structure, pacing, act architecture, and genre delivery."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="developmental_editor", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "evaluate_draft":
            return self._evaluate_draft(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _evaluate_draft(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        stories = self.list_contracts("story")
        if stories:
            title = getattr(stories[0], "title", "untitled")
            return AgentResult(
                success=result.get("success", True),
                message=result.get("message", f"Developmental edit complete for '{title}' — structural recommendations issued"),
                errors=result.get("errors", []),
            )
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Developmental edit complete"),
            errors=result.get("errors", []),
        )
