"""Copy Editor — grammar, spelling, timeline, and terminology consistency."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CritiqueContract


class CopyEditor(BaseAgent):
    """Checks grammar, spelling, cross-references, timeline, and style guide adherence."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="copy_editor", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        return ["scene"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )
        if context.step_id == "check_consistency":
            return self._check_consistency(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _check_consistency(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        quality_score = result.get("contract_data", {}).get("quality_score")
        if quality_score is not None:
            cc = CritiqueContract(
                target_type="copy_edit",
                reviewer="copy_editor",
                verdict="pass" if result.get("success", False) else "fail",
                summary=result.get("message", "Copy edit complete"),
            )
            self.write_contract("critique", cc)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "Copy edit complete — consistency verified"),
            errors=result.get("errors", []),
        )
