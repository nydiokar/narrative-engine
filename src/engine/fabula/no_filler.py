"""No-Filler Rules — anti-filler checks powered by Greimas action/state diagnostics.

Every scene, event, character, and line of dialogue must serve a structural
function or be flagged for removal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NoFillerCheckResult:
    target_type: str  # scene, character, dialogue, event, action
    target_id: str
    passed: bool = False
    violations: list[str] = field(default_factory=list)


@dataclass
class NoFillerReport:
    checks: list[NoFillerCheckResult] = field(default_factory=list)
    passed: bool = False
    total: int = 0
    passed_count: int = 0
    summary: str = ""


class NoFillerEnforcer:
    """Enforces that every narrative element serves a structural function.

    Checks from no-filler-rules.yaml:
    1. Scene necessity — scene must advance NP, modify modality, redefine OoV,
       or make/block future action
    2. Character necessity — character must occupy an actantial role
    3. Dialogue necessity — dialogue must convey information changing configuration
    4. Event necessity — event must be causally connected
    5. Action/state necessity — action must transform a state parameter
    """

    # ── Scene necessity ──────────────────────────────────────────────

    @staticmethod
    def check_scene(scene: dict[str, Any]) -> NoFillerCheckResult:
        sid = str(scene.get("id", "?"))
        diagnostic = scene.get("greimas_diagnostic", {})
        violations: list[str] = []

        if isinstance(diagnostic, dict):
            state_before = diagnostic.get("state_before", "")
            action = diagnostic.get("action_occurs", "")
            state_after = diagnostic.get("state_after", "")
            value_change = diagnostic.get("value_object_change", "none")
            future_effect = diagnostic.get("future_action_possible_or_blocked", "")
        else:
            state_before = getattr(diagnostic, "state_before", "")
            action = getattr(diagnostic, "action_occurs", "")
            state_after = getattr(diagnostic, "state_after", "")
            value_change = getattr(diagnostic, "value_object_change", "none")
            future_effect = getattr(diagnostic, "future_action_possible_or_blocked", "")

        anti_filler_passes = 0

        # Check 1: junction change
        if state_before != state_after and action:
            anti_filler_passes += 1

        # Check 2: modality change
        modality_changes = scene.get("modality_changes", [])
        if modality_changes:
            anti_filler_passes += 1

        # Check 3: value-object redefinition
        if value_change not in ("", "none", "unchanged"):
            anti_filler_passes += 1

        # Check 4: future action made possible/impossible
        if future_effect:
            anti_filler_passes += 1

        if anti_filler_passes == 0:
            violations.append(
                "Scene failed all 4 anti-filler checks: no junction change, "
                "no modality change, no value-object change, no future effect"
            )
        elif anti_filler_passes < 2:
            violations.append(
                f"Scene passed only {anti_filler_passes}/4 anti-filler checks — "
                "weak structural justification"
            )

        return NoFillerCheckResult(
            target_type="scene",
            target_id=sid,
            passed=len(violations) == 0,
            violations=violations,
        )

    # ── Character necessity ──────────────────────────────────────────

    @staticmethod
    def check_character(
        character: dict[str, Any],
        actant_roles_in_play: list[str] | None = None,
    ) -> NoFillerCheckResult:
        cid = str(character.get("id", "?"))
        violations: list[str] = []

        actant_roles = character.get("actant_roles", [])
        if not actant_roles:
            violations.append(
                "Character has no actant_roles — occupies no structural position"
            )

        if actant_roles_in_play:
            has_role = any(r in actant_roles_in_play for r in actant_roles)
            if not has_role:
                violations.append(
                    "Character's actant roles not active in current narrative program"
                )

        return NoFillerCheckResult(
            target_type="character",
            target_id=cid,
            passed=len(violations) == 0,
            violations=violations,
        )

    # ── Dialogue necessity ───────────────────────────────────────────

    @staticmethod
    def check_dialogue(
        dialogue_block: dict[str, Any],
        scene_id: str = "",
    ) -> NoFillerCheckResult:
        violations: list[str] = []

        conveys_information = dialogue_block.get("conveys_information", True)
        changes_configuration = dialogue_block.get("changes_configuration", False)
        content = dialogue_block.get("content", "")

        if not conveys_information and not changes_configuration:
            violations.append(
                "Dialogue conveys no information and changes no configuration — "
                "pure banter is filler"
            )
        if not content:
            violations.append("Dialogue block has empty content")

        return NoFillerCheckResult(
            target_type="dialogue",
            target_id=dialogue_block.get("id", scene_id or "?"),
            passed=len(violations) == 0,
            violations=violations,
        )

    # ── Event necessity ──────────────────────────────────────────────

    @staticmethod
    def check_event(event: dict[str, Any]) -> NoFillerCheckResult:
        eid = str(event.get("id", "?"))
        violations: list[str] = []

        predecessors = event.get("causal_predecessors", [])
        successors = event.get("causal_successors", [])

        if not predecessors:
            violations.append("Event has no causal predecessors — orphan event")
        if not successors:
            violations.append("Event has no causal successors — dead-end event")

        return NoFillerCheckResult(
            target_type="event",
            target_id=eid,
            passed=len(violations) == 0,
            violations=violations,
        )

    # ── Action/state necessity ───────────────────────────────────────

    @staticmethod
    def check_action(
        action: dict[str, Any],
    ) -> NoFillerCheckResult:
        aid = action.get("id", action.get("actant", "?"))
        violations: list[str] = []

        state_before = action.get("state_before", "")
        state_after = action.get("state_after", "")

        if state_before and state_after and state_before == state_after:
            violations.append(
                "Action does not transform state — pseudo-action / filler"
            )

        operation = action.get("operation", action.get("action_type", ""))
        if not operation:
            violations.append("Action has no operation or action_type defined")

        return NoFillerCheckResult(
            target_type="action",
            target_id=aid,
            passed=len(violations) == 0,
            violations=violations,
        )

    # ── Batch orchestration ──────────────────────────────────────────

    @classmethod
    def check_scenes_batch(
        cls, scenes: list[dict[str, Any]]
    ) -> NoFillerReport:
        checks = [cls.check_scene(s) for s in scenes]
        passed = [c for c in checks if c.passed]
        return NoFillerReport(
            checks=checks,
            passed=len(passed) == len(checks),
            total=len(checks),
            passed_count=len(passed),
            summary=(
                f"No-filler: {len(passed)}/{len(checks)} checks passed"
            ),
        )

    @classmethod
    def check_characters_batch(
        cls,
        characters: list[dict[str, Any]],
        actant_roles_in_play: list[str] | None = None,
    ) -> NoFillerReport:
        checks = [
            cls.check_character(c, actant_roles_in_play) for c in characters
        ]
        passed = [c for c in checks if c.passed]
        return NoFillerReport(
            checks=checks,
            passed=len(passed) == len(checks),
            total=len(checks),
            passed_count=len(passed),
            summary=(
                f"No-filler (characters): {len(passed)}/{len(checks)} checks passed"
            ),
        )
