"""Character Simulator — enacts characters through episodes, generates state vectors."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class CharacterSimulator(BaseAgent):
    """Loads character profiles and simulates responses to each event in an episode."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="character_simulator", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "enact_episode":
            return self._enact_episode(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _enact_episode(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        chars = self.list_contracts("character")
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", f"Simulated {len(chars)} characters through episode"),
            artifacts=[str(c.id) for c in chars],
            errors=result.get("errors", []),
        )
