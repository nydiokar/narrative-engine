"""Worldbuilder — world creation with dimension axes and rule systems."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class Worldbuilder(BaseAgent):
    """Builds consistent world systems with dimension axes and rule enforcement."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="worldbuilder", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "build_world":
            return self._build_world(context)
        if context.step_id == "validate_consistency":
            return self._validate_consistency(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _build_world(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "World configuration ready"),
            errors=result.get("errors", []),
        )

    def _validate_consistency(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "World consistency validated"),
            errors=result.get("errors", []),
        )
