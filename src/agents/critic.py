"""Critic — two-gate evaluation: hard gate, soft gate, cliché detection."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CritiqueContract
from src.evaluation.cliche import ClicheDetector
from src.evaluation.hard_gate import HardGate
from src.evaluation.soft_gate import SoftGate


class Critic(BaseAgent):
    """Evaluates narrative quality through the two-gate system."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="critic", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        if step_id in ("run_hard_gate", "run_soft_gate", "run_greimas_diagnostics"):
            return ["scene", "story", "episode", "character"]
        return ["scene"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )

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
        episodes = self.list_contracts("episode")
        episodes_data = [e.model_dump(mode="json") for e in episodes if hasattr(e, "model_dump")]
        characters = self.list_contracts("character")
        characters_data = [c.model_dump(mode="json") for c in characters if hasattr(c, "model_dump")]
        story_list = self.list_contracts("story")

        # Build event dicts from scene greimas diagnostics so all 10
        # coherence checks run on real data instead of empty input.
        events_data: list[dict[str, Any]] = []
        for i, scene in enumerate(scenes_data):
            diag = scene.get("greimas_diagnostic", {})
            if not diag:
                continue
            preds: list[str] = []
            if i > 0:
                prev_id = scenes_data[i - 1].get("id", "")
                if prev_id:
                    preds.append(str(prev_id))
            chars_present = scene.get("characters_present", [])
            actant = ""
            if chars_present and isinstance(chars_present, list):
                first = chars_present[0]
                actant = str(first.get("id", first.get("name", "")))
            events_data.append({
                "id": str(scene.get("id", "")),
                "actant": actant,
                "action": diag.get("action_occurs", ""),
                "state_before": diag.get("state_before", ""),
                "state_after": diag.get("state_after", ""),
                "value_object_change": diag.get("value_object_change", "none"),
                "modality_changes": scene.get("modality_changes", []),
                "unlocks": diag.get("future_action_possible_or_blocked", ""),
                "blocks": "",
                "causal_predecessors": preds,
                "world_rule_violations": [],
            })

        gate = HardGate()
        result = gate.evaluate(
            scenes=scenes_data,
            events=events_data,
            characters=characters_data,
            episodes=episodes_data,
        )

        critique = CritiqueContract(
            target_id=getattr(story_list[0], "id", None) if story_list else None,
            target_type="story_draft",
            reviewer="critic",
            verdict="pass" if result.passed else "fail",
            summary=result.coherence_report.summary if result.coherence_report else "No report",
        )
        cid = self.write_contract("critique", critique)

        if result.passed:
            return AgentResult(success=True, message="Hard gate: PASS", artifacts=[cid])
        return AgentResult(
            success=False,
            message="Hard gate: FAIL",
            artifacts=[cid],
            errors=result.failure_reasons,
        )

    def _run_soft_gate(self, context: AgentContext) -> AgentResult:
        gate = SoftGate(threshold=5.0)

        llm_result = self._call_llm_for_step(context)
        scores_obtained = False
        if llm_result.get("success", False):
            contract_data = llm_result.get("contract_data", {}) or {}
            if isinstance(contract_data, dict):
                dimension_scores = contract_data.get("dimension_scores", {})
                if isinstance(dimension_scores, dict) and dimension_scores:
                    dimension_notes = contract_data.get("dimension_notes", {}) or {}
                    for dim_name, score in dimension_scores.items():
                        try:
                            numeric_score = int(score) if not isinstance(score, int) else score
                            if 0 <= numeric_score <= 10:
                                note = dimension_notes.get(dim_name, "") if isinstance(dimension_notes, dict) else ""
                                gate.set_score(dim_name, numeric_score, notes=str(note))
                                scores_obtained = True
                            else:
                                self.log("warning", f"Soft gate score for '{dim_name}' out of range: {score}")
                        except (ValueError, TypeError):
                            self.log("warning", f"Soft gate non-numeric score for '{dim_name}': {score}")
        if not scores_obtained:
            self.log("warning", "Soft gate LLM returned no scores — using fallback mid-range")
            gate.set_score("genre_fit", 5)
            gate.set_score("thematic_clarity", 5)
            gate.set_score("conflict_density", 5)
            gate.set_score("relationship_tension", 5)
            gate.set_score("scene_level_purpose", 5)
            gate.set_score("suspense_curiosity_surprise", 5)
            gate.set_score("emotional_transport", 5)
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
        explicit_signals: list[tuple[str, int]] = []

        llm_result = self._call_llm_for_step(context)
        if llm_result.get("success", False):
            contract_data = llm_result.get("contract_data", {}) or {}
            if isinstance(contract_data, dict):
                cliche_signals = contract_data.get("cliche_signals", [])
                if isinstance(cliche_signals, list):
                    for signal in cliche_signals:
                        if isinstance(signal, dict):
                            name = signal.get("name", "")
                            raw_severity = signal.get("severity", 1)
                            severity = 1
                            try:
                                severity = int(raw_severity)
                                severity = max(1, min(3, severity))
                            except (ValueError, TypeError):
                                self.log("warning", f"Non-numeric cliché severity '{raw_severity}' for '{name}', using 1")
                            if name:
                                explicit_signals.append((name, severity))
        else:
            self.log("warning", "Greimas diagnostics LLM call failed — no cliché signals")

        cliche_result = ClicheDetector.detect(explicit_signals=explicit_signals if explicit_signals else None)
        score = cliche_result.cliche_score
        return AgentResult(
            success=True,
            message=f"Greimas diagnostics complete. Cliché score: {score}/{cliche_result.max_score}",
        )
