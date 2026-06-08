"""Outline Planner — segments fabula into episodes and acts."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import CanonicalPhase, EpisodeContract, GreimasEpisodeTracking


class OutlinePlanner(BaseAgent):
    """Groups events into acts and episodes with narrative program assignments."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="outline_planner", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        return ["story", "character"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )

        if context.step_id == "segment_fabula":
            return self._segment_fabula(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _segment_fabula(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)

        contracts_data = result.get("contracts_data", [])
        if not contracts_data:
            contracts_data = self._fallback_episodes()

        artifacts = []
        for ep_data in contracts_data:
            ep_data = self._normalize_episode(ep_data)
            try:
                ep = EpisodeContract(**ep_data)
                eid = self.write_contract("episode", ep)
                artifacts.append(eid)
            except Exception as e:
                self.log("warning", f"Invalid episode data, using fallback: {e}")
                ep = EpisodeContract(
                    sequence_number=ep_data.get("sequence_number", 0),
                    title=ep_data.get("title", "Untitled Episode"),
                    summary=ep_data.get("summary", ""),
                    canonical_phase=CanonicalPhase.MANIPULATION,
                    dominant_conflict=ep_data.get("dominant_conflict", "interpersonal"),
                    greimas_tracking=GreimasEpisodeTracking(
                        subject=ep_data.get("greimas_tracking", {}).get("subject", ""),
                        object_of_value=ep_data.get("greimas_tracking", {}).get("object_of_value", ""),
                        current_state=ep_data.get("greimas_tracking", {}).get("current_state", "initial"),
                        desired_transformation=ep_data.get("greimas_tracking", {}).get("desired_transformation", "to be determined"),
                        opponent=ep_data.get("greimas_tracking", {}).get("opponent", ""),
                        opponent_value_logic=ep_data.get("greimas_tracking", {}).get("opponent_value_logic", ""),
                        helper=ep_data.get("greimas_tracking", {}).get("helper", ""),
                        action_type=ep_data.get("greimas_tracking", {}).get("action_type", ""),
                        resulting_state=ep_data.get("greimas_tracking", {}).get("resulting_state", ""),
                        sanction_or_judgment=ep_data.get("greimas_tracking", {}).get("sanction_or_judgment", ""),
                        contribution_to_whole_fabula=ep_data.get("greimas_tracking", {}).get("contribution_to_whole_fabula", ""),
                    ),
                )
                eid = self.write_contract("episode", ep)
                artifacts.append(eid)

        return AgentResult(
            success=True,
            message=f"Fabula segmented into {len(artifacts)} episodes",
            artifacts=artifacts,
        )

    def _normalize_episode(self, ep_data: dict[str, Any]) -> dict[str, Any]:
        """Fix common LLM output issues like wrong case on enum fields."""
        # Convert None values in greimas_tracking to empty strings
        gt = ep_data.get("greimas_tracking")
        if isinstance(gt, dict):
            for key in list(gt.keys()):
                if gt[key] is None:
                    gt[key] = ""
            ep_data["greimas_tracking"] = gt

        phase = ep_data.get("canonical_phase", "")
        if isinstance(phase, str):
            lower = phase.lower()
            for valid in ("manipulation", "competence", "performance", "sanction"):
                if lower == valid:
                    ep_data["canonical_phase"] = valid
                    break

        dc = ep_data.get("dominant_conflict", "")
        if isinstance(dc, str):
            valid_conflicts = {"internal", "interpersonal", "institutional", "environmental", "epistemic", "metaphysical", "systemic"}
            lower_dc = dc.lower().replace(" ", "_")
            if lower_dc in valid_conflicts:
                ep_data["dominant_conflict"] = lower_dc
            else:
                ep_data["dominant_conflict"] = "interpersonal"

        for arc_field in ("emotional_arc_opening", "emotional_arc_closing"):
            val = ep_data.get(arc_field)
            if isinstance(val, str):
                valid_emotions = {"joy", "trust", "fear", "surprise", "sadness", "disgust", "anger", "anticipation"}
                lower_val = val.lower()
                ep_data[arc_field] = lower_val if lower_val in valid_emotions else "anticipation"
        return ep_data

    def _fallback_episodes(self) -> list[dict[str, Any]]:
        fallback_phases = [
            CanonicalPhase.MANIPULATION,
            CanonicalPhase.COMPETENCE,
            CanonicalPhase.PERFORMANCE,
            CanonicalPhase.SANCTION,
        ]
        fallback = []
        for i, phase in enumerate(fallback_phases):
            fallback.append({
                "sequence_number": i,
                "title": f"Act {i + 1}",
                "summary": f"Core narrative arc segment {i + 1}",
                "canonical_phase": phase.value,
                "greimas_tracking": {
                    "subject": "",
                    "object_of_value": "",
                    "current_state": "initial",
                    "desired_transformation": "to be determined",
                    "opponent": "",
                    "opponent_value_logic": "",
                    "helper": "",
                    "action_type": "",
                    "resulting_state": "",
                    "sanction_or_judgment": "",
                    "contribution_to_whole_fabula": "",
                },
            })
        return fallback
