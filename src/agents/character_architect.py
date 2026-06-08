"""Character Architect — multi-layer character creation and arc planning."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CharacterContract, PersonalityProfile


def _build_character(data: dict[str, Any]) -> CharacterContract:
    try:
        return CharacterContract(**data)
    except Exception as e:
        raise ValueError(f"CharacterContract creation failed: {e}") from e


def _fallback_character(data: dict[str, Any]) -> CharacterContract:
    return CharacterContract(
        name=data.get("name", "Protagonist"),
        description=data.get("description", "Primary viewpoint character"),
        actant_roles=data.get("actant_roles", ["subject"]),
        personality=PersonalityProfile(
            openness=data.get("personality", {}).get("openness", 7),
            conscientiousness=data.get("personality", {}).get("conscientiousness", 6),
            extraversion=data.get("personality", {}).get("extraversion", 5),
            agreeableness=data.get("personality", {}).get("agreeableness", 6),
            neuroticism=data.get("personality", {}).get("neuroticism", 4),
        ),
        core_desires=data.get("core_desires", ["freedom", "belonging"]),
        core_fears=data.get("core_fears", ["captivity", "isolation"]),
        values={"primary": data.get("values", {}).get("primary", "self_direction")},
        attachment_pattern=data.get("attachment_pattern"),
        emotional_baseline_emotion=data.get("emotional_baseline_emotion"),
        goal_polarity=data.get("goal_polarity", "attain"),
        wound_types=data.get("wound_types", []),
        need_types=data.get("need_types", []),
    )


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

        char_datas: list[dict[str, Any]] = []

        contracts_data = result.get("contracts_data")
        if isinstance(contracts_data, list) and contracts_data:
            char_datas = contracts_data
        else:
            contract_data = result.get("contract_data")
            if contract_data and contract_data.get("name"):
                char_datas = [contract_data]

        if not char_datas:
            char_datas = [{}]

        committed_ids: list[str] = []
        first = True
        for data in char_datas:
            try:
                character = _build_character(data)
            except Exception as e:
                self.log("warning", f"LLM contract_data invalid, using fallback: {e}")
                character = _fallback_character(data)
            cid = self.write_contract("character", character)
            committed_ids.append(cid)

            if first:
                story = self.list_contracts("story")[0]
                story.subject_id = cid
                self.write_contract("story", story)
                first = False

        return AgentResult(
            success=True,
            message=result.get("message", f"{len(committed_ids)} character(s) drafted"),
            artifacts=committed_ids,
            errors=result.get("errors", []),
        )

    def _refine_arcs(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "Character arcs refined"),
            errors=result.get("errors", []),
        )
