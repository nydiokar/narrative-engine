from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.contracts.models import CanonicalPhase
from src.engine.fabula.causality import CausalityMechanism


class ModalityChange(BaseModel):
    actant_id: str = ""
    modality: str = ""
    from_state: str = ""
    to_state: str = ""
    trigger: str = ""


class CausalLink(BaseModel):
    cause_id: UUID
    effect_id: UUID
    mechanism: CausalityMechanism = CausalityMechanism.PHYSICAL
    description: str = ""


class Event(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    sequence_number: int = 0
    episode_id: UUID | None = None
    phase: CanonicalPhase | None = None

    actant_id: str = ""
    action_type: str = ""
    action_description: str = ""

    goal: str = ""
    outcome: str = ""
    perception: str = ""
    internal_element: str = ""

    state_before: str = ""
    state_after: str = ""
    value_object_change: str = "none"

    modality_changes: list[ModalityChange] = Field(default_factory=list)

    causal_predecessors: list[UUID] = Field(default_factory=list)

    propp_function: str = ""

    unlocks: str = ""
    blocks: str = ""

    def to_dict(self) -> dict:
        d = self.model_dump()
        d["id"] = str(self.id)
        d["episode_id"] = str(self.episode_id) if self.episode_id else None
        d["causal_predecessors"] = [str(p) for p in self.causal_predecessors]
        d["phase"] = self.phase.value if self.phase else None
        return d


class EventChain(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    episode_id: UUID | None = None
    phase: CanonicalPhase | None = None
    events: list[Event] = Field(default_factory=list)
    causal_links: list[CausalLink] = Field(default_factory=list)

    def add_event(self, event: Event) -> None:
        event.sequence_number = len(self.events)
        if self.episode_id and not event.episode_id:
            event.episode_id = self.episode_id
        if self.phase and not event.phase:
            event.phase = self.phase
        self.events.append(event)

    def add_causal_link(
        self,
        cause_id: UUID,
        effect_id: UUID,
        mechanism: CausalityMechanism = CausalityMechanism.PHYSICAL,
        description: str = "",
    ) -> None:
        self.causal_links.append(CausalLink(
            cause_id=cause_id,
            effect_id=effect_id,
            mechanism=mechanism,
            description=description,
        ))

    def link_previous(self, mechanism: CausalityMechanism = CausalityMechanism.PHYSICAL) -> None:
        for i in range(1, len(self.events)):
            prev = self.events[i - 1]
            curr = self.events[i]
            curr.causal_predecessors.append(prev.id)
            self.add_causal_link(prev.id, curr.id, mechanism)

    def get_events_sorted(self) -> list[Event]:
        return sorted(self.events, key=lambda e: e.sequence_number)

    def to_event_dicts(self) -> list[dict]:
        return [e.to_dict() for e in self.get_events_sorted()]

    def validate_complete(self) -> list[str]:
        issues: list[str] = []
        for i, event in enumerate(self.get_events_sorted()):
            if not event.actant_id:
                issues.append(f"Event[{i}] ({event.id}): no actant_id set")
            if not event.action_type:
                issues.append(f"Event[{i}] ({event.id}): no action_type set")
            if event.state_before and event.state_after and event.state_before == event.state_after:
                issues.append(f"Event[{i}] ({event.id}): state did not change")
            if i > 0 and not event.causal_predecessors:
                issues.append(f"Event[{i}] ({event.id}): no causal predecessors — orphan")
        return issues
