"""World Researcher — defines worldbuilding dimensions and rules."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CritiqueContract, WorldContract, WorldDimension


class WorldResearcher(BaseAgent):
    """Establishes world axes, rules, and setting assignments per episode."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="world_researcher", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        if step_id == "assign_settings":
            return ["story", "episode"]
        return ["story"]

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id not in ("set_world_axes", "assign_settings"):
            return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )
        if context.step_id == "set_world_axes":
            return self._set_world_axes(context)
        return self._assign_settings(context)

    def _set_world_axes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        contract_data = result.get("contract_data")
        if isinstance(contract_data, dict):
            axes_data = contract_data.get("axes", contract_data.get("dimensions", []))
            if isinstance(axes_data, list) and axes_data:
                dimensions = []
                for a in axes_data:
                    if isinstance(a, dict):
                        dimensions.append(WorldDimension(
                            axis=a.get("axis", a.get("name", "")),
                            value=float(a.get("value", 0.0)),
                            description=a.get("description", ""),
                        ))
                wc = WorldContract(
                    name=contract_data.get("world_name", contract_data.get("name", "Story World")),
                    dimensions=dimensions,
                    rules=contract_data.get("rules", []),
                    description=contract_data.get("description", ""),
                )
                self.write_contract("world", wc)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "World axes defined"),
            errors=result.get("errors", []),
        )

    def _assign_settings(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        contracts_data = result.get("contracts_data")
        if isinstance(contracts_data, list) and contracts_data:
            cc = CritiqueContract(
                target_type="setting_assignments",
                reviewer="world_researcher",
                verdict="pass" if result.get("success", False) else "fail",
                summary=result.get("message", "Settings assigned"),
            )
            self.write_contract("critique", cc)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "Settings assigned"),
            errors=result.get("errors", []),
        )
