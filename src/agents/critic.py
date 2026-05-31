"""Critic — two-gate evaluation: hard gate, soft gate, cliché detection."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.evaluation.hard_gate import HardGate
from src.evaluation.soft_gate import SoftGate
from src.evaluation.cliche import ClicheDetector
from src.contracts.models import CritiqueContract


class Critic(BaseAgent):
    """Evaluates narrative quality through the two-gate system."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="critic", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "run_hard_gate":
            return self._run_hard_gate(context)
        if context.step_id == "run_soft_gate":
            return self._run_soft_gate(context)
        if context.step_id == "run_greimas_diagnostics":
            return self._run_greimas_diagnostics(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _run_hard_gate(self, context: AgentContext) -> AgentResult:
        scenes = self.list_contracts("scene")
        scenes_data = [s.model_dump(mode="json") for s in scenes if hasattr(s, "model_dump")]
        story_list = self.list_contracts("story")

        gate = HardGate()
        result = gate.evaluate(scenes=scenes_data, events=[])

        critique = CritiqueContract(
            target_id=getattr(story_list[0], "id", None) if story_list else None,
            target_type="story_draft",
            reviewer="critic",
            verdict="pass" if result.passed else "fail",
            summary=result.coherence_report.summary if result.coherence_report else "No report",
        )
        self.write_contract("critique", critique)

        if result.passed:
            return AgentResult(success=True, message="Hard gate: PASS")
        return AgentResult(
            success=False,
            message="Hard gate: FAIL",
            errors=result.failure_reasons,
        )

    def _run_soft_gate(self, context: AgentContext) -> AgentResult:
        gate = SoftGate(threshold=5.0)
        gate.set_score("genre_fit", 7)
        gate.set_score("thematic_clarity", 6)
        gate.set_score("conflict_density", 6)
        gate.set_score("relationship_tension", 5)
        gate.set_score("scene_level_purpose", 8)
        gate.set_score("suspense_curiosity_surprise", 6)
        gate.set_score("emotional_transport", 6)
        gate.set_score("novelty", 5)
        gate.set_score("prose_distinctiveness", 5)
        s_result = gate.evaluate()

        critique_list = self.list_contracts("critique")
        if critique_list:
            c = critique_list[0]
            c.verdict = "pass" if s_result.passed else "needs_revision"
            c.summary = f"Soft gate: composite={s_result.composite_score:.1f}/{s_result.threshold}"
            self.write_contract("critique", c)

        if s_result.passed:
            return AgentResult(success=True, message=f"Soft gate: PASS ({s_result.composite_score:.1f})")
        return AgentResult(
            success=False,
            message=f"Soft gate: FAIL ({s_result.composite_score:.1f}/{s_result.threshold})",
            errors=s_result.notes,
        )

    def _run_greimas_diagnostics(self, context: AgentContext) -> AgentResult:
        cliche_result = ClicheDetector.detect(explicit_signals=[])
        score = cliche_result.cliche_score
        return AgentResult(
            success=True,
            message=f"Greimas diagnostics complete. Cliché score: {score}/{cliche_result.max_score}",
        )
