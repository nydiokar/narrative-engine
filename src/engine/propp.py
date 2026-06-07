"""Proppian morphology — the 32 narrative functions and sequence validation.

Based on Vladimir Propp's *Morphology of the Folktale* (1928). Every narrative
episode maps to a subset of these functions in canonical order. The validator
checks that:

1. Functions appear in canonical order (no skips backward)
2. Core functions are present (villainy/lack, struggle, victory, liquidation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProppSphere(str, Enum):
    """The seven spheres of action in Proppian morphology."""

    PREPARATION = "preparation"
    COMPLICATION = "complication"
    DONOR = "donor"
    TRANSFIGURATION = "transfiguration"
    RETURN = "return"
    RECOGNITION = "recognition"
    EXPOSURE = "exposure"


class ProppFunction(str, Enum):
    """The 32 functions of Proppian morphology (functions 1-31, with VIIIa as LACK).

    Each entry encodes:
    - The Propp function symbol (e.g. β, γ, δ)
    - A short label
    - Which sphere it belongs to
    - Whether it is considered a core/mandatory function
    """

    # ── Preparation sphere (functions 1-7) ─────────────────────────────
    ABSENTATION = "absentation"
    INTERDICTION = "interdiction"
    VIOLATION = "violation"
    RECONNAISSANCE = "reconnaissance"
    DELIVERY = "delivery"
    TRICKERY = "trickery"
    COMPLICITY = "complicity"

    # ── Complication sphere (functions 8-10) ───────────────────────────
    VILLAINY = "villainy"
    LACK = "lack"
    MEDIATION = "mediation"
    BEGINNING_COUNTERACTION = "beginning_counteraction"

    # ── Donor sphere (functions 11-14) ─────────────────────────────────
    DEPARTURE = "departure"
    DONOR_TEST = "donor_test"
    HERO_REACTION = "hero_reaction"
    RECEIPT_MAGICAL_AGENT = "receipt_magical_agent"

    # ── Transfiguration sphere (functions 15-18) ───────────────────────
    GUIDANCE = "guidance"
    STRUGGLE = "struggle"
    BRANDING = "branding"
    VICTORY = "victory"

    # ── Return sphere (functions 19-22) ────────────────────────────────
    LIQUIDATION = "liquidation"
    RETURN = "return"
    PURSUIT = "pursuit"
    RESCUE = "rescue"

    # ── Recognition sphere (functions 23-26) ───────────────────────────
    UNRECOGNIZED_ARRIVAL = "unrecognized_arrival"
    UNFOUNDED_CLAIMS = "unfounded_claims"
    DIFFICULT_TASK = "difficult_task"
    SOLUTION = "solution"

    # ── Exposure sphere (functions 27-31) ──────────────────────────────
    RECOGNITION = "recognition"
    EXPOSURE = "exposure"
    TRANSFIGURATION = "transfiguration"
    PUNISHMENT = "punishment"
    WEDDING = "wedding"


# ── Metadata ──────────────────────────────────────────────────────────────

PROPP_METADATA: dict[ProppFunction, dict[str, Any]] = {
    ProppFunction.ABSENTATION: {
        "symbol": "β",
        "sphere": ProppSphere.PREPARATION,
        "description": "A member of the family leaves home",
        "core": False,
    },
    ProppFunction.INTERDICTION: {
        "symbol": "γ",
        "sphere": ProppSphere.PREPARATION,
        "description": "An interdiction is addressed to the hero",
        "core": False,
    },
    ProppFunction.VIOLATION: {
        "symbol": "δ",
        "sphere": ProppSphere.PREPARATION,
        "description": "The interdiction is violated",
        "core": False,
    },
    ProppFunction.RECONNAISSANCE: {
        "symbol": "ε",
        "sphere": ProppSphere.PREPARATION,
        "description": "The villain makes an attempt at reconnaissance",
        "core": False,
    },
    ProppFunction.DELIVERY: {
        "symbol": "ζ",
        "sphere": ProppSphere.PREPARATION,
        "description": "The villain receives information about the victim",
        "core": False,
    },
    ProppFunction.TRICKERY: {
        "symbol": "η",
        "sphere": ProppSphere.PREPARATION,
        "description": "The villain attempts to deceive the victim",
        "core": False,
    },
    ProppFunction.COMPLICITY: {
        "symbol": "θ",
        "sphere": ProppSphere.PREPARATION,
        "description": "The victim submits to the deception",
        "core": False,
    },
    ProppFunction.VILLAINY: {
        "symbol": "A",
        "sphere": ProppSphere.COMPLICATION,
        "description": "The villain causes harm or injury to a member of the family",
        "core": True,
    },
    ProppFunction.LACK: {
        "symbol": "a",
        "sphere": ProppSphere.COMPLICATION,
        "description": "A member of the family lacks something or desires something",
        "core": True,
    },
    ProppFunction.MEDIATION: {
        "symbol": "B",
        "sphere": ProppSphere.COMPLICATION,
        "description": "Misfortune or lack is made known; the hero is approached",
        "core": False,
    },
    ProppFunction.BEGINNING_COUNTERACTION: {
        "symbol": "C",
        "sphere": ProppSphere.COMPLICATION,
        "description": "The seeker agrees to or decides upon counteraction",
        "core": False,
    },
    ProppFunction.DEPARTURE: {
        "symbol": "↑",
        "sphere": ProppSphere.DONOR,
        "description": "The hero leaves home",
        "core": False,
    },
    ProppFunction.DONOR_TEST: {
        "symbol": "D",
        "sphere": ProppSphere.DONOR,
        "description": "The hero is tested, preparing the way for receiving a magical agent",
        "core": False,
    },
    ProppFunction.HERO_REACTION: {
        "symbol": "E",
        "sphere": ProppSphere.DONOR,
        "description": "The hero reacts to the actions of the future donor",
        "core": False,
    },
    ProppFunction.RECEIPT_MAGICAL_AGENT: {
        "symbol": "F",
        "sphere": ProppSphere.DONOR,
        "description": "The hero acquires the use of a magical agent",
        "core": False,
    },
    ProppFunction.GUIDANCE: {
        "symbol": "G",
        "sphere": ProppSphere.TRANSFIGURATION,
        "description": "The hero is transferred to the whereabouts of an object of search",
        "core": False,
    },
    ProppFunction.STRUGGLE: {
        "symbol": "H",
        "sphere": ProppSphere.TRANSFIGURATION,
        "description": "The hero and the villain join in direct combat",
        "core": True,
    },
    ProppFunction.BRANDING: {
        "symbol": "J",
        "sphere": ProppSphere.TRANSFIGURATION,
        "description": "The hero is branded",
        "core": False,
    },
    ProppFunction.VICTORY: {
        "symbol": "I",
        "sphere": ProppSphere.TRANSFIGURATION,
        "description": "The villain is defeated",
        "core": True,
    },
    ProppFunction.LIQUIDATION: {
        "symbol": "K",
        "sphere": ProppSphere.RETURN,
        "description": "The initial misfortune or lack is liquidated",
        "core": True,
    },
    ProppFunction.RETURN: {
        "symbol": "↓",
        "sphere": ProppSphere.RETURN,
        "description": "The hero returns",
        "core": False,
    },
    ProppFunction.PURSUIT: {
        "symbol": "Pr",
        "sphere": ProppSphere.RETURN,
        "description": "The hero is pursued",
        "core": False,
    },
    ProppFunction.RESCUE: {
        "symbol": "Rs",
        "sphere": ProppSphere.RETURN,
        "description": "Rescue of the hero from pursuit",
        "core": False,
    },
    ProppFunction.UNRECOGNIZED_ARRIVAL: {
        "symbol": "o",
        "sphere": ProppSphere.RECOGNITION,
        "description": "The hero, unrecognized, arrives home or in another country",
        "core": False,
    },
    ProppFunction.UNFOUNDED_CLAIMS: {
        "symbol": "L",
        "sphere": ProppSphere.RECOGNITION,
        "description": "A false hero presents unfounded claims",
        "core": False,
    },
    ProppFunction.DIFFICULT_TASK: {
        "symbol": "M",
        "sphere": ProppSphere.RECOGNITION,
        "description": "A difficult task is proposed to the hero",
        "core": False,
    },
    ProppFunction.SOLUTION: {
        "symbol": "N",
        "sphere": ProppSphere.RECOGNITION,
        "description": "The task is resolved",
        "core": False,
    },
    ProppFunction.RECOGNITION: {
        "symbol": "Q",
        "sphere": ProppSphere.EXPOSURE,
        "description": "The hero is recognized",
        "core": False,
    },
    ProppFunction.EXPOSURE: {
        "symbol": "Ex",
        "sphere": ProppSphere.EXPOSURE,
        "description": "The false hero or villain is exposed",
        "core": False,
    },
    ProppFunction.TRANSFIGURATION: {
        "symbol": "T",
        "sphere": ProppSphere.EXPOSURE,
        "description": "The hero is given a new appearance",
        "core": False,
    },
    ProppFunction.PUNISHMENT: {
        "symbol": "U",
        "sphere": ProppSphere.EXPOSURE,
        "description": "The villain is punished",
        "core": False,
    },
    ProppFunction.WEDDING: {
        "symbol": "W",
        "sphere": ProppSphere.EXPOSURE,
        "description": "The hero is married and ascends the throne",
        "core": False,
    },
}


# Canonical order of functions
_CANONICAL_ORDER: list[ProppFunction] = [
    ProppFunction.ABSENTATION,
    ProppFunction.INTERDICTION,
    ProppFunction.VIOLATION,
    ProppFunction.RECONNAISSANCE,
    ProppFunction.DELIVERY,
    ProppFunction.TRICKERY,
    ProppFunction.COMPLICITY,
    ProppFunction.VILLAINY,
    ProppFunction.LACK,
    ProppFunction.MEDIATION,
    ProppFunction.BEGINNING_COUNTERACTION,
    ProppFunction.DEPARTURE,
    ProppFunction.DONOR_TEST,
    ProppFunction.HERO_REACTION,
    ProppFunction.RECEIPT_MAGICAL_AGENT,
    ProppFunction.GUIDANCE,
    ProppFunction.STRUGGLE,
    ProppFunction.BRANDING,
    ProppFunction.VICTORY,
    ProppFunction.LIQUIDATION,
    ProppFunction.RETURN,
    ProppFunction.PURSUIT,
    ProppFunction.RESCUE,
    ProppFunction.UNRECOGNIZED_ARRIVAL,
    ProppFunction.UNFOUNDED_CLAIMS,
    ProppFunction.DIFFICULT_TASK,
    ProppFunction.SOLUTION,
    ProppFunction.RECOGNITION,
    ProppFunction.EXPOSURE,
    ProppFunction.TRANSFIGURATION,
    ProppFunction.PUNISHMENT,
    ProppFunction.WEDDING,
]

_CANONICAL_INDEX: dict[ProppFunction, int] = {
    fn: idx for idx, fn in enumerate(_CANONICAL_ORDER)
}

@dataclass
class ProppValidationResult:
    """Result of validating a Propp function sequence."""

    passed: bool = False
    violations: list[str] = field(default_factory=list)
    sequence: list[ProppFunction] = field(default_factory=list)
    missing_core: list[ProppFunction] = field(default_factory=list)


class ProppSequenceValidator:
    """Validates that a sequence of Propp functions is structurally sound."""

    @classmethod
    def parse_functions(
        cls,
        raw_functions: list[str],
    ) -> tuple[list[ProppFunction], list[str]]:
        """Parse a list of strings into ProppFunction enum values.

        Returns (parsed, errors). Unknown strings produce an error
        but are silently skipped — the parser is lenient.
        """
        parsed: list[ProppFunction] = []
        errors: list[str] = []
        for raw in raw_functions:
            normalized = raw.strip().lower().replace(" ", "_")
            try:
                parsed.append(ProppFunction(normalized))
            except ValueError:
                errors.append(f"Unknown Propp function: '{raw}'")
        return parsed, errors

    @classmethod
    def validate_sequence(
        cls,
        functions: list[ProppFunction],
        episode_label: str = "",
    ) -> ProppValidationResult:
        """Validate a sequence of Propp functions.

        Rules:
        1. Canonical order — functions must not skip backward
        2. Core presence — at least one of {villainy, lack} must be present
           and {struggle, victory, liquidation} must be present if any
           transfiguration or return sphere functions appear
        3. No empty sequence — at least one function must be present
        """
        violations: list[str] = []
        prefix = f"[{episode_label}] " if episode_label else ""

        if not functions:
            return ProppValidationResult(
                passed=False,
                violations=[f"{prefix}Empty Propp sequence — at least one function is required"],
                sequence=[],
                missing_core=[],
            )

        # Rule 1: Canonical order
        last_valid_index = -1
        for fn in functions:
            idx = _CANONICAL_INDEX.get(fn, -1)
            if idx == -1:
                violations.append(
                    f"{prefix}Unknown function '{fn.value}' — cannot validate order"
                )
                continue
            if idx < last_valid_index:
                violations.append(
                    f"{prefix}Sequence order violation: '{fn.value}' "
                    f"(canonical position {idx}) appears after position {last_valid_index} "
                    f"— functions cannot move backward"
                )
            last_valid_index = idx

        # Rule 2: Core presence
        present = set(functions)
        missing_core: list[ProppFunction] = []

        # Must have at least one inciting incident (villainy or lack)
        if ProppFunction.VILLAINY not in present and ProppFunction.LACK not in present:
            missing_core.append(ProppFunction.VILLAINY)
            violations.append(
                f"{prefix}Missing core inciting incident — "
                "at least one of 'villainy' or 'lack' is required"
            )

        # If any transfiguration or return sphere functions appear, struggle + victory + liquidation are required
        combat_resolution_sphere = {fn for fn in present if PROPP_METADATA.get(fn, {}).get("sphere") in (
            ProppSphere.TRANSFIGURATION, ProppSphere.RETURN
        )}
        if combat_resolution_sphere:
            for required in (ProppFunction.STRUGGLE, ProppFunction.VICTORY, ProppFunction.LIQUIDATION):
                if required not in present:
                    missing_core.append(required)
                    violations.append(
                        f"{prefix}Missing core function '{required.value}' — "
                        "required when transfiguration or return sphere functions are present"
                    )

        # Specific: if struggle appears, victory must also appear
        if ProppFunction.STRUGGLE in present and ProppFunction.VICTORY not in present:
            if ProppFunction.VICTORY not in missing_core:
                missing_core.append(ProppFunction.VICTORY)
            violations.append(
                f"{prefix}'struggle' present without 'victory' — "
                "conflict must reach resolution"
            )

        return ProppValidationResult(
            passed=len(violations) == 0,
            violations=violations,
            sequence=functions,
            missing_core=missing_core,
        )

    @classmethod
    def validate_episodes(
        cls,
        episodes: list[dict[str, Any]],
    ) -> list[ProppValidationResult]:
        """Validate Propp function sequences across multiple episodes.

        Parse errors (unknown function names) are appended as violations
        on the result so callers can surface them.
        """
        results: list[ProppValidationResult] = []
        for ep in episodes:
            raw = ep.get("propp_functions", []) or []
            title = ep.get("title", ep.get("id", "?"))
            parsed, errors = cls.parse_functions(raw)
            result = cls.validate_sequence(parsed, episode_label=title)
            for err in errors:
                result.violations.append(f"[{title}] {err}")
                result.passed = False
            results.append(result)
        return results
