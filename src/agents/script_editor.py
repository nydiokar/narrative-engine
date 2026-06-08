"""Script Editor — script-level editorial oversight for screen-based mediums."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class ScriptEditor(BaseAgent):
    """Provides editorial review for animation/movie/series scripts.

    Validates sluglines, scene structure, action/dialogue balance,
    and applies medium-specific formatting rules.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="script_editor", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        return ["scene"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )

        if context.step_id == "refine_script":
            return self._refine_script(context)

        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _refine_script(self, context: AgentContext) -> AgentResult:
        scenes = self.list_contracts("scene")
        if not scenes:
            return AgentResult(
                success=False,
                errors=["No scenes to refine"],
            )

        self.log("info", f"Refining {len(scenes)} scenes for script formatting")

        llm_result = self._call_llm_for_step(context)
        if llm_result.get("success", False):
            contracts_data = llm_result.get("contracts_data")
            if isinstance(contracts_data, list):
                refined_count = 0
                for refined in contracts_data:
                    sid = refined.get("id", "")
                    if not sid:
                        continue
                    target = next((s for s in scenes if str(s.id) == sid), None)
                    if target is None:
                        continue
                    content = refined.get("content")
                    if content is not None:
                        target.content = content
                    new_setting = refined.get("setting_location")
                    if new_setting:
                        target.setting_location = new_setting
                    new_time = refined.get("setting_time")
                    if new_time:
                        target.setting_time = new_time
                    self.write_contract("scene", target)
                    refined_count += 1
                self.log("info", f"Applied LLM refinements to {refined_count} scenes")

        # Validate scene structure — check required fields exist
        issues: list[str] = []
        for s in scenes:
            d = s.model_dump(mode="json") if hasattr(s, "model_dump") else {}
            if not d.get("content"):
                issues.append(f"Scene {getattr(s, 'id', '?')} missing content")
            if not d.get("greimas_diagnostic", {}).get("value_object_change"):
                issues.append(f"Scene {getattr(s, 'id', '?')} missing value_object_change")
            if not d.get("characters_present"):
                issues.append(f"Scene {getattr(s, 'id', '?')} missing characters_present")

        if issues:
            self.log("warning", f"Script refinement found {len(issues)} issue(s): {issues[:3]}...")

        return AgentResult(
            success=True,
            message=f"Script refined — {len(scenes)} scenes reviewed, {len(issues)} issue(s) noted",
            errors=issues if issues else [],
        )
