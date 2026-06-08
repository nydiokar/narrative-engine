from __future__ import annotations

from src.contracts.models import (
    CanonicalPhase,
    CharacterContract,
    EpisodeContract,
    StoryContract,
)
from src.engine.golem.event import Event, EventChain, ModalityChange


class GolemEventGenerator:
    """Reads actantial models + modality states → produces typed event sequences.

    Each canonical phase generates a chain of Events that realise the
    structural transformations demanded by the Greimas model. The output
    feeds into the Fabula Coherence Engine for validation.
    """

    @staticmethod
    def generate_manipulation_events(
        story: StoryContract,
        subject_char: CharacterContract | None = None,
    ) -> EventChain:
        chain = EventChain(phase=CanonicalPhase.MANIPULATION)

        # Event 1: Sender proposes contract to Subject
        e1 = Event(
            actant_id=story.sender_id or "sender",
            action_type="propose",
            action_description=f"{story.sender_id or 'Sender'} proposes a contract to {story.subject_id or 'Subject'}",
            goal=f"Contract {story.subject_id or 'Subject'} to obtain {story.object_of_value_description or 'the Object of Value'}",
            state_before="no contract exists",
            state_after="contract proposed",
            value_object_change="contract_introduced",
            outcome="Subject receives the proposal",
            perception="Subject is aware of the offer",
            internal_element="The proposal creates a possibility for the Subject",
            unlocks=f"{story.subject_id or 'Subject'} can now accept or reject",
        )
        chain.add_event(e1)

        # Event 2: Subject desires the Object of Value
        e2 = Event(
            actant_id=story.subject_id or "subject",
            action_type="desire",
            action_description=f"{story.subject_id or 'Subject'} desires {story.object_of_value_description or 'the Object of Value'}",
            goal="Acquire the Object of Value",
            state_before="Subject is indifferent",
            state_after="Subject desires the Object",
            value_object_change="desire_kindled",
            modality_changes=[
                ModalityChange(
                    actant_id=story.subject_id or "subject",
                    modality="wanting",
                    from_state="indifferent",
                    to_state="desires",
                    trigger=f"Exposure to {story.object_of_value_description or 'Object of Value'}",
                ),
            ],
            outcome="Subject wants the Object of Value",
            perception="Subject recognises the Object's worth",
            internal_element="Desire motivates the Subject to act",
            unlocks=f"{story.subject_id or 'Subject'} may now seek the Object",
        )
        chain.add_event(e2)
        chain.add_causal_link(e1.id, e2.id, description="Proposal creates awareness of the Object")

        # Event 3: Subject becomes obligated (via Sender's authority)
        e3 = Event(
            actant_id=story.subject_id or "subject",
            action_type="accept_contract",
            action_description=f"{story.subject_id or 'Subject'} accepts the contract from {story.sender_id or 'Sender'}",
            goal="Accept the mission",
            state_before="Subject has received the proposal",
            state_after="Subject is committed",
            value_object_change="obligation_assumed",
            modality_changes=[
                ModalityChange(
                    actant_id=story.subject_id or "subject",
                    modality="having_to",
                    from_state="free",
                    to_state="obligated",
                    trigger=f"Acceptance of {story.sender_id or 'Sender'}'s contract",
                ),
            ],
            outcome="Subject is now bound by the contract",
            perception="Subject understands the commitment",
            internal_element="Duty now drives the Subject forward",
            unlocks="Subject can now seek competence",
            blocks="Subject cannot turn back without consequence",
        )
        chain.add_event(e3)
        chain.add_causal_link(e2.id, e3.id, description="Desire leads to acceptance of obligation")

        chain.link_previous()
        return chain

    @staticmethod
    def generate_competence_events(
        story: StoryContract,
        subject_char: CharacterContract | None = None,
    ) -> EventChain:
        chain = EventChain(phase=CanonicalPhase.COMPETENCE)

        helpers = story.helper_ids or ["helper"]

        # Event 1: Subject seeks knowledge
        e1 = Event(
            actant_id=story.subject_id or "subject",
            action_type="seek_knowledge",
            action_description=f"{story.subject_id or 'Subject'} seeks knowledge about the Object of Value",
            goal="Acquire necessary knowledge",
            state_before="Subject is ignorant",
            state_after="Subject is informed",
            value_object_change="knowledge_gained",
            modality_changes=[
                ModalityChange(
                    actant_id=story.subject_id or "subject",
                    modality="knowing",
                    from_state="ignorant",
                    to_state="knows",
                    trigger="Research, training, or revelation",
                ),
            ],
            outcome="Subject now knows how to proceed",
            perception="Subject understands the challenge",
            internal_element="Knowledge replaces uncertainty",
            unlocks="Subject can now plan the approach",
        )
        chain.add_event(e1)

        # Event 2: Helper provides ability
        helper_id = helpers[0] if helpers else "helper"
        e2 = Event(
            actant_id=helper_id,
            action_type="grant_ability",
            action_description=f"{helper_id} grants {story.subject_id or 'Subject'} the ability to act",
            goal=f"Empower {story.subject_id or 'Subject'} for the task",
            state_before=f"{story.subject_id or 'Subject'} is unable",
            state_after=f"{story.subject_id or 'Subject'} is able",
            value_object_change="ability_granted",
            modality_changes=[
                ModalityChange(
                    actant_id=story.subject_id or "subject",
                    modality="being_able",
                    from_state="unable",
                    to_state="able",
                    trigger=f"Aid from {helper_id}",
                ),
            ],
            outcome="Subject is now capable of performing the task",
            perception="Subject feels empowered",
            internal_element="Competence builds confidence",
            unlocks="Subject can now confront the Opponent",
        )
        chain.add_event(e2)
        chain.add_causal_link(e1.id, e2.id, description="Knowledge enables the Subject to receive aid")

        # Event 3: Subject demonstrates readiness
        e3 = Event(
            actant_id=story.subject_id or "subject",
            action_type="demonstrate_readiness",
            action_description=f"{story.subject_id or 'Subject'} demonstrates readiness through preparation",
            goal="Prove competence before the performance",
            state_before="Subject has gained abilities",
            state_after="Subject is prepared",
            value_object_change="readiness_achieved",
            outcome="Subject is fully prepared for the performance",
            perception="Subject feels ready",
            internal_element="Confidence replaces doubt",
            unlocks="Performance phase can now begin",
        )
        chain.add_event(e3)
        chain.add_causal_link(e2.id, e3.id, description="Ability enables readiness")

        chain.link_previous()
        return chain

    @staticmethod
    def generate_performance_events(
        story: StoryContract,
        episode: EpisodeContract | None = None,
    ) -> EventChain:
        chain = EventChain(phase=CanonicalPhase.PERFORMANCE)

        opponent_ids = story.opponent_ids or ["opponent"]

        # Event 1: Subject confronts Opponent
        opponent_id = opponent_ids[0] if opponent_ids else "opponent"
        e1 = Event(
            actant_id=story.subject_id or "subject",
            action_type="confront",
            action_description=f"{story.subject_id or 'Subject'} confronts {opponent_id}",
            goal="Overcome the opposing force",
            state_before="Opponent blocks the Subject's path",
            state_after="Opponent is engaged",
            value_object_change="conflict_begun",
            outcome="The central struggle is underway",
            perception="Subject faces the primary obstacle",
            internal_element="The Subject's resolve is tested",
            unlocks="The struggle can now unfold",
            propp_function="struggle",
        )
        chain.add_event(e1)

        # Event 2: Struggle
        e2 = Event(
            actant_id=story.subject_id or "subject",
            action_type="struggle",
            action_description=f"{story.subject_id or 'Subject'} struggles against {opponent_id} over {story.object_of_value_description or 'the Object of Value'}",
            goal="Defeat the Opponent and claim the Object",
            state_before="Outcome uncertain",
            state_after="Victory achieved",
            value_object_change="transferred",
            outcome=f"{story.subject_id or 'Subject'} gains access to {story.object_of_value_description or 'the Object of Value'}",
            perception="Subject perceives the shift in power",
            internal_element="The struggle transforms the Subject",
            unlocks="The Object of Value can now be claimed",
            propp_function="victory",
        )
        chain.add_event(e2)
        chain.add_causal_link(e1.id, e2.id, description="Confrontation leads to struggle")

        # Event 3: Liquidation of lack
        e3 = Event(
            actant_id=story.subject_id or "subject",
            action_type="liquidate_lack",
            action_description=f"{story.subject_id or 'Subject'} liquidates the initial lack by obtaining {story.object_of_value_description or 'the Object of Value'}",
            goal="Fulfil the transformation from disjunction to conjunction",
            state_before=f"Lack of {story.object_of_value_description or 'Object of Value'}",
            state_after=f"{story.object_of_value_description or 'Object of Value'} obtained",
            value_object_change="acquired",
            outcome="The initial lack is resolved",
            perception="Subject now possesses what was missing",
            internal_element="Completion and wholeness",
            unlocks="Sanction phase can now proceed",
            propp_function="liquidation",
        )
        chain.add_event(e3)
        chain.add_causal_link(e2.id, e3.id, description="Victory enables liquidation of lack")

        chain.link_previous()
        return chain

    @staticmethod
    def generate_sanction_events(
        story: StoryContract,
    ) -> EventChain:
        chain = EventChain(phase=CanonicalPhase.SANCTION)

        # Event 1: Sender evaluates the outcome
        e1 = Event(
            actant_id=story.sender_id or "sender",
            action_type="evaluate",
            action_description=f"{story.sender_id or 'Sender'} evaluates {story.subject_id or 'Subject'}'s performance",
            goal="Determine whether the Subject fulfilled the contract",
            state_before="Performance complete, pending judgment",
            state_after="Judgment rendered",
            value_object_change="judgment_rendered",
            outcome="The Sender delivers a verdict",
            perception="The Subject awaits the judgment",
            internal_element="The outcome determines the Subject's final state",
            unlocks="The narrative can reach closure",
        )
        chain.add_event(e1)

        # Event 2: Subject receives sanction (recognition or punishment)
        e2 = Event(
            actant_id=story.subject_id or "subject",
            action_type="receive_sanction",
            action_description=f"{story.subject_id or 'Subject'} receives sanction from {story.sender_id or 'Sender'}",
            goal="Accept the final judgment",
            state_before="Subject is in a state of uncertainty",
            state_after="Subject reaches terminal state",
            value_object_change="sanction_applied",
            outcome="The narrative achieves closure",
            perception="Subject understands the consequences",
            internal_element="The Subject's journey finds its meaning",
            unlocks="Story resolution achieved",
            blocks="Further events would be post-narrative",
            propp_function="recognition",
        )
        chain.add_event(e2)
        chain.add_causal_link(e1.id, e2.id, description="Judgment leads to sanction")

        chain.link_previous()
        return chain

    @staticmethod
    def generate_all_events(
        story: StoryContract,
        episodes: list[EpisodeContract] | None = None,
        characters: list[CharacterContract] | None = None,
    ) -> list[Event]:
        all_events: list[Event] = []
        sequence_counter = 0

        subject_char = None
        if characters and story.subject_id:
            for c in characters:
                if str(c.id) == story.subject_id or c.name == story.subject_id:
                    subject_char = c
                    break

        phase_generators = [
            GolemEventGenerator.generate_manipulation_events,
            GolemEventGenerator.generate_competence_events,
            GolemEventGenerator.generate_performance_events,
            GolemEventGenerator.generate_sanction_events,
        ]

        last_event: Event | None = None

        for gen in phase_generators:
            chain: EventChain
            if gen == GolemEventGenerator.generate_performance_events:
                matching_ep = None
                if episodes:
                    for ep in episodes:
                        if ep.canonical_phase == CanonicalPhase.PERFORMANCE:
                            matching_ep = ep
                            break
                chain = gen(story, matching_ep)
            elif gen in (GolemEventGenerator.generate_manipulation_events, GolemEventGenerator.generate_competence_events):
                chain = gen(story, subject_char)
            else:
                chain = gen(story)

            for event in chain.get_events_sorted():
                event.sequence_number = sequence_counter
                sequence_counter += 1
                if last_event is not None:
                    event.causal_predecessors.append(last_event.id)
                all_events.append(event)
                last_event = event

        return all_events
