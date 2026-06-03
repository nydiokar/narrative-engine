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
        result = self._call_llm_for_step(context)
        contract_data = result.get("contract_data")
        if contract_data:
            try:
                theme = ThemeContract(
                    primary_themes=contract_data.get("primary_themes", [{"name": "freedom", "question": "What is the cost of freedom?"}]),
                    secondary_themes=contract_data.get("secondary_themes", []),
                    moral_tensions=contract_data.get("moral_tensions", []),
                    symbolic_motifs=contract_data.get("symbolic_motifs", []),
                )
                tid = self.write_contract("theme", theme)
                return AgentResult(success=True, message=result.get("message", "Themes selected"), artifacts=[tid])
            except Exception:
                self.log("warning", "LLM contract_data invalid for themes, using fallback")
        theme = ThemeContract(
            primary_themes=[{"name": "freedom", "question": "What is the cost of freedom?"}],
            moral_tensions=[{"themes": ["freedom", "security"], "conflict": "Freedom vs security"}],
        )
        tid = self.write_contract("theme", theme)
        return AgentResult(success=True, message="Themes selected", artifacts=[tid])

    def _select_genre(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        stories = self.list_contracts("story")
        if stories:
            story = stories[0]
            contract_data = result.get("contract_data", {})
            genre = GenreSelection(
                primary_bisac=contract_data.get("primary_bisac", "FIC009000"),
                secondary_bisac=contract_data.get("secondary_bisac", ["FIC009020"]),
                subgenre_notes=contract_data.get("subgenre_notes", "Epic fantasy with mythic stakes"),
            )
            story.genre = genre
            self.write_contract("story", story)
        return AgentResult(success=True, message=result.get("message", "Genre selected"))

    def _validate_thematic_fit(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        return AgentResult(
            success=result.get("success", True),
            message=result.get("message", "Themes validated against fabula"),
            errors=result.get("errors", []),
        )
