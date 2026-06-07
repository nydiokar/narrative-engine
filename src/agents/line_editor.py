"""Line Editor — prose-level refinement pass."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class LineEditor(BaseAgent):
    """Improves sentence rhythm, diction, metaphor density while preserving voice."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="line_editor", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "refine_prose":
            return self._refine_prose(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _refine_prose(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "Line edit complete — prose refined"),
            errors=result.get("errors", []),
        )
