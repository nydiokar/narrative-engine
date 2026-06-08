"""Tests for GOLEM Event and EventChain types."""

from uuid import UUID, uuid4

from src.contracts.models import CanonicalPhase
from src.engine.fabula.causality import CausalityMechanism
from src.engine.golem.event import CausalLink, Event, EventChain, ModalityChange


class TestEvent:
    def test_create_event(self):
        e = Event(
            actant_id="hero",
            action_type="confront",
            action_description="Hero confronts the villain",
            goal="Defeat the villain",
            state_before="villain holds the treasure",
            state_after="hero claims the treasure",
            value_object_change="transferred",
        )
        assert isinstance(e.id, UUID)
        assert e.actant_id == "hero"
        assert e.sequence_number == 0
        assert e.phase is None
        assert e.propp_function == ""

    def test_event_with_phase(self):
        e = Event(phase=CanonicalPhase.MANIPULATION, actant_id="sender", action_type="propose")
        assert e.phase == CanonicalPhase.MANIPULATION

    def test_event_with_modality_changes(self):
        e = Event(
            actant_id="hero",
            action_type="train",
            modality_changes=[
                ModalityChange(
                    actant_id="hero",
                    modality="knowing",
                    from_state="ignorant",
                    to_state="knows",
                    trigger="Training montage",
                ),
            ],
        )
        assert len(e.modality_changes) == 1
        assert e.modality_changes[0].to_state == "knows"

    def test_event_to_dict(self):
        e = Event(
            actant_id="hero",
            action_type="confront",
            phase=CanonicalPhase.PERFORMANCE,
        )
        d = e.to_dict()
        assert d["actant_id"] == "hero"
        assert d["phase"] == "performance"
        assert isinstance(d["id"], str)
        assert UUID(d["id"]) == e.id

    def test_event_to_dict_roundtrip(self):
        e = Event(
            actant_id="hero",
            action_type="seek",
            goal="Find the sword",
            outcome="Sword found",
            perception="Hero sees the sword",
            internal_element="Hope kindles",
            causal_predecessors=[uuid4()],
        )
        d = e.to_dict()
        assert len(d["causal_predecessors"]) == 1
        assert isinstance(d["causal_predecessors"][0], str)


class TestEventChain:
    def test_empty_chain(self):
        chain = EventChain()
        assert len(chain.events) == 0
        assert len(chain.get_events_sorted()) == 0

    def test_add_event_assigns_sequence(self):
        chain = EventChain()
        e1 = Event(actant_id="hero", action_type="propose")
        e2 = Event(actant_id="hero", action_type="accept")
        chain.add_event(e1)
        chain.add_event(e2)
        assert e1.sequence_number == 0
        assert e2.sequence_number == 1
        assert len(chain.events) == 2

    def test_add_event_inherits_episode_id(self):
        ep_id = uuid4()
        chain = EventChain(episode_id=ep_id)
        e = Event(actant_id="hero", action_type="act")
        chain.add_event(e)
        assert e.episode_id == ep_id

    def test_add_event_inherits_phase(self):
        chain = EventChain(phase=CanonicalPhase.MANIPULATION)
        e = Event(actant_id="hero", action_type="act")
        chain.add_event(e)
        assert e.phase == CanonicalPhase.MANIPULATION

    def test_add_causal_link(self):
        chain = EventChain()
        cause_id = uuid4()
        effect_id = uuid4()
        chain.add_causal_link(cause_id, effect_id, CausalityMechanism.PSYCHOLOGICAL, "fear drove action")
        assert len(chain.causal_links) == 1
        link = chain.causal_links[0]
        assert link.cause_id == cause_id
        assert link.effect_id == effect_id
        assert link.mechanism == CausalityMechanism.PSYCHOLOGICAL

    def test_link_previous(self):
        chain = EventChain()
        e1 = Event(actant_id="hero", action_type="first")
        e2 = Event(actant_id="hero", action_type="second")
        e3 = Event(actant_id="hero", action_type="third")
        chain.add_event(e1)
        chain.add_event(e2)
        chain.add_event(e3)
        chain.link_previous()
        assert len(e2.causal_predecessors) == 1
        assert e2.causal_predecessors[0] == e1.id
        assert len(e3.causal_predecessors) == 1
        assert e3.causal_predecessors[0] == e2.id
        assert len(e1.causal_predecessors) == 0

    def test_to_event_dicts(self):
        chain = EventChain(phase=CanonicalPhase.COMPETENCE)
        e1 = Event(actant_id="hero", action_type="learn", state_before="ignorant", state_after="knows")
        e2 = Event(actant_id="hero", action_type="train", state_before="weak", state_after="strong")
        chain.add_event(e1)
        chain.add_event(e2)
        dicts = chain.to_event_dicts()
        assert len(dicts) == 2
        assert dicts[0]["action_type"] == "learn"
        assert dicts[1]["sequence_number"] == 1

    def test_validate_complete_missing_actant(self):
        chain = EventChain()
        e = Event(action_type="act")
        chain.add_event(e)
        issues = chain.validate_complete()
        assert any("no actant_id" in i for i in issues)

    def test_validate_complete_missing_action(self):
        chain = EventChain()
        e = Event(actant_id="hero")
        chain.add_event(e)
        issues = chain.validate_complete()
        assert any("no action_type" in i for i in issues)

    def test_validate_complete_state_unchanged(self):
        chain = EventChain()
        e = Event(actant_id="hero", action_type="act", state_before="calm", state_after="calm")
        chain.add_event(e)
        issues = chain.validate_complete()
        assert any("state did not change" in i for i in issues)

    def test_validate_complete_orphan(self):
        chain = EventChain()
        e1 = Event(actant_id="hero", action_type="first")
        e2 = Event(actant_id="hero", action_type="second")
        chain.add_event(e1)
        chain.add_event(e2)
        issues = chain.validate_complete()
        assert any("orphan" in i for i in issues)


class TestCausalLink:
    def test_create_causal_link(self):
        cause = uuid4()
        effect = uuid4()
        link = CausalLink(
            cause_id=cause,
            effect_id=effect,
            mechanism=CausalityMechanism.SOCIAL,
            description="Character betrayed trust",
        )
        assert link.cause_id == cause
        assert link.effect_id == effect
        assert link.mechanism == CausalityMechanism.SOCIAL


class TestCausalLinkDefaults:
    def test_default_mechanism(self):
        cause = uuid4()
        effect = uuid4()
        link = CausalLink(cause_id=cause, effect_id=effect)
        assert link.mechanism == CausalityMechanism.PHYSICAL
