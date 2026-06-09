"""Chapter Planner — divides episodes into chapter contracts."""

from __future__ import annotations

from uuid import UUID
from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import ChapterContract


class ChapterPlanner(BaseAgent):
    """Breaks episodes into chapters with arcs, word counts, and scene goals."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="chapter_planner", **kwargs)

    def get_prerequisites(self, step_id: str) -> list[str]:
        return ["episode"]

    def execute(self, context: AgentContext) -> AgentResult:
        missing = self.check_prerequisites(context.step_id)
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing prerequisites: {missing} — go back"],
            )
        if context.step_id == "divide_episodes":
            return self._divide_episodes(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _normalize_conflict_type(self, raw: str) -> str:
        if not isinstance(raw, str):
            return "interpersonal"
        valid = {"internal", "interpersonal", "institutional", "environmental", "epistemic", "metaphysical", "systemic"}
        lower = raw.lower().replace(" ", "_")
        return lower if lower in valid else "interpersonal"

    def _divide_episodes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        contracts_data = result.get("contracts_data")
        if contracts_data:
            artifacts = []
            for ch_data in contracts_data:
                try:
                    raw_ids = ch_data.get("narrative_programs_active", [])
                    narrative_programs_active: list[Any] = []
                    for pid in (raw_ids if isinstance(raw_ids, list) else []):
                        try:
                            narrative_programs_active.append(UUID(str(pid)))
                        except Exception:
                            self.log("warning", f"Invalid narrative program ID: {pid}")

                    ch = ChapterContract(
                        episode_id=ch_data.get("episode_id"),
                        sequence_number=ch_data.get("sequence_number", 0),
                        title=ch_data.get("title", f"Chapter {ch_data.get('sequence_number', 0) + 1}"),
                        summary=ch_data.get("summary", ""),
                        chapter_arc_opening=ch_data.get("chapter_arc_opening", ""),
                        chapter_arc_closing=ch_data.get("chapter_arc_closing", ""),
                        primary_conflict_type=self._normalize_conflict_type(ch_data.get("primary_conflict_type", "interpersonal")),
                        word_count_target=ch_data.get("word_count_target", 2500),
                        narrative_programs_active=narrative_programs_active,
                    )
                    cid = self.write_contract("chapter", ch)
                    artifacts.append(cid)
                except Exception:
                    self.log("warning", "Invalid chapter from LLM, skipping")
            if artifacts:
                return AgentResult(
                    success=True,
                    message=f"Created {len(artifacts)} chapters from LLM",
                    artifacts=artifacts,
                )
        episodes = self.list_contracts("episode")
        artifacts = []
        for ep in episodes:
            for i in range(3):
                ch = ChapterContract(
                    episode_id=ep.id,
                    sequence_number=i,
                    title=f"Chapter {i + 1}",
                    word_count_target=2500,
                )
                cid = self.write_contract("chapter", ch)
                artifacts.append(cid)
        return AgentResult(
            success=True,
            message=f"Created {len(artifacts)} chapters for {len(episodes)} episodes",
            artifacts=artifacts,
        )
