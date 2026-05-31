"""Chapter Planner — divides episodes into chapter contracts."""

from __future__ import annotations

from typing import Any

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.contracts.models import ChapterContract


class ChapterPlanner(BaseAgent):
    """Breaks episodes into chapters with arcs, word counts, and scene goals."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(role="chapter_planner", **kwargs)

    def execute(self, context: AgentContext) -> AgentResult:
        if context.step_id == "divide_episodes":
            return self._divide_episodes(context)
        return AgentResult(success=False, errors=[f"Unknown step: {context.step_id}"])

    def _divide_episodes(self, context: AgentContext) -> AgentResult:
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
