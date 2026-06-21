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
        if step_id == "define_discourse":
            return ["story"]
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
        if context.step_id == "define_discourse":
            return self._define_discourse(context)
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
        if context.step_id == "assemble_script":
            return self._assemble_script(context)
        if context.step_id == "assemble_screenplay":
            return self._assemble_screenplay(context)
        if context.step_id == "assemble_teleplay":
            return self._assemble_teleplay(context)
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

    def _define_discourse(self, context: AgentContext) -> AgentResult:
        from src.contracts.models import DiscourseContract, POV, Tense

        medium = context.metadata.get("medium", "book")

        if medium in ("movie", "animation"):
            pov = POV.THIRD_OBJECTIVE
            tense = Tense.PRESENT
        elif medium == "series":
            pov = POV.THIRD_LIMITED
            tense = Tense.PRESENT
        else:
            pov = POV.THIRD_LIMITED
            tense = Tense.PAST

        discourse = DiscourseContract(
            point_of_view=pov,
            tense=tense,
        )
        did = self.write_contract("discourse", discourse)

        story = self.list_contracts("story")[0]
        story.discourse_contract_id = discourse.id
        self.write_contract("story", story)

        return AgentResult(
            success=True,
            message=f"Discourse defined: {pov.value}, {tense.value}",
            artifacts=[did, str(story.id)],
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
            success=result.get("success", False),
            message=result.get("message", "Structure review complete"),
            errors=result.get("errors", []),
        )

    def _approve_episodes(self, context: AgentContext) -> AgentResult:
        result = self._call_llm_for_step(context)
        episodes = self.list_contracts("episode")
        chapters = self.list_contracts("chapter")

        errors = []

        expected_phases = ["manipulation", "competence", "performance", "sanction"]
        episode_phases = [getattr(e, "canonical_phase", None) or getattr(e, "phase", "") for e in episodes]

        for phase in expected_phases:
            if phase not in episode_phases:
                errors.append(f"Missing episode with canonical_phase '{phase}'")

        episode_ids = {str(e.id) for e in episodes}
        for ch in chapters:
            eid = getattr(ch, "episode_id", None)
            if eid and str(eid) not in episode_ids:
                errors.append(f"Chapter '{getattr(ch, 'title', '?')}' references unknown episode {eid}")

        if errors:
            return AgentResult(
                success=False,
                message="Episode approval rejected",
                errors=errors,
            )

        return AgentResult(
            success=result.get("success", False),
            message=result.get("message", "Episode structure approved"),
            errors=result.get("errors", []),
        )

    def _assemble_draft(self, context: AgentContext) -> AgentResult:
        from pathlib import Path

        story = self.list_contracts("story")
        episodes = sorted(self.list_contracts("episode"), key=lambda e: e.sequence_number)
        chapters = self.list_contracts("chapter")
        scenes = self.list_contracts("scene")

        lines = []
        title = story[0].title if story else "Untitled"
        lines.append(f"# {title}\n")

        for ep in episodes:
            ep_chapters = [ch for ch in chapters if getattr(ch, "episode_id", None) == ep.id]
            if not ep_chapters:
                continue
            lines.append(f"\n## Episode {ep.sequence_number}: {ep.title}\n")
            for ch in ep_chapters:
                ch_scenes = [s for s in scenes if getattr(s, "chapter_id", None) == ch.id]
                ch_scenes = sorted(ch_scenes, key=lambda s: s.sequence_number)
                if not ch_scenes:
                    continue
                lines.append(f"\n### {ch.title}\n")
                for s in ch_scenes:
                    if s.content:
                        lines.append(s.content + "\n")

        draft_text = "\n".join(lines)

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        draft_path = output_dir / "draft.md"
        draft_path.write_text(draft_text, encoding="utf-8")

        char_count = len(draft_text)
        return AgentResult(
            success=True,
            message=f"Draft assembled: {char_count} chars across {len(episodes)} episodes, {len(scenes)} scenes",
            artifacts=[str(draft_path)],
        )

    def _assemble_script(self, context: AgentContext) -> AgentResult:
        from pathlib import Path

        story = self.list_contracts("story")
        episodes = sorted(self.list_contracts("episode"), key=lambda e: e.sequence_number)
        chapters = self.list_contracts("chapter")
        scenes = self.list_contracts("scene")

        lines = []
        title = story[0].title if story else "Untitled"
        lines.append(f"# {title} — Animation Script\n")

        for ep in episodes:
            ep_chapters = [ch for ch in chapters if getattr(ch, "episode_id", None) == ep.id]
            if not ep_chapters:
                continue
            lines.append(f"\n## Episode {ep.sequence_number}: {ep.title}\n")
            for ch in ep_chapters:
                ch_scenes = [s for s in scenes if getattr(s, "chapter_id", None) == ch.id]
                ch_scenes = sorted(ch_scenes, key=lambda s: s.sequence_number)
                if not ch_scenes:
                    continue
                lines.append(f"\n### {ch.title}\n")
                for s in ch_scenes:
                    if s.content:
                        lines.append(s.content + "\n")

        script_text = "\n".join(lines)

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        script_path = output_dir / "script.md"
        script_path.write_text(script_text, encoding="utf-8")

        char_count = len(script_text)
        return AgentResult(
            success=True,
            message=f"Script assembled: {char_count} chars across {len(episodes)} episodes, {len(scenes)} scenes",
            artifacts=[str(script_path)],
        )

    def _assemble_screenplay(self, context: AgentContext) -> AgentResult:
        from pathlib import Path

        story = self.list_contracts("story")
        episodes = sorted(self.list_contracts("episode"), key=lambda e: e.sequence_number)
        chapters = self.list_contracts("chapter")
        scenes = self.list_contracts("scene")

        lines = []
        title = story[0].title if story else "Untitled"
        lines.append(f"{title.upper()}\n{'=' * len(title)}\n")

        for ep in episodes:
            lines.append(f"\n{ep.title.upper()}\n{'-' * len(ep.title)}\n")
            ep_chapters = [ch for ch in chapters if getattr(ch, "episode_id", None) == ep.id]
            if not ep_chapters:
                continue
            for ch in ep_chapters:
                ch_scenes = [s for s in scenes if getattr(s, "chapter_id", None) == ch.id]
                ch_scenes = sorted(ch_scenes, key=lambda s: s.sequence_number)
                if not ch_scenes:
                    continue
                for s in ch_scenes:
                    if s.content:
                        lines.append(s.content + "\n")

        screenplay_text = "\n".join(lines)

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        screenplay_path = output_dir / "screenplay.md"
        screenplay_path.write_text(screenplay_text, encoding="utf-8")

        char_count = len(screenplay_text)
        return AgentResult(
            success=True,
            message=f"Screenplay assembled: {char_count} chars across {len(episodes)} episodes, {len(scenes)} scenes",
            artifacts=[str(screenplay_path)],
        )

    def _assemble_teleplay(self, context: AgentContext) -> AgentResult:
        from pathlib import Path

        story = self.list_contracts("story")
        episodes = sorted(self.list_contracts("episode"), key=lambda e: e.sequence_number)
        chapters = self.list_contracts("chapter")
        scenes = self.list_contracts("scene")

        lines = []
        title = story[0].title if story else "Untitled"
        lines.append(f"{title.upper()}\n{'=' * len(title)}\n")

        for ep in episodes:
            lines.append(f"\nACT {ep.sequence_number}\n{'---' * 10}\n")
            ep_chapters = [ch for ch in chapters if getattr(ch, "episode_id", None) == ep.id]
            if not ep_chapters:
                continue
            for ch in ep_chapters:
                ch_scenes = [s for s in scenes if getattr(s, "chapter_id", None) == ch.id]
                ch_scenes = sorted(ch_scenes, key=lambda s: s.sequence_number)
                if not ch_scenes:
                    continue
                for s in ch_scenes:
                    if s.content:
                        lines.append(s.content + "\n")

        teleplay_text = "\n".join(lines)

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        teleplay_path = output_dir / "teleplay.md"
        teleplay_path.write_text(teleplay_text, encoding="utf-8")

        char_count = len(teleplay_text)
        return AgentResult(
            success=True,
            message=f"Teleplay assembled: {char_count} chars across {len(episodes)} episodes, {len(scenes)} scenes",
            artifacts=[str(teleplay_path)],
        )

    def _approve_final(self, context: AgentContext) -> AgentResult:
        critiques = self.list_contracts("critique")
        if critiques:
            c = critiques[0]
            verdict = getattr(c, "verdict", "")
            if verdict == "fail":
                return AgentResult(
                    success=False,
                    errors=[f"Final approval rejected — hard gate verdict is 'fail'"],
                )

        expected_types = ["story", "theme", "character", "episode", "chapter", "scene", "critique", "discourse"]
        missing = [t for t in expected_types if not self.list_contracts(t)]
        if missing:
            return AgentResult(
                success=False,
                errors=[f"Missing contracts: {missing}"],
            )

        return AgentResult(
            success=True,
            message="Final version approved — all contracts present, hard gate passed",
            artifacts=[],
        )
