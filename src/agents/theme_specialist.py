"""Theme Specialist — theme ontology queries, genre selection, thematic validation."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import GenreSelection, ThemeContract


class ThemeSpecialist(BaseAgent):
    """Selects themes and genres, validates thematic fit in fabula."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="theme_specialist", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        return ["story"]

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id not in ("select_themes", "select_genre", "validate_thematic_fit"):
            return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )
        if context.step_id == "select_themes":
            return self._select_themes(context)
        if context.step_id == "select_genre":
            return self._select_genre(context)
        if context.step_id == "validate_thematic_fit":
            return self._validate_thematic_fit(context)

    def _validate_theme_contract(self, theme: ThemeContract) -> list[str]:
        violations: list[str] = []
        for i, pt in enumerate(theme.primary_themes):
            q = pt.get("question", "")
            if not q.endswith("?"):
                violations.append(f"primary_themes[{i}].question '{q}' must end with '?'")
        for i, mt in enumerate(theme.moral_tensions):
            ts = mt.get("themes", [])
            if len(ts) < 2:
                violations.append(f"moral_tensions[{i}].themes {ts} must contain at least 2 opposing values")
        for v in violations:
            self.log("warning", f"Theme quality violation: {v}")
        return violations

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
                self._validate_theme_contract(theme)
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
        if not result.get("success"):
            return AgentResult(success=False, errors=result.get("errors", ["LLM call failed"]))
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
            success=result.get("success", False),
            message=result.get("message", "Themes validated against fabula"),
            errors=result.get("errors", []),
        )
