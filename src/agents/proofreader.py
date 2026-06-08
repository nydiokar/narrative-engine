"""Proofreader — final quality check before clearance."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CritiqueContract


class Proofreader(BaseAgent):
    """Residual typos, formatting, chapter headings, metadata validation."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="proofreader", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        return ["scene", "chapter"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )
        if context.step_id == "final_check":
            return self._final_check(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _final_check(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        contract_data = result.get("contract_data")
        if isinstance(contract_data, dict):
            cc = CritiqueContract(
                target_type="proofread",
                reviewer="proofreader",
                verdict=contract_data.get("clearance_recommendation", "conditional"),
                summary=result.get("message", "Proofread complete"),
            )
            self.write_contract("critique", cc)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "Proofread complete — clearance certificate issued"),
            errors=result.get("errors", []),
        )
