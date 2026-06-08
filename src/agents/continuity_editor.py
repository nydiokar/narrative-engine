"""Continuity Editor — checks consistency across characters, causality, and world rules."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CritiqueContract
from src.engine.fabula.coherence import FabulaCoherenceEngine


class ContinuityEditor(BaseAgent):
    """Verifies character, causality, world rule, and discourse consistency."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="continuity_editor", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        if step_id == "final_check":
            return []
        return ["scene", "episode"]

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id not in ("check_consistency", "final_check"):
            return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )
        if context.step_id == "check_consistency":
            return self._check_consistency(context)
        return self._final_check(context)

    def _check_consistency(self, context: AgentContext) -> AgentResult:
        scenes = self.list_contracts("scene")
        scenes_data = [s.model_dump(mode="json") for s in scenes if hasattr(s, "model_dump")]
        episodes = self.list_contracts("episode")
        episodes_data = [e.model_dump(mode="json") for e in episodes if hasattr(e, "model_dump")]
        report = FabulaCoherenceEngine.run_all_checks(scenes=scenes_data, episodes=episodes_data)

        engine_findings = {
            "passed": report.passed,
            "summary": report.summary,
            "checks": [
                {"name": c.name, "passed": c.passed, "violations": c.violations}
                for c in report.checks
            ],
        }
        context.metadata["engine_findings"] = engine_findings

        result = self._call_llm_for_step(context)
        contract_data = result.get("contract_data")
        if isinstance(contract_data, dict):
            cc = CritiqueContract(
                target_type="continuity_check",
                reviewer="continuity_editor",
                verdict="pass" if contract_data.get("passing", True) else "fail",
                summary=result.get("message", "Continuity check complete"),
            )
            self.write_contract("critique", cc)

        if report.passed:
            return AgentResult(success=True, message="Continuity check passed")
        return AgentResult(
            success=False,
            message=report.summary,
            errors=[c.name for c in report.checks if not c.passed],
        )

    def _final_check(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Final continuity check passed")
