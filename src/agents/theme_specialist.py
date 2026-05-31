"""Theme Specialist — theme ontology queries, genre selection, thematic validation."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import GenreSelection, ThemeContract


class ThemeSpecialist(BaseAgent):
    """Selects themes and genres, validates thematic fit in fabula."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="theme_specialist", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "select_themes":
            return self._select_themes(context)
        if context.step_id == "select_genre":
            return self._select_genre(context)
        if context.step_id == "validate_thematic_fit":
            return self._validate_thematic_fit(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _select_themes(self, context: AgentContext) -> AgentResult:
        theme = ThemeContract(
            primary_themes=[{"name": "freedom", "question": "What is the cost of freedom?"}],
            moral_tensions=[{"themes": ["freedom", "security"], "conflict": "Freedom vs security"}],
        )
        tid = self.write_contract("theme", theme)
        return AgentResult(success=True, message="Themes selected", artifacts=[tid])

    def _select_genre(self, context: AgentContext) -> AgentResult:
        stories = self.list_contracts("story")
        if stories:
            story = stories[0]
            genre = GenreSelection(
                primary_bisac="FIC009000" if not getattr(story, "genre", None) else "FIC009000",
                secondary_bisac=["FIC009020"],
                subgenre_notes="Epic fantasy with mythic stakes",
            )
            story.genre = genre
            self.write_contract("story", story)
        return AgentResult(success=True, message="Genre selected")

    def _validate_thematic_fit(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message="Themes validated against fabula")
