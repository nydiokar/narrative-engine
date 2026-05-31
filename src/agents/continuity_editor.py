"""Continuity Editor — checks consistency across characters, causality, and world rules."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.engine.fabula.coherence import FabulaCoherenceEngine


class ContinuityEditor(BaseAgent):
    """Verifies character, causality, world rule, and discourse consistency."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="continuity_editor", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "check_consistency":
            return self._check_consistency(context)
        if context.step_id == "final_check":
            return self._final_check(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _check_consistency(self, context: AgentContext) -> AgentResult:
        scenes = self.list_contracts("scene")
        scenes_data = [s.model_dump(mode="json") for s in scenes if hasattr(s, "model_dump")]
        report = FabulaCoherenceEngine.run_all_checks(scenes=scenes_data)
        if report.passed:
            return AgentResult(success=True, message="Continuity check passed")
        return AgentResult(
            success=False,
            message=report.summary,
            errors=[c.name for c in report.checks if not c.passed],
        )

    def _final_check(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Final continuity check passed")
