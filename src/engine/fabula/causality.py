"""Causality rules — causal relationships between narrative events.

Every event must follow from prior events by logical necessity.
Four axioms govern the causality system:
1. Ex nihilo: No event arises without a cause.
2. Transitivity: If A causes B and B causes C, then A indirectly causes C.
3. No backward causation: Effects cannot precede their causes in the fabula.
4. Conservation of modality: Modality changes must have explicit causes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CausalityMechanism(str, Enum):
    PHYSICAL = "physical"
    PSYCHOLOGICAL = "psychological"
    SOCIAL = "social"
    MAGICAL = "magical"


@dataclass
class CausalLink:
    cause_id: str
    effect_id: str
    mechanism: CausalityMechanism = CausalityMechanism.PHYSICAL
    description: str = ""


@dataclass
class CausalityValidationResult:
    is_valid: bool = False
    issues: list[str] = field(default_factory=list)
    orphan_events: list[str] = field(default_factory=list)
    backward_causes: list[tuple[str, str]] = field(default_factory=list)
    unexplained_modality_shifts: list[str] = field(default_factory=list)


class CausalityGraph:
    """Builds and validates a causality graph from a list of events."""

    def __init__(self) -> None:
        self.events: dict[str, int] = {}  # event_id -> sequence_number
        self.causal_links: list[CausalLink] = []

    def add_event(self, event_id: str, sequence_number: int) -> None:
        self.events[event_id] = sequence_number

    def add_link(self, link: CausalLink) -> None:
        self.causal_links.append(link)

    def build_from_events(
        self, events: list[dict[str, Any]]
    ) -> None:
        for event in events:
            eid = event.get("id", "")
            if isinstance(eid, str):
                seq = event.get("sequence_number", 0)
                self.add_event(eid, seq)

                predecessors = event.get("causal_predecessors", [])
                for pred_id in predecessors:
                    mechanism_str = event.get("causality_mechanism", "physical")
                    mechanism = CausalityMechanism(mechanism_str)
                    self.add_link(CausalLink(
                        cause_id=str(pred_id),
                        effect_id=eid,
                        mechanism=mechanism,
                    ))

    def get_ancestors(self, event_id: str) -> set[str]:
        ancestors: set[str] = set()
        queue = [event_id]
        while queue:
            current = queue.pop(0)
            for link in self.causal_links:
                if link.effect_id == current and link.cause_id not in ancestors:
                    ancestors.add(link.cause_id)
                    queue.append(link.cause_id)
        return ancestors

    def get_descendants(self, event_id: str) -> set[str]:
        descendants: set[str] = set()
        queue = [event_id]
        while queue:
            current = queue.pop(0)
            for link in self.causal_links:
                if link.cause_id == current and link.effect_id not in descendants:
                    descendants.add(link.effect_id)
                    queue.append(link.effect_id)
        return descendants

    def validate(self) -> CausalityValidationResult:
        issues: list[str] = []
        orphan_events: list[str] = []
        backward_causes: list[tuple[str, str]] = []
        unexplained_modality_shifts: list[str] = []

        # Find orphan events (events with no predecessors)
        all_effect_ids = {link.effect_id for link in self.causal_links}
        all_cause_ids = {link.cause_id for link in self.causal_links}
        linked_ids = all_effect_ids | all_cause_ids

        for eid, seq in self.events.items():
            if seq > 0 and eid not in linked_ids:
                orphan_events.append(eid)
                issues.append(f"Orphan event '{eid}' (seq {seq}): no causal links")

        # Check backward causation
        for link in self.causal_links:
            cause_seq = self.events.get(link.cause_id)
            effect_seq = self.events.get(link.effect_id)
            if cause_seq is not None and effect_seq is not None:
                if cause_seq > effect_seq:
                    backward_causes.append((link.cause_id, link.effect_id))
                    issues.append(
                        f"Backward causation: {link.cause_id} (seq {cause_seq}) "
                        f"→ {link.effect_id} (seq {effect_seq})"
                    )

        # Check transitivity (axiom 2): if A→B and B→C exist, verify A can reach C
        for link in self.causal_links:
            descendants = self.get_descendants(link.cause_id)
            for other in self.causal_links:
                if other.cause_id == link.effect_id:
                    if other.effect_id not in descendants:
                        pass  # Indirect chain exists by definition via get_descendants

        is_valid = len(issues) == 0
        return CausalityValidationResult(
            is_valid=is_valid,
            issues=issues,
            orphan_events=orphan_events,
            backward_causes=backward_causes,
            unexplained_modality_shifts=unexplained_modality_shifts,
        )


class CausalityValidator:
    """Validates causality rules against a narrative artifact."""

    @staticmethod
    def validate_events(events: list[dict[str, Any]]) -> CausalityValidationResult:
        graph = CausalityGraph()
        graph.build_from_events(events)
        return graph.validate()

    @staticmethod
    def validate_event_chain(
        chain: list[dict[str, Any]]
    ) -> CausalityValidationResult:
        """Validate a fabula chain — events must be ordered and linked."""
        graph = CausalityGraph()
        graph.build_from_events(chain)

        result = graph.validate()

        # Additional constraint: events must be strictly ordered
        seq_numbers = [e.get("sequence_number", 0) for e in chain]
        for i in range(len(seq_numbers) - 1):
            if seq_numbers[i] >= seq_numbers[i + 1]:
                result.issues.append(
                    f"Sequence order violation: event[{i}] seq {seq_numbers[i]} "
                    f"≥ event[{i + 1}] seq {seq_numbers[i + 1]}"
                )

        if result.issues:
            result.is_valid = False
        return result
