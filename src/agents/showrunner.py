"""Showrunner — top-level controller, creative authority, final approver."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class Showrunner(BaseAgent):
    """Top-level AI controller. Owns creative vision, canon, and final decisions."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="showrunner", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        if step_id in ("approve_premise",):
            return ["story", "character"]
        if step_id in ("approve_structure",):
            return ["story", "character", "theme"]
        if step_id in ("approve_episodes",):
            return ["story", "episode", "chapter"]
        return ["story"]

    def execute(self, context: AgentContext) -> AgentResult:
        self.log("info", f"Executing workflow step: {context.step_id}")

        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )

        if context.step_id == "review_brief":
            return self._review_brief(context)
        if context.step_id == "approve_brief":
            return self._approve_brief(context)
        if context.step_id == "approve_premise":
            return self._approve_premise(context)
        if context.step_id == "approve_structure":
            return self._approve_structure(context)
        if context.step_id == "approve_episodes":
            return self._approve_episodes(context)
        if context.step_id == "assemble_draft":
            return self._assemble_draft(context)
        if context.step_id == "approve_final":
            return self._approve_final(context)

        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _review_brief(self, context: AgentContext) -> AgentResult:
        stories = self.list_contracts("story")
        story = stories[0]
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", ""),
            errors=result.get("errors", []),
        )

    def _approve_brief(self, context: AgentContext) -> AgentResult:
        story = self.list_contracts("story")[0]
        if not story.premise:
            return AgentResult(success=False, errors=["Story has no premise"])
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", ""),
            artifacts=[str(story.id)] if result.get("success") else [],
            errors=result.get("errors", []),
        )

    def _approve_premise(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        story = self.list_contracts("story")[0]
        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", ""),
            artifacts=[str(story.id)] if result.get("success") else [],
            errors=result.get("errors", []),
        )

    def _approve_structure(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Structure approved"),
            errors=result.get("errors", []),
        )

    def _approve_episodes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Episode structure approved"),
            errors=result.get("errors", []),
        )

    def _assemble_draft(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Draft assembled"),
            errors=result.get("errors", []),
        )

    def _approve_final(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Final version approved"),
            errors=result.get("errors", []),
        )
