"""Line Editor — prose-level refinement pass."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CritiqueContract


class LineEditor(BaseAgent):
    """Improves sentence rhythm, diction, metaphor density while preserving voice."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="line_editor", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        return ["scene"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )
        if context.step_id == "refine_prose":
            return self._refine_prose(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _refine_prose(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        contracts_data = result.get("contracts_data")
        if isinstance(contracts_data, list) and contracts_data:
            edit_count = sum(len(e.get("edits", [])) for e in contracts_data)
            cc = CritiqueContract(
                target_type="line_edit",
                reviewer="line_editor",
                verdict="pass",
                summary=result.get("message", f"Line edit complete — {edit_count} edits"),
            )
            self.write_contract("critique", cc)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "Line edit complete — prose refined"),
            errors=result.get("errors", []),
        )
