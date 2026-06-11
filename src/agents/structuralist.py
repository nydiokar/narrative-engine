"""Structuralist — Greimas/Propp analysis, fabula construction."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import FabulaChain, NarrativeProgramRef
from src.engine.fabula.coherence import FabulaCoherenceEngine


class Structuralist(BaseAgent):
    """Applies Greimasian and Proppian analysis to construct and validate fabula."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="structuralist", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        if step_id == "analyze_premise":
            return ["story"]
        if step_id in ("build_fabula", "check_constraints"):
            return ["story", "character"]
        return ["story"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )

        if context.step_id == "analyze_premise":
            return self._analyze_premise(context)
        if context.step_id == "select_backbone":
            return self._select_backbone(context)
        if context.step_id == "build_fabula":
            return self._build_fabula(context)
        if context.step_id == "check_constraints":
            return self._check_constraints(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _analyze_premise(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        story = self.list_contracts("story")[0]

        # If LLM returned actantial data, update the story contract
        contract_data = result.get("contract_data")
        if contract_data and isinstance(contract_data, dict):
            for field in ("subject_id", "object_of_value_id", "object_of_value_description", "sender_id", "receiver_id"):
                if field in contract_data:
                    setattr(story, field, contract_data[field])
            self.write_contract("story", story)

        return AgentResult(
            success=result.get("success", False) if not result.get("contract_data") else True,
            message=result.get("message", "Premise analyzed"),
            errors=result.get("errors", []),
        )

    def _select_backbone(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "Backbone grammar selected"),
            errors=result.get("errors", []),
        )

    def _build_fabula(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)

        # Persist fabula data to the story contract so downstream steps can see it
        contract_data = result.get("contract_data")
        if contract_data and isinstance(contract_data, dict):
            try:
                stories = self.list_contracts("story")
                if stories:
                    story = stories[0]
                    fabula_data = contract_data.get("fabula", {})
                    if fabula_data:
                        story.fabula = FabulaChain(**fabula_data)
                    nps = contract_data.get("narrative_programs", [])
                    if nps:
                        story.narrative_programs = [NarrativeProgramRef(**np) for np in nps]
                    self.write_contract("story", story)
            except Exception as e:
                self.log("warning", f"Failed to persist fabula data: {e}")

        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "Fabula constructed"),
            errors=result.get("errors", []),
        )

    def _check_constraints(self, context: AgentContext) -> AgentResult:
        scenes = self.list_contracts("scene")
        scenes_data = [s.model_dump(mode="json") for s in scenes if hasattr(s, "model_dump")]
        episodes = self.list_contracts("episode")
        episodes_data = [e.model_dump(mode="json") for e in episodes if hasattr(e, "model_dump")]
        report = FabulaCoherenceEngine.run_all_checks(events=[], scenes=scenes_data, episodes=episodes_data)
        if report.passed:
            return AgentResult(success=True, message="All fabula constraints satisfied")
        return AgentResult(
            success=False,
            message=report.summary,
            errors=[c.name for c in report.checks if not c.passed],
        )
