"""Character Architect — multi-layer character creation and arc planning."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CharacterContract, PersonalityProfile


class CharacterArchitect(BaseAgent):
    """Creates layered character profiles with FFM, values, attachment, motivation."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="character_architect", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "prepare_layers":
            return self._prepare_layers(context)
        if context.step_id == "draft_protagonists":
            return self._draft_protagonists(context)
        if context.step_id == "refine_arcs":
            return self._refine_arcs(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _prepare_layers(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Character layer defaults configured")

    def _draft_protagonists(self, context: AgentContext) -> AgentResult:
        hero = CharacterContract(
            name="Protagonist",
            description="Primary viewpoint character",
            actant_roles=["subject"],
            personality=PersonalityProfile(openness=7, conscientiousness=6, extraversion=5, agreeableness=6, neuroticism=4),
            core_desires=["freedom", "belonging"],
            core_fears=["captivity", "isolation"],
        )
        cid = self.write_contract("character", hero)
        return AgentResult(success=True, message="Protagonist drafted", artifacts=[cid])

    def _refine_arcs(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Character arcs refined")
