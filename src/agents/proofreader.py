"""Proofreader — final quality check before clearance."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class Proofreader(BaseAgent):
    """Residual typos, formatting, chapter headings, metadata validation."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="proofreader", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "final_check":
            return self._final_check(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _final_check(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "Proofread complete — clearance certificate issued"),
            errors=result.get("errors", []),
        )
