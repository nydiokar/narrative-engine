"""Showrunner — top-level controller, creative authority, final approver."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent


class Showrunner(BaseAgent):
    """Top-level AI controller. Owns creative vision, canon, and final decisions."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="showrunner", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        self.log("info", f"Executing workflow step: {context.step_id}")

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
        """Review the premise viability (workflow 01 step 1)."""
        stories = self.list_contracts("story")
        if not stories:
            return AgentResult(success=False, errors=["No story contract to review"])
        story = stories[0]
        has_premise = bool(story.premise) if hasattr(story, "premise") else False
        if not has_premise:
            return AgentResult(success=False, errors=["Story premise is empty — cannot proceed"])
        return AgentResult(
            success=True,
            message=f"Brief reviewed for '{getattr(story, 'title', 'untitled')}' — viable",
        )

    def _approve_brief(self, context: AgentContext) -> AgentResult:
        stories = self.list_contracts("story")
        if not stories:
            return AgentResult(success=False, errors=["No story contract found"])
        story = stories[0]
        has_premise = bool(story.premise) if hasattr(story, "premise") else False
        if not has_premise:
            return AgentResult(success=False, errors=["Story has no premise"])
        return AgentResult(
            success=True,
            message=f"Brief approved for '{getattr(story, 'title', 'untitled')}'",
            artifacts=[str(story.id)],
        )

    def _approve_premise(self, context: AgentContext) -> AgentResult:
        stories = self.list_contracts("story")
        if not stories:
            return AgentResult(success=False, errors=["No story contract found"])
        story = stories[0]
        has_subject = bool(getattr(story, "subject_id", ""))
        return AgentResult(
            success=has_subject,
            message="Premise approved" if has_subject else "Premise missing subject",
            artifacts=[str(story.id)],
        )

    def _approve_structure(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Structure approved")

    def _approve_episodes(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Episode structure approved")

    def _assemble_draft(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Draft assembled")

    def _approve_final(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Final version approved")
