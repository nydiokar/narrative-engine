"""Character Architect — multi-layer character creation and arc planning."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CharacterContract, PersonalityProfile


class CharacterArchitect(BaseAgent):
    """Creates layered character profiles with FFM, values, attachment, motivation."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="character_architect", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        if step_id == "draft_protagonists":
            return ["story"]
        if step_id == "refine_arcs":
            return ["story", "character", "episode"]
        return ["story"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )

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
        result = self._call_llm_for_step(context)

        contract_data = result.get("contract_data")
        if not contract_data or not contract_data.get("name"):
            hero = CharacterContract(
                name="Protagonist",
                description="Primary viewpoint character",
                actant_roles=["subject"],
                personality=PersonalityProfile(openness=7, conscientiousness=6, extraversion=5, agreeableness=6, neuroticism=4),
                core_desires=["freedom", "belonging"],
                core_fears=["captivity", "isolation"],
            )
            character = hero
        else:
            try:
                character = CharacterContract(**contract_data)
            except Exception as e:
                self.log("warning", f"LLM contract_data invalid, using fallback: {e}")
                character = CharacterContract(
                    name=contract_data.get("name", "Protagonist"),
                    description=contract_data.get("description", "Primary viewpoint character"),
                    actant_roles=contract_data.get("actant_roles", ["subject"]),
                    personality=PersonalityProfile(
                        openness=contract_data.get("personality", {}).get("openness", 7),
                        conscientiousness=contract_data.get("personality", {}).get("conscientiousness", 6),
                        extraversion=contract_data.get("personality", {}).get("extraversion", 5),
                        agreeableness=contract_data.get("personality", {}).get("agreeableness", 6),
                        neuroticism=contract_data.get("personality", {}).get("neuroticism", 4),
                    ),
                    core_desires=contract_data.get("core_desires", ["freedom", "belonging"]),
                    core_fears=contract_data.get("core_fears", ["captivity", "isolation"]),
                )

        cid = self.write_contract("character", character)

        story = self.list_contracts("story")[0]
        story.subject_id = cid
        self.write_contract("story", story)

        return AgentResult(
            success=True,
            message=result.get("message", "Protagonist drafted"),
            artifacts=[cid],
            errors=result.get("errors", []),
        )

    def _refine_arcs(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Character arcs refined"),
            errors=result.get("errors", []),
        )
