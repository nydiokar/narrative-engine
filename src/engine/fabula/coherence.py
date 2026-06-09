"""Fabula Coherence Engine — the 11 diagnostic checks for narrative soundness.

These checks constitute the hard gate from the evaluation-rubric specification.
Every narrative artifact must pass all checks or be rejected without scoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from src.engine.propp import ProppSequenceValidator
from src.engine.todorov import TodorovValidator


@dataclass
class FabulaCoherenceCheck:
    """Result of a single coherence check."""

    name: str
    description: str
    passed: bool = False
    violations: list[str] = field(default_factory=list)


@dataclass
class FabulaCoherenceReport:
    """Aggregate report of all 8 coherence checks."""

    checks: list[FabulaCoherenceCheck] = field(default_factory=list)
    passed: bool = False
    summary: str = ""


class FabulaCoherenceEngine:
    """Runs the 11 Fabula Coherence checks on a narrative artifact.

    The 11 checks:
    1. Causal Soundness — every event follows from prior events
    2. Character Intentionality — every action grounded in motivation
    3. World Rule Consistency — no world-rule violations
    4. Stakes Presence — Object of value contested every scene
    5. Contradiction-Free — no logical/temporal/factual contradictions
    6. Conflict Active — at least one conflict type active per scene
    7. Continuity — no drift without causal justification
    8. Event Necessity — every event transforms state or enables future
    9. Propp Sequence — functions follow canonical morphology order
    10. Todorov Equilibrium — phases follow canonical narrative arc
    11. GOLEM Event Validation — every event follows goal→action→outcome→perception→internal_element
    """

    CHECK_DEFINITIONS: list[dict[str, str]] = [
        {
            "name": "causal_soundness",
            "description": "Every event follows from prior events. No ex nihilo events.",
        },
        {
            "name": "character_intentionality",
            "description": "Every action by a character is grounded in their motivation stack.",
        },
        {
            "name": "world_rule_consistency",
            "description": "No violation of established world rules.",
        },
        {
            "name": "stakes_presence",
            "description": "At least one Object of value is under contest in every scene.",
        },
        {
            "name": "contradiction_free",
            "description": "No logical, temporal, or factual contradictions within the artifact.",
        },
        {
            "name": "conflict_active",
            "description": "At least one conflict type is active per scene.",
        },
        {
            "name": "continuity",
            "description": "No drift in character traits, modality states, or actantial positions without causal justification.",
        },
        {
            "name": "event_necessity",
            "description": "Every event must register a non-none value_object_change or modality change — otherwise it is filler.",
        },
        {
            "name": "propp_sequence",
            "description": "Propp functions follow canonical morphology order with core functions present.",
        },
        {
            "name": "todorov_equilibrium",
            "description": "Todorov phases follow canonical narrative arc with no regression.",
        },
        {
            "name": "golem_event_validation",
            "description": "Every event must follow the GOLEM model: goal, action, outcome, perception, internal_element.",
        },
    ]

    # ── Individual check methods ─────────────────────────────────────

    @staticmethod
    def check_causal_soundness(
        events: list[dict[str, Any]],
    ) -> FabulaCoherenceCheck:
        check = FabulaCoherenceCheck(
            name="causal_soundness",
            description="Every event follows from prior events. No ex nihilo events.",
            passed=True,
        )
        for i, event in enumerate(events):
            predecessors = event.get("causal_predecessors", [])
            if i > 0 and not predecessors:
                check.violations.append(
                    f"Event[{i}] ({event.get('id', '?')}) has no causal predecessors — "
                    "appears ex nihilo"
                )
        if check.violations:
            check.passed = False
        return check

    @staticmethod
    def check_character_intentionality(
        events: list[dict[str, Any]],
        characters: list[dict[str, Any]] | None = None,
    ) -> FabulaCoherenceCheck:
        check = FabulaCoherenceCheck(
            name="character_intentionality",
            description="Every action by a character is grounded in their motivation stack.",
            passed=True,
        )
        char_map: dict[str, dict[str, Any]] = {}
        if characters:
            for c in characters:
                cid = c.get("id", "")
                if isinstance(cid, UUID):
                    cid = str(cid)
                char_map[cid] = c

        for i, event in enumerate(events):
            actant = event.get("actant", event.get("subject", ""))
            if not actant:
                continue
            action = event.get("action", event.get("operation", ""))
            if not action:
                continue

            if actant in char_map:
                desires = char_map[actant].get("core_desires", [])
                fears = char_map[actant].get("core_fears", [])
                if not desires and not fears:
                    check.violations.append(
                        f"Event[{i}]: {actant} performs '{action}' but has "
                        "no core_desires or core_fears defined"
                    )
        if check.violations:
            check.passed = False
        return check

    @staticmethod
    def check_world_rule_consistency(
        events: list[dict[str, Any]],
        world_rules: list[str] | None = None,
    ) -> FabulaCoherenceCheck:
        check = FabulaCoherenceCheck(
            name="world_rule_consistency",
            description="No violation of established world rules.",
            passed=True,
        )
        for i, event in enumerate(events):
            violations = event.get("world_rule_violations", [])
            if violations:
                check.violations.append(
                    f"Event[{i}]: world rule violations: {violations}"
                )
        if check.violations:
            check.passed = False
        return check

    @staticmethod
    def check_stakes_presence(
        scenes: list[dict[str, Any]],
    ) -> FabulaCoherenceCheck:
        check = FabulaCoherenceCheck(
            name="stakes_presence",
            description="At least one Object of value is under contest in every scene.",
            passed=True,
        )
        for i, scene in enumerate(scenes):
            value_change = scene.get("greimas_diagnostic", {}).get(
                "value_object_change", "none"
            )
            if value_change in ("", "none", "unchanged"):
                check.violations.append(
                    f"Scene[{i}] has no Object-of-value change — stakes absent"
                )
        if check.violations:
            check.passed = False
        return check

    @staticmethod
    def check_contradiction_free(
        events: list[dict[str, Any]],
    ) -> FabulaCoherenceCheck:
        check = FabulaCoherenceCheck(
            name="contradiction_free",
            description="No logical, temporal, or factual contradictions.",
            passed=True,
        )
        seen_states: dict[str, Any] = {}

        for i, event in enumerate(events):
            state_after = event.get("state_after", "")
            if not state_after:
                continue
            # Track modality states per actant for contradiction detection
            modality_changes = event.get("modality_changes", [])
            for mc in modality_changes:
                actant_id = mc.get("actant_id", "")
                mod = mc.get("modality", "")
                to_state = mc.get("to_state", "")
                key = f"{actant_id}.{mod}"
                if key in seen_states and seen_states[key] != to_state:
                    # This is only a contradiction if the change is unexplained
                    from_state = mc.get("from_state", "")
                    check.violations.append(
                        f"Event[{i}]: {key} changed {from_state}→{to_state} "
                        f"but was previously {seen_states[key]} — "
                        "check for causal justification"
                    )
                seen_states[key] = to_state
        if check.violations:
            check.passed = False
        return check

    @staticmethod
    def check_conflict_active(
        scenes: list[dict[str, Any]],
    ) -> FabulaCoherenceCheck:
        check = FabulaCoherenceCheck(
            name="conflict_active",
            description="At least one conflict type is active per scene.",
            passed=True,
        )
        for i, scene in enumerate(scenes):
            conflict_load = scene.get("conflict_load", {})
            if isinstance(conflict_load, dict):
                all_none = all(
                    v in ("", "none", None) for v in conflict_load.values()
                )
            else:
                all_none = all(
                    v in ("", "none", None) for v in conflict_load.values()
                )

            if all_none:
                check.violations.append(
                    f"Scene[{i}] has no active conflict types"
                )
        if check.violations:
            check.passed = False
        return check

    @staticmethod
    def check_continuity(
        events: list[dict[str, Any]],
        characters: list[dict[str, Any]] | None = None,
    ) -> FabulaCoherenceCheck:
        check = FabulaCoherenceCheck(
            name="continuity",
            description="No drift without causal justification.",
            passed=True,
        )
        # Track character modality trajectories
        modality_log: dict[str, list[tuple[int, str, str]]] = {}

        for i, event in enumerate(events):
            for mc in event.get("modality_changes", []):
                actant_id = mc.get("actant_id", "")
                mod = mc.get("modality", "")
                to_state = mc.get("to_state", "")
                trigger = mc.get("trigger", mc.get("cause", ""))
                if actant_id and mod:
                    modality_log.setdefault(f"{actant_id}.{mod}", []).append(
                        (i, to_state, trigger)
                    )

        for key, transitions in modality_log.items():
            for j in range(1, len(transitions)):
                prev_idx, prev_state, prev_trigger = transitions[j - 1]
                curr_idx, curr_state, curr_trigger = transitions[j]
                if prev_state != curr_state and not curr_trigger:
                    check.violations.append(
                        f"{key} changed {prev_state}→{curr_state} at event[{curr_idx}] "
                        f"but has no causal trigger"
                    )

        if check.violations:
            check.passed = False
        return check

    @staticmethod
    def check_event_necessity(
        events: list[dict[str, Any]],
    ) -> FabulaCoherenceCheck:
        check = FabulaCoherenceCheck(
            name="event_necessity",
            description="Every event must register a non-none value_object_change or modality change.",
            passed=True,
        )
        for i, event in enumerate(events):
            value_change = event.get("value_object_change", "none")
            modality_change = event.get("modality_changes", [])
            has_modality_change = bool(modality_change)
            unlocks = event.get("unlocks", "")
            blocks = event.get("blocks", "")

            if (
                value_change in ("", "none", "unchanged")
                and not has_modality_change
                and not unlocks
                and not blocks
            ):
                check.violations.append(
                    f"Event[{i}] has no value_object_change, no modality change, "
                    "no unlocks, and no blocks — filler"
                )
        if check.violations:
            check.passed = False
        return check

    # ── Todorov equilibrium check ───────────────────────────────────

    @staticmethod
    def check_todorov_equilibrium(
        episodes: list[dict[str, Any]] | None = None,
    ) -> FabulaCoherenceCheck:
        check = FabulaCoherenceCheck(
            name="todorov_equilibrium",
            description="Todorov phases follow canonical narrative arc with no regression.",
            passed=True,
        )
        if not episodes:
            return check

        result = TodorovValidator.validate_episodes(episodes)
        for v in result.violations:
            check.violations.append(v)

        if check.violations:
            check.passed = False
        return check

    # ── GOLEM event validation check ────────────────────────────────

    @staticmethod
    def check_golem_event_validation(
        events: list[dict[str, Any]] | None = None,
    ) -> FabulaCoherenceCheck:
        check = FabulaCoherenceCheck(
            name="golem_event_validation",
            description="Every event must follow the GOLEM model: goal, action, outcome, perception, internal_element.",
            passed=True,
        )
        if not events:
            return check

        for i, event in enumerate(events):
            if not event.get("goal"):
                check.violations.append(
                    f"Event[{i}] ({event.get('id', '?')}): missing 'goal' — "
                    "every event must originate from a character's goal"
                )
            if not event.get("action_type") and not event.get("action"):
                check.violations.append(
                    f"Event[{i}] ({event.get('id', '?')}): missing 'action_type' or 'action' — "
                    "action is required between goal and outcome"
                )
            if not event.get("outcome"):
                check.violations.append(
                    f"Event[{i}] ({event.get('id', '?')}): missing 'outcome' — "
                    "every action must produce an outcome"
                )
            if not event.get("perception"):
                check.violations.append(
                    f"Event[{i}] ({event.get('id', '?')}): missing 'perception' — "
                    "how the actant perceives the outcome must be recorded"
                )
            if not event.get("internal_element"):
                check.violations.append(
                    f"Event[{i}] ({event.get('id', '?')}): missing 'internal_element' — "
                    "every event must register an internal/subjective effect"
                )

        if check.violations:
            check.passed = False
        return check

    # ── Propp morphology check ──────────────────────────────────────

    @staticmethod
    def check_propp_sequence(
        episodes: list[dict[str, Any]] | None = None,
    ) -> FabulaCoherenceCheck:
        check = FabulaCoherenceCheck(
            name="propp_sequence",
            description="Propp functions follow canonical morphology order with core functions present.",
            passed=True,
        )
        if not episodes:
            # No episode data to validate — skip (backward compatible)
            return check

        # Skip if no episodes have explicit propp_functions (not opted in)
        has_functions = any(ep.get("propp_functions") for ep in episodes)
        if not has_functions:
            return check

        results = ProppSequenceValidator.validate_episodes(episodes)
        for result in results:
            for v in result.violations:
                check.violations.append(v)

        if check.violations:
            check.passed = False
        return check

    # ── Orchestration ────────────────────────────────────────────────

    @classmethod
    def run_all_checks(
        cls,
        events: list[dict[str, Any]] | None = None,
        scenes: list[dict[str, Any]] | None = None,
        characters: list[dict[str, Any]] | None = None,
        world_rules: list[str] | None = None,
        episodes: list[dict[str, Any]] | None = None,
        golem_events: list[dict[str, Any]] | None = None,
    ) -> FabulaCoherenceReport:
        events = events or []
        scenes = scenes or []

        checks: list[FabulaCoherenceCheck] = [
            cls.check_causal_soundness(events),
            cls.check_character_intentionality(events, characters),
            cls.check_world_rule_consistency(events, world_rules),
            cls.check_stakes_presence(scenes),
            cls.check_contradiction_free(events),
            cls.check_conflict_active(scenes),
            cls.check_continuity(events, characters),
            cls.check_event_necessity(events),
            cls.check_propp_sequence(episodes),
            cls.check_todorov_equilibrium(episodes),
            cls.check_golem_event_validation(golem_events),
        ]

        passed = all(c.passed for c in checks)
        total = len(checks)
        passed_count = sum(1 for c in checks if c.passed)
        violation_count = sum(len(c.violations) for c in checks)

        summary = (
            f"Fabula Coherence: {passed_count}/{total} checks passed, "
            f"{violation_count} violations."
            if violation_count > 0
            else f"Fabula Coherence: all {total}/{total} checks passed."
        )

        return FabulaCoherenceReport(
            checks=checks,
            passed=passed,
            summary=summary,
        )
