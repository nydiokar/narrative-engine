"""Copy Editor — grammar, spelling, timeline, and terminology consistency."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class CopyEditor(BaseAgent):
    """Checks grammar, spelling, cross-references, timeline, and style guide adherence."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="copy_editor", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "check_consistency":
            return self._check_consistency(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _check_consistency(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Copy edit complete — consistency verified"),
            errors=result.get("errors", []),
        )
