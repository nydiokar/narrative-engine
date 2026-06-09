"""Revision Agent — applies targeted revisions from critique and editorial reports."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class RevisionAgent(BaseAgent):
    """Parses critique/editorial contracts and applies targeted revisions."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="revision_agent", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        return ["critique"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=True,
                message=f"Skipped (missing prerequisites: {missing})",
            )
        if context.step_id == "apply_structural_changes":
            return self._apply_structural_changes(context)
        if context.step_id == "apply_line_changes":
            return self._apply_line_changes(context)
        if context.step_id == "apply_copy_changes":
            return self._apply_copy_changes(context)
        if context.step_id == "apply_revisions":
            return self._apply_revisions(context)
        if context.step_id == "apply_script_changes":
            return self._apply_script_changes(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _apply_structural_changes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        if not result.get("success", False):
            return AgentResult(
                success=False,
                message=result.get("message", "Structural changes failed"),
                errors=result.get("errors", []),
            )
        applied = self._apply_changes_from_result(result)
        return AgentResult(
            success=True,
            message=f"Structural changes applied: {applied} contract(s) modified",
            errors=result.get("errors", []),
        )

    def _apply_line_changes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        if not result.get("success", False):
            return AgentResult(
                success=False,
                message=result.get("message", "Line edit changes failed"),
                errors=result.get("errors", []),
            )
        applied = self._apply_changes_from_result(result)
        return AgentResult(
            success=True,
            message=f"Line edit changes applied: {applied} contract(s) modified",
            errors=result.get("errors", []),
        )

    def _apply_copy_changes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        if not result.get("success", False):
            return AgentResult(
                success=False,
                message=result.get("message", "Copy edit changes failed"),
                errors=result.get("errors", []),
            )
        applied = self._apply_changes_from_result(result)
        return AgentResult(
            success=True,
            message=f"Copy edit changes applied: {applied} contract(s) modified",
            errors=result.get("errors", []),
        )

    def _apply_script_changes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        if not result.get("success", False):
            return AgentResult(
                success=False,
                message=result.get("message", "Script edit changes failed"),
                errors=result.get("errors", []),
            )
        applied = self._apply_changes_from_result(result)
        return AgentResult(
            success=True,
            message=f"Script edit changes applied: {applied} contract(s) modified",
            errors=result.get("errors", []),
        )

    def _apply_revisions(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        critiques = self.list_contracts("critique")
        if critiques:
            c = critiques[0]
            if getattr(c, "verdict", "") == "fail":
                return AgentResult(
                    success=False,
                    message=result.get("message", "Revisions needed — hard gate failures remain"),
                    errors=result.get("errors", []),
                )
        applied = self._apply_changes_from_result(result) if result.get("success", False) else 0
        return AgentResult(
            success=True,
            message=f"All revisions applied ({applied} contract(s) modified)",
            errors=result.get("errors", []),
        )

    def _apply_changes_from_result(self, result: dict) -> int:
        """Parse revision changes from LLM output and apply them to contracts.

        Expects result['contract_data'] with structure:
          {
            "changes": [
              {
                "type": "scene",
                "contract_id": "<uuid>",
                "field": "content",
                "new_value": "replaced prose text"
              },
              ...
            ]
          }
        Returns count of successfully applied changes.
        """
        contract_data = result.get("contract_data", {})
        changes = contract_data.get("changes", []) if isinstance(contract_data, dict) else []
        if not changes:
            return 0

        applied = 0
        for change in changes:
            try:
                ctype = change.get("type", "scene")
                cid = change.get("contract_id", "")
                field = change.get("field", "")
                new_value = change.get("new_value")

                if not cid or not field or new_value is None:
                    self.log("warning", f"Skipping change — missing cid/field/value: {change}")
                    continue

                contracts = self.list_contracts(ctype)
                target = None
                for c in contracts:
                    if str(c.id) == cid:
                        target = c
                        break
                if target is None:
                    self.log("warning", f"Contract {cid} of type {ctype} not found")
                    continue

                if not hasattr(target, field):
                    self.log("warning", f"Field '{field}' does not exist on {ctype} contract {cid}")
                    continue

                setattr(target, field, new_value)
                self.write_contract(ctype, target)
                applied += 1
            except Exception as e:
                self.log("warning", f"Failed to apply change {change}: {e}")

        return applied
