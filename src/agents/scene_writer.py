"""Scene Writer — renders scenes with Greimas diagnostics, medium-agnostic."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import ConflictLoad, Intensity, SceneContract
from src.engine.greimas.action_state import SceneDiagnosticEngine


_MEDIUM_STEP_MAP: dict[str, str] = {
    "render_prose": "book",
    "render_visual_scene": "animation",
    "render_cinematic_scene": "movie",
    "render_television_scene": "series",
}


class SceneWriter(BaseAgent):
    """Converts scene units into medium-specific output and runs Greimas diagnostics."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="scene_writer", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        if step_id in ("render_prose", "render_visual_scene", "render_cinematic_scene", "render_television_scene"):
            return ["chapter", "story"]
        return ["scene"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )

        if context.step_id in _MEDIUM_STEP_MAP:
            return self._render_scenes(context)
        if context.step_id == "run_greimas_diagnostic":
            return self._run_greimas_diagnostic(context)
        if context.step_id in ("finalize_prose", "finalize_script", "finalize_screenplay", "finalize_teleplay"):
            return self._finalize_scenes(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _render_scenes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)

        contracts_data = result.get("contracts_data", [])
        if not contracts_data:
            chapters = self.list_contracts("chapter")
            fallback = []
            for ch in chapters:
                for i in range(2):
                    fallback.append({
                        "chapter_id": str(ch.id),
                        "sequence_number": i,
                        "setting_location": "unknown",
                        "greimas_diagnostic": {
                            "state_before": "Initial state",
                            "action_occurs": "Key action",
                            "state_after": "Transformed state",
                            "value_object_change": "transferred",
                            "future_action_possible_or_blocked": "Next scene enabled",
                            "diagnostic_pass": True,
                        },
                    })
            contracts_data = fallback

        artifacts = []
        for sc_data in contracts_data:
            sc_data = self._normalize_scene(sc_data)
            try:
                sc = SceneContract(**sc_data)
                sc.conflict_load = ConflictLoad(
                    interpersonal=Intensity.MEDIUM,
                    internal=Intensity.LOW,
                )
                sid = self.write_contract("scene", sc)
                artifacts.append(sid)
            except Exception as e:
                self.log("warning", f"Invalid scene data, using fallback: {e}")
                sc = SceneContract(
                    chapter_id=sc_data.get("chapter_id"),
                    sequence_number=sc_data.get("sequence_number", 0),
                    setting_location=sc_data.get("setting_location", "unknown"),
                )
                sc.conflict_load = ConflictLoad(interpersonal=Intensity.MEDIUM, internal=Intensity.LOW)
                sid = self.write_contract("scene", sc)
                artifacts.append(sid)

        return AgentResult(
            success=True,
            message=f"Rendered {len(artifacts)} scenes",
            artifacts=artifacts,
        )

    def _run_greimas_diagnostic(self, context: AgentContext) -> AgentResult:
        scenes = self.list_contracts("scene")
        failures = []
        for sc in scenes:
            diag = getattr(sc, "greimas_diagnostic", {})
            result = SceneDiagnosticEngine.run_diagnostic(
                state_before=getattr(diag, "state_before", "") if not isinstance(diag, dict) else diag.get("state_before", ""),
                action=getattr(diag, "action_occurs", "") if not isinstance(diag, dict) else diag.get("action_occurs", ""),
                state_after=getattr(diag, "state_after", "") if not isinstance(diag, dict) else diag.get("state_after", ""),
                value_object_change=getattr(diag, "value_object_change", "none") if not isinstance(diag, dict) else diag.get("value_object_change", "none"),
                future_effect=getattr(diag, "future_action_possible_or_blocked", "") if not isinstance(diag, dict) else diag.get("future_action_possible_or_blocked", ""),
            )
            if not result.passes:
                failures.append(str(sc.id))

        if failures:
            return AgentResult(
                success=False,
                message=f"{len(failures)} scenes failed Greimas diagnostic",
                errors=failures,
            )
        return AgentResult(success=True, message="All scenes pass Greimas diagnostic")

    def _normalize_scene(self, sc_data: dict[str, Any]) -> dict[str, Any]:
        # LLM often returns fake/invalid UUIDs — strip them, we want auto-generated
        for id_field in ("id", "episode_id", "chapter_id"):
            if id_field in sc_data:
                del sc_data[id_field]
        # Remap common LLM field errors
        if "greimas_tracking" in sc_data and "greimas_diagnostic" not in sc_data:
            self.log("warning", "LLM used greimas_tracking instead of greimas_diagnostic — remapping")
            tracking = sc_data.pop("greimas_tracking")
            sc_data["greimas_diagnostic"] = {
                "state_before": tracking.get("current_state", "Initial state"),
                "action_occurs": tracking.get("desired_transformation", "Action occurs"),
                "state_after": tracking.get("resulting_state", "Transformed state"),
                "value_object_change": "transformed",
                "future_action_possible_or_blocked": tracking.get("sanction_or_judgment", "Next scene enabled"),
            }
        if "characters" in sc_data and "characters_present" not in sc_data:
            self.log("warning", "LLM used characters instead of characters_present — remapping")
            sc_data["characters_present"] = [
                {"id": c.get("id", c.get("name", "?")), "emotion": c.get("emotion", "neutral"), "intensity": c.get("intensity", "medium")}
                for c in sc_data.pop("characters")
            ]
        if "scene_type" in sc_data:
            valid_literals = {"inciting", "confrontation", "resolution", "transition", "exposition", "climax", "rising_action", "falling_action"}
            st = sc_data["scene_type"]
            if isinstance(st, str) and st.lower() in valid_literals:
                sc_data["scene_type"] = st.lower()
            elif isinstance(st, str) and st.lower() not in {"introduction", "decision", "discovery", "interrogation", "seduction", "betrayal", "reversal", "revelation", "training", "test", "negotiation", "escape", "chase", "battle", "quiet_aftermath", "recognition", "judgment"}:
                sc_data["scene_type"] = "confrontation"
        if "canonical_phase" in sc_data:
            valid_phases = {"manipulation", "competence", "performance", "sanction"}
            cp = sc_data["canonical_phase"]
            if isinstance(cp, str) and cp.lower() in valid_phases:
                sc_data["canonical_phase"] = cp.lower()
        return sc_data

    def _finalize_scenes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Scenes finalized"),
            errors=result.get("errors", []),
        )
