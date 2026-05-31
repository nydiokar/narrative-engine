"""Cliché detection — identifies high-frequency genre defaults.

Cliché = high-frequency genre defaults assembled without meaningful inversion,
escalation, recombination, or thematic necessity.

Fresh = low-similarity or unexpectedly recombined candidate that still passes
the hard gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ClicheSignal:
    name: str
    description: str
    detected: bool = False
    severity: int = 0  # 0-3


@dataclass
class ClicheDetectionResult:
    signals: list[ClicheSignal] = field(default_factory=list)
    cliche_score: int = 0  # Sum of severities
    max_score: int = 0
    novelty_penalty: float = 0.0  # 0.0 - 1.0 multiplier on novelty score
    is_fresh: bool = False


CLICHE_SIGNALS: list[dict[str, str]] = [
    {"name": "default_genre_setting", "description": "The most obvious world for the genre (e.g. medieval tavern for fantasy)"},
    {"name": "default_protagonist_type", "description": "The expected protagonist archetype (e.g. chosen one in fantasy)"},
    {"name": "default_motivation", "description": "The obvious reason for acting (e.g. save the world)"},
    {"name": "default_villain_motive", "description": "Villain is evil because evil — no value-logic"},
    {"name": "default_ending", "description": "The genre-standard resolution (e.g. wedding for romance)"},
    {"name": "no_cost_for_victory", "description": "Protagonist wins everything, loses nothing"},
    {"name": "no_contradiction_inside_protagonist", "description": "Internally consistent in a way that feels unreal"},
    {"name": "theme_stated_not_dramatized", "description": "Theme is named but not embodied in any scene"},
    {"name": "world_as_decoration", "description": "Setting has no impact on choices or outcomes"},
    {"name": "villain_evil_without_value", "description": "No value-logic behind the opposition"},
    {"name": "chosen_one_without_burden", "description": "Destiny without cost"},
    {"name": "revenge_without_deformation", "description": "Protagonist exacts revenge and remains unchanged"},
    {"name": "romance_without_specific_incompatibility", "description": "Lovers kept apart by vague circumstances, not genuine value conflict"},
    {"name": "mentor_dies_only_to_motivate", "description": "Mentor death has no other narrative function"},
]


FRESHNESS_GENERATORS: list[dict[str, str]] = [
    {"name": "change_object_of_value", "description": "Make the protagonist want something unexpected"},
    {"name": "change_moral_cost", "description": "Raise the price of pursuing the Object"},
    {"name": "change_actant_roles", "description": "Swap who occupies which structural position"},
    {"name": "invert_helper_opponent", "description": "The helper has a hidden cost; the opponent has a valid point"},
    {"name": "world_enforces_theme", "description": "The setting's rules force thematic choices"},
    {"name": "valid_antagonist_value", "description": "The opponent is right about something"},
    {"name": "unexpected_genre_world", "description": "Move genre promise into unexpected world"},
    {"name": "victory_damages_something_real", "description": "Success has a permanent cost"},
    {"name": "wound_contradicts_desire", "description": "What the character wants conflicts with their deepest damage"},
    {"name": "helper_is_dangerous", "description": "Aid comes with strings"},
    {"name": "love_interest_ideologically_opposed", "description": "Attraction across a value chasm"},
    {"name": "ambiguous_final_sanction", "description": "The ending unsettles easy judgment"},
    {"name": "tactically_right_morally_wrong", "description": "Protagonist wins the battle but loses themselves"},
    {"name": "antagonist_wrong_method_right_diagnosis", "description": "Antagonist's diagnosis is accurate even if methods are not"},
]


class ClicheDetector:
    """Detects cliché signals and computes novelty penalties."""

    @classmethod
    def detect(
        cls,
        story: dict[str, Any] | None = None,
        characters: list[dict[str, Any]] | None = None,
        settings: list[dict[str, Any]] | None = None,
        explicit_signals: list[tuple[str, int]] | None = None,
    ) -> ClicheDetectionResult:
        signals: list[ClicheSignal] = []

        for signal_def in CLICHE_SIGNALS:
            signals.append(ClicheSignal(
                name=signal_def["name"],
                description=signal_def["description"],
            ))

        if explicit_signals:
            for signal_name, severity in explicit_signals:
                for sig in signals:
                    if sig.name == signal_name:
                        sig.detected = True
                        sig.severity = severity
                        break

        cliche_score = sum(s.severity for s in signals if s.detected)
        max_score = 3 * len(signals)

        # Novelty penalty: 0.0 at 0 cliché, up to 1.0 at max
        if max_score > 0:
            penalty = cliche_score / max_score
        else:
            penalty = 0.0

        # A story is "fresh" if cliche_score <= 3 (i.e. practically no clichés)
        is_fresh = cliche_score <= 3

        return ClicheDetectionResult(
            signals=signals,
            cliche_score=cliche_score,
            max_score=max_score,
            novelty_penalty=penalty,
            is_fresh=is_fresh,
        )

    @classmethod
    def list_signals(cls) -> list[dict[str, str]]:
        return CLICHE_SIGNALS

    @classmethod
    def list_freshness_generators(cls) -> list[dict[str, str]]:
        return FRESHNESS_GENERATORS
