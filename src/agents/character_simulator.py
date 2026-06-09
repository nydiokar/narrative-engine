"""Character Simulator — enacts characters through episodes, generates state vectors."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CritiqueContract


class CharacterSimulator(BaseAgent):
    """Loads character profiles and simulates responses to each event in an episode."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="character_simulator", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        return ["character", "episode"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )
        if context.step_id == "enact_episode":
            return self._enact_episode(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _enact_episode(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        contracts_data = result.get("contracts_data")
        has_data = isinstance(contracts_data, list) and len(contracts_data) > 0
        if has_data:
            cc = CritiqueContract(
                target_type="character_simulation",
                reviewer="character_simulator",
                verdict="pass" if result.get("success", False) else "fail",
                summary=result.get("message", "Character simulation complete"),
            )
            self.write_contract("critique", cc)
        chars = self.list_contracts("character")
        if not result.get("success", False) and not has_data:
            return AgentResult(
                success=False,
                message="Character simulation failed — no data from LLM",
                errors=result.get("errors", ["LLM produced no simulation data"]),
            )
        return AgentResult(
            success=True,
            message=result.get("message", f"Simulated {len(chars)} characters through episode"),
            artifacts=[str(c.id) for c in chars],
            errors=result.get("errors", []),
        )
