"""Narrative Program (NP) — formal transformation from initial to terminal state.

Every NP follows the canonical schema:
    Manipulation → Competence → Performance → Sanction

This module validates phase ordering, prerequisites, and completeness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID


class CanonicalPhase(str, Enum):
    MANIPULATION = "manipulation"
    COMPETENCE = "competence"
    PERFORMANCE = "performance"
    SANCTION = "sanction"


# Canonical phase order
PHASE_ORDER: list[CanonicalPhase] = [
    CanonicalPhase.MANIPULATION,
    CanonicalPhase.COMPETENCE,
    CanonicalPhase.PERFORMANCE,
    CanonicalPhase.SANCTION,
]

PHASE_INDEX = {p: i for i, p in enumerate(PHASE_ORDER)}


@dataclass
class NarrativeProgramData:
    """Simplified view of a narrative program for validation."""
    id: UUID | str
    subject: str
    object_of_value_id: str
    object_of_value_type: str

    manipulation_completed: bool = False
    competence_completed: bool = False
    performance_completed: bool = False
    sanction_completed: bool = False

    manipulation_sender: str = ""
    competence_modalities: list[str] = field(default_factory=list)
    performance_operation: str = ""
    sanction_judgment: str = ""

    junction_initial: str = "disjunction"
    junction_terminal: str = "conjunction"


@dataclass
class PhaseValidationResult:
    phase: CanonicalPhase
    completed: bool
    issues: list[str] = field(default_factory=list)


@dataclass
class NarrativeProgramValidationResult:
    np_id: str | UUID
    is_valid: bool = False
    phases: list[PhaseValidationResult] = field(default_factory=list)
    ordering_issues: list[str] = field(default_factory=list)
    completeness_issues: list[str] = field(default_factory=list)


class CanonicalSchemaChecker:
    """Validates that a narrative program follows the canonical schema."""

    @staticmethod
    def validate_phase_order(
        completed_phases: dict[str, bool],
    ) -> list[str]:
        """Check that phases are completed in canonical order with no gaps."""
        issues: list[str] = []
        last_completed_index = -1

        for phase in PHASE_ORDER:
            completed = completed_phases.get(phase.value, False)
            idx = PHASE_INDEX[phase]

            if completed:
                if last_completed_index >= 0 and idx > last_completed_index + 1:
                    gap_phases = [
                        p.value for p in PHASE_ORDER[last_completed_index + 1 : idx]
                    ]
                    issues.append(
                        f"Phase '{phase.value}' completed but gap exists: "
                        f"{', '.join(gap_phases)} not completed"
                    )
                last_completed_index = idx

        return issues

    @staticmethod
    def validate_narrative_program(
        np_data: NarrativeProgramData,
    ) -> NarrativeProgramValidationResult:
        issues: list[str] = []
        phase_results: list[PhaseValidationResult] = []

        completed = {
            "manipulation": np_data.manipulation_completed,
            "competence": np_data.competence_completed,
            "performance": np_data.performance_completed,
            "sanction": np_data.sanction_completed,
        }

        ordering_issues = CanonicalSchemaChecker.validate_phase_order(completed)
        completeness_issues: list[str] = []

        # Phase-specific preconditions
        if np_data.manipulation_completed and not np_data.manipulation_sender:
            completeness_issues.append(
                "Manipulation completed but no Sender specified"
            )

        if np_data.competence_completed and not np_data.competence_modalities:
            completeness_issues.append(
                "Competence completed but no modalities acquired"
            )

        if np_data.performance_completed and not np_data.performance_operation:
            completeness_issues.append(
                "Performance completed but no operation specified"
            )

        if np_data.sanction_completed and not np_data.sanction_judgment:
            completeness_issues.append(
                "Sanction completed but no judgment rendered"
            )

        # Terminal state must differ from initial
        if np_data.junction_initial == np_data.junction_terminal:
            completeness_issues.append(
                f"Terminal junction '{np_data.junction_terminal}' equals initial — "
                "no transformation occurred"
            )

        for phase in PHASE_ORDER:
            ph_completed = completed[phase.value]
            ph_issues: list[str] = []

            if phase == CanonicalPhase.MANIPULATION and not np_data.subject:
                ph_issues.append("No subject defined")

            if phase == CanonicalPhase.PERFORMANCE and not np_data.performance_operation:
                ph_issues.append("No operation defined for performance")

            phase_results.append(
                PhaseValidationResult(
                    phase=phase,
                    completed=ph_completed,
                    issues=ph_issues,
                )
            )

        all_issues = issues + ordering_issues + completeness_issues
        return NarrativeProgramValidationResult(
            np_id=np_data.id,
            is_valid=len(all_issues) == 0,
            phases=phase_results,
            ordering_issues=ordering_issues,
            completeness_issues=completeness_issues,
        )

    @staticmethod
    def validate_from_dict(
        data: dict[str, Any],
    ) -> NarrativeProgramValidationResult:
        """Validate a narrative program from a dict (e.g. model_dump)."""
        canonical = data.get("canonical_phases", {})
        if isinstance(canonical, dict):
            manip = canonical.get("manipulation", {})
            comp = canonical.get("competence", {})
            perf = canonical.get("performance", {})
            sanct = canonical.get("sanction", {})
        else:
            manip = getattr(canonical, "manipulation", {})
            comp = getattr(canonical, "competence", {})
            perf = getattr(canonical, "performance", {})
            sanct = getattr(canonical, "sanction", {})

        np_data = NarrativeProgramData(
            id=data.get("id", ""),
            subject=data.get("subject", ""),
            object_of_value_id=data.get("object_of_value", {}).get("id", ""),
            object_of_value_type=data.get("object_of_value", {}).get("type", ""),
            manipulation_completed=manip.get("completed", False) if isinstance(manip, dict) else getattr(manip, "completed", False),
            competence_completed=comp.get("completed", False) if isinstance(comp, dict) else getattr(comp, "completed", False),
            performance_completed=perf.get("completed", False) if isinstance(perf, dict) else getattr(perf, "completed", False),
            sanction_completed=sanct.get("completed", False) if isinstance(sanct, dict) else getattr(sanct, "completed", False),
            manipulation_sender=manip.get("sender", "") if isinstance(manip, dict) else getattr(manip, "sender", ""),
            competence_modalities=comp.get("modalities_acquired", []) if isinstance(comp, dict) else getattr(comp, "modalities_acquired", []),
            performance_operation=perf.get("operation", "") if isinstance(perf, dict) else getattr(perf, "operation", ""),
            sanction_judgment=sanct.get("judgment", "") if isinstance(sanct, dict) else getattr(sanct, "judgment", ""),
            junction_initial=data.get("initial_state", {}).get("junction", "disjunction"),
            junction_terminal=data.get("terminal_state", {}).get("junction", "conjunction"),
        )

        return CanonicalSchemaChecker.validate_narrative_program(np_data)


@dataclass
class EpisodeGreimasValidation:
    episode_id: str | UUID
    subject: str
    object_of_value: str
    current_state: str
    desired_transformation: str
    opponent: str
    opponent_value_logic: str
    helper: str
    action_type: str
    resulting_state: str
    sanction_or_judgment: str
    contribution: str

    is_complete: bool = False
    missing_fields: list[str] = field(default_factory=list)


class EpisodeTrackingValidator:
    """Validates Greimas episode tracking fields."""

    REQUIRED_FIELDS = [
        "subject",
        "object_of_value",
        "current_state",
        "desired_transformation",
        "opponent",
        "opponent_value_logic",
        "action_type",
        "resulting_state",
        "contribution",
    ]

    @classmethod
    def validate_tracking(cls, tracking: dict[str, Any] | Any) -> EpisodeGreimasValidation:
        if hasattr(tracking, "model_dump"):
            tracking = tracking.model_dump()

        missing = []
        for field in cls.REQUIRED_FIELDS:
            val = tracking.get(field, "") if isinstance(tracking, dict) else getattr(tracking, field, "")
            if not val:
                missing.append(field)

        return EpisodeGreimasValidation(
            episode_id=tracking.get("episode_id", "") if isinstance(tracking, dict) else getattr(tracking, "episode_id", ""),
            subject=tracking.get("subject", "") if isinstance(tracking, dict) else getattr(tracking, "subject", ""),
            object_of_value=tracking.get("object_of_value", "") if isinstance(tracking, dict) else getattr(tracking, "object_of_value", ""),
            current_state=tracking.get("current_state", "") if isinstance(tracking, dict) else getattr(tracking, "current_state", ""),
            desired_transformation=tracking.get("desired_transformation", "") if isinstance(tracking, dict) else getattr(tracking, "desired_transformation", ""),
            opponent=tracking.get("opponent", "") if isinstance(tracking, dict) else getattr(tracking, "opponent", ""),
            opponent_value_logic=tracking.get("opponent_value_logic", "") if isinstance(tracking, dict) else getattr(tracking, "opponent_value_logic", ""),
            helper=tracking.get("helper", "") if isinstance(tracking, dict) else getattr(tracking, "helper", ""),
            action_type=tracking.get("action_type", "") if isinstance(tracking, dict) else getattr(tracking, "action_type", ""),
            resulting_state=tracking.get("resulting_state", "") if isinstance(tracking, dict) else getattr(tracking, "resulting_state", ""),
            sanction_or_judgment=tracking.get("sanction_or_judgment", "") if isinstance(tracking, dict) else getattr(tracking, "sanction_or_judgment", ""),
            contribution=tracking.get("contribution", "") if isinstance(tracking, dict) else getattr(tracking, "contribution", ""),
            is_complete=len(missing) == 0,
            missing_fields=missing,
        )
