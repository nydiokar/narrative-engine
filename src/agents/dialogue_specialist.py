"""Dialogue Specialist — plans speech acts and ensures narrative purpose."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class DialogueSpecialist(BaseAgent):
    """Plans dialogue function annotations per scene, ensuring each line serves a purpose."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="dialogue_specialist", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "plan_speech_acts":
            return self._plan_speech_acts(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _plan_speech_acts(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        scenes = self.list_contracts("scene")
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", f"Speech acts planned for {len(scenes)} scenes"),
            errors=result.get("errors", []),
        )
