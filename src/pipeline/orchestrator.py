"""Pipeline orchestration — runs the 8-stage workflow sequence.

The orchestrator is the entry point. It instantiates all agents,
creates the Director, and runs the pipeline from brief to final draft.
"""

from __future__ import annotations

from logging import Logger
from typing import Any

from src.agents.base import BaseAgent
from src.agents.chapter_planner import ChapterPlanner
from src.agents.character_architect import CharacterArchitect
from src.agents.character_simulator import CharacterSimulator
from src.agents.continuity_editor import ContinuityEditor
from src.agents.copy_editor import CopyEditor
from src.agents.critic import Critic
from src.agents.developmental_editor import DevelopmentalEditor
from src.agents.dialogue_specialist import DialogueSpecialist
from src.agents.director import Director
from src.agents.line_editor import LineEditor
from src.agents.outline_planner import OutlinePlanner
from src.agents.proofreader import Proofreader
from src.agents.revision_agent import RevisionAgent
from src.agents.scene_writer import SceneWriter
from src.agents.script_editor import ScriptEditor
from src.agents.showrunner import Showrunner
from src.agents.structuralist import Structuralist
from src.agents.theme_specialist import ThemeSpecialist
from src.agents.world_researcher import WorldResearcher
from src.agents.worldbuilder import Worldbuilder
from src.agents.store import ContractStore, get_store
from src.engine.config import get_settings


def default_agent_registry(
    store: ContractStore | None = None,
    logger: Logger | None = None,
) -> dict[str, BaseAgent]:
    """Create the full 20-agent registry with default instances."""
    common = {"store": store, "logger": logger}
    return {
        "showrunner": Showrunner(**common),
        "script_editor": ScriptEditor(**common),
        "theme_specialist": ThemeSpecialist(**common),
        "structuralist": Structuralist(**common),
        "character_architect": CharacterArchitect(**common),
        "character_simulator": CharacterSimulator(**common),
        "dialogue_specialist": DialogueSpecialist(**common),
        "world_researcher": WorldResearcher(**common),
        "worldbuilder": Worldbuilder(**common),
        "outline_planner": OutlinePlanner(**common),
        "chapter_planner": ChapterPlanner(**common),
        "scene_writer": SceneWriter(**common),
        "continuity_editor": ContinuityEditor(**common),
        "critic": Critic(**common),
        "developmental_editor": DevelopmentalEditor(**common),
        "line_editor": LineEditor(**common),
        "copy_editor": CopyEditor(**common),
        "proofreader": Proofreader(**common),
        "revision_agent": RevisionAgent(**common),
    }


class PipelineOrchestrator:
    """Top-level entry point. Manages the full 8-workflow pipeline execution."""

    def __init__(
        self,
        agents: dict[str, BaseAgent] | None = None,
        store: ContractStore | None = None,
        logger: Logger | None = None,
    ) -> None:
        self.store = store or get_store()
        self.logger = logger
        self.agents = agents or default_agent_registry(self.store, self.logger)
        self.director = Director(self.agents, self.store, self.logger)

    def run(self) -> dict[str, list[Any]]:
        self._log("Pipeline started")
        results = self.director.run_full_pipeline()
        self._log(f"Pipeline complete — {len(results)} workflows executed")
        return results

    def run_workflow(self, workflow_id: str) -> list[Any]:
        self._log(f"Running single workflow: {workflow_id}")
        return self.director.run_workflow(workflow_id)

    def _log(self, message: str) -> None:
        if self.logger:
            self.logger.info(f"[PipelineOrchestrator] {message}")
