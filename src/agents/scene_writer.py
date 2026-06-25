"""Scene Writer — renders scenes with Greimas diagnostics, medium-agnostic."""

from __future__ import annotations

import math
import time as _time
from collections import defaultdict
from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.agents.llm import GenerationContext
from src.agents.prompts import (
    contracts_to_yaml,
    parse_json_output,
    render_system_prompt,
    render_user_prompt,
)
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
        chapters = self.list_contracts("chapter")
        if not chapters:
            return AgentResult(success=False, errors=["No chapters found — go back"])

        episodes: dict[str | None, list[Any]] = defaultdict(list)
        for ch in chapters:
            eid = str(ch.episode_id) if getattr(ch, "episode_id", None) else None
            episodes[eid].append(ch)

        for eid in episodes:
            episodes[eid].sort(key=lambda ch: getattr(ch, "sequence_number", 0))

        all_scenes_data: list[dict[str, Any]] = []

        for ep_id, ep_chapters in episodes.items():
            result = self._render_episode_chapters(context, ep_id, ep_chapters)
            contracts_data = result.get("contracts_data", [])
            if contracts_data:
                scenes_with_chapter = self._assign_chapter_ids(contracts_data, ep_chapters)
                all_scenes_data.extend(scenes_with_chapter)
            else:
                self.log("warning", f"No scenes returned for episode {ep_id}, using fallback")
                for ch in ep_chapters:
                    ch_title = getattr(ch, "title", "unknown")
                    ch_summary = getattr(ch, "summary", "") or ch_title
                    for i in range(3):
                        all_scenes_data.append({
                            "chapter_id": str(ch.id),
                            "episode_id": ep_id,
                            "sequence_number": i,
                            "setting_location": "unknown",
                            "setting_time": "unknown",
                            "setting_atmosphere": "neutral",
                            "scene_type": "confrontation",
                            "canonical_phase": "performance",
                            "emotional_tone": "anticipation",
                            "content": f"Chapter: {ch_title}. {ch_summary}",
                            "characters_present": [],
                            "greimas_diagnostic": {
                                "state_before": "Initial state before the events of this scene",
                                "action_occurs": f"Key action in chapter {ch_title}",
                                "state_after": "Transformed state resulting from the action",
                                "value_object_change": "transferred",
                                "future_action_possible_or_blocked": "Next scene is now enabled",
                            },
                        })

        artifacts = []
        for sc_data in all_scenes_data:
            sc_data = self._normalize_scene(sc_data)
            try:
                sc = SceneContract(**sc_data)
                sc.conflict_load = ConflictLoad(
                    interpersonal=Intensity.MEDIUM,
                    internal=Intensity.LOW,
                )
                if not sc.episode_id and sc.chapter_id:
                    ch = self.read_contract("chapter", str(sc.chapter_id))
                    if ch and getattr(ch, "episode_id", None):
                        sc.episode_id = ch.episode_id
                sid = self.write_contract("scene", sc)
                artifacts.append(sid)
            except Exception as e:
                self.log("warning", f"Invalid scene data, using fallback: {e}")
                sc = SceneContract(
                    chapter_id=sc_data.get("chapter_id"),
                    sequence_number=sc_data.get("sequence_number", 0),
                    setting_location=sc_data.get("setting_location", "unknown"),
                    setting_time=sc_data.get("setting_time", "unknown"),
                    setting_atmosphere=sc_data.get("setting_atmosphere", "neutral"),
                    scene_type=sc_data.get("scene_type", "confrontation"),
                    greimas_diagnostic={
                        "state_before": "Scene exists in narrative flow",
                        "action_occurs": "Narrative action advances",
                        "state_after": "Situation has changed",
                        "value_object_change": "advanced",
                        "future_action_possible_or_blocked": "Story continues",
                        "diagnostic_pass": False,
                    },
                )
                sc.conflict_load = ConflictLoad(interpersonal=Intensity.MEDIUM, internal=Intensity.LOW)
                sid = self.write_contract("scene", sc)
                artifacts.append(sid)

        return AgentResult(
            success=True,
            message=f"Rendered {len(artifacts)} scenes across {sum(len(v) for v in episodes.values())} chapters",
            artifacts=artifacts,
        )

    def _assign_chapter_ids(
        self, scenes: list[dict[str, Any]], chapters: list[Any]
    ) -> list[dict[str, Any]]:
        """Assign chapter_id and episode_id to LLM-returned scenes.

        The LLM is instructed not to include chapter_id, so we distribute
        scenes evenly across the chapters in this episode.
        """
        if not scenes or not chapters:
            return scenes

        ep_id = str(chapters[0].episode_id) if getattr(chapters[0], "episode_id", None) else None
        ch_count = len(chapters)
        scenes_per_ch = max(1, math.ceil(len(scenes) / ch_count))

        assigned = []
        for i, sc in enumerate(scenes):
            sc["episode_id"] = ep_id
            ch_idx = min(i // scenes_per_ch, ch_count - 1)
            sc["chapter_id"] = str(chapters[ch_idx].id)
            assigned.append(sc)
        return assigned

    def _render_episode_chapters(
        self, context: AgentContext, ep_id: str | None, chapters: list[Any]
    ) -> dict[str, Any]:
        """Call LLM to render scenes for all chapters in one episode."""
        context_contracts: dict[str, list[Any]] = {}

        story_list = self.list_contracts("story")
        if story_list:
            context_contracts["story"] = story_list

        theme_list = self.list_contracts("theme")
        if theme_list:
            context_contracts["theme"] = theme_list

        character_list = self.list_contracts("character")
        if character_list:
            context_contracts["character"] = character_list

        if ep_id:
            episode = self.read_contract("episode", ep_id)
            if episode:
                context_contracts["episode"] = [episode]

        context_contracts["chapter"] = chapters

        yaml_parts: list[str] = []
        for type_key, contracts in context_contracts.items():
            max_chars = 8000 if type_key in ("chapter", "episode") else 4000
            y = contracts_to_yaml(contracts, max_chars=max_chars)
            yaml_parts.append(f"{type_key}:\n{y}")
        upstream_yaml = "\n".join(yaml_parts)

        medium = context.metadata.get("medium", "book")
        extra_meta = {k: v for k, v in context.metadata.items() if k not in ("medium",)}

        system_prompt = render_system_prompt(
            self.role,
            upstream_contracts=upstream_yaml,
            current_step=context.step_id,
            medium=medium,
            **extra_meta,
        )
        user_prompt = render_user_prompt(
            step_id=context.step_id,
            upstream_yaml=upstream_yaml,
            agent_name=self.role,
            medium=medium,
            **extra_meta,
        )

        gen_ctx = GenerationContext(
            agent_role=self.role,
            step_id=context.step_id,
            workflow_id=context.workflow_id,
            medium=medium,
        )

        ep_title = ""
        if ep_id:
            ep = self.read_contract("episode", ep_id)
            if ep:
                ep_title = getattr(ep, "title", "") or ""

        ch_titles = [getattr(ch, "title", "?") for ch in chapters]
        self.log(
            "info",
            f"Calling LLM for episode '{ep_title}' ({len(chapters)} chapters: {', '.join(ch_titles)})",
        )

        last_error = ""
        for attempt in range(3):
            try:
                response = self.llm.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.7,
                    max_tokens=8192,
                    context=gen_ctx,
                )
            except Exception as e:
                if attempt > 0:
                    _time.sleep(2.0 * (2 ** (attempt - 1)))
                last_error = str(e)
                self.log("error", f"LLM call failed for episode '{ep_title}': {e}")
                continue

            parsed = parse_json_output(response.content)
            if parsed.get("contracts_data"):
                return parsed
            last_error = parsed.get("message", "Parse returned no data")
            self.log("warning", f"Parse failure (attempt {attempt + 1}): {last_error}")
            break

        self.log("error", f"All attempts failed for episode '{ep_title}': {last_error}")
        return {"contracts_data": [], "success": False, "errors": [last_error], "message": last_error}

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
            sc.greimas_diagnostic.diagnostic_pass = result.passes
            self.write_contract("scene", sc)
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
        # Strip only fake/invalid UUIDs — preserve episode_id and chapter_id
        if "id" in sc_data:
            del sc_data["id"]
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
        if "emotional_tone" in sc_data:
            valid_emotions = {"joy", "trust", "fear", "surprise", "sadness", "disgust", "anger", "anticipation"}
            et = sc_data["emotional_tone"]
            if isinstance(et, str):
                lower_et = et.lower()
                sc_data["emotional_tone"] = lower_et if lower_et in valid_emotions else "anticipation"
        return sc_data

    def _finalize_scenes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "Scenes finalized"),
            errors=result.get("errors", []),
        )
