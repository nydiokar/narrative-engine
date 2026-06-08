"""Dialogue Specialist — plans speech acts and ensures narrative purpose."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CritiqueContract


class DialogueSpecialist(BaseAgent):
    """Plans dialogue function annotations per scene, ensuring each line serves a purpose."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="dialogue_specialist", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        return ["character"]

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id not in ("plan_speech_acts",):
            return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )
        return self._plan_speech_acts(context)

    def _plan_speech_acts(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        contracts_data = result.get("contracts_data")
        if isinstance(contracts_data, list) and contracts_data:
            cc = CritiqueContract(
                target_type="speech_acts",
                reviewer="dialogue_specialist",
                verdict="pass" if result.get("success", False) else "fail",
                summary=result.get("message", "Speech acts planned"),
            )
            self.write_contract("critique", cc)
        scenes = self.list_contracts("scene")
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", f"Speech acts planned for {len(scenes)} scenes"),
            errors=result.get("errors", []),
        )
