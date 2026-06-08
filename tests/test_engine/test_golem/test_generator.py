"""Tests for GOLEM event generator — actantial model → event sequences."""

from src.contracts.models import CanonicalPhase, CharacterContract, EpisodeContract, StoryContract
from src.engine.golem.generator import GolemEventGenerator


def _make_story(**overrides) -> StoryContract:
    kwargs = dict(
        title="Test Story",
        premise="A hero's journey",
        subject_id="hero",
        object_of_value_id="the_crown",
        object_of_value_description="the lost crown",
        object_of_value_type="power",
        sender_id="sage",
        receiver_id="hero",
        helper_ids=["ally"],
        opponent_ids=["villain"],
    )
    kwargs.update(overrides)
    return StoryContract(**kwargs)


class TestGolemGeneratorManipulation:
    def test_generates_three_events(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_manipulation_events(story)
        events = chain.get_events_sorted()
        assert len(events) == 3

    def test_first_event_is_propose(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_manipulation_events(story)
        events = chain.get_events_sorted()
        assert events[0].action_type == "propose"
        assert events[0].actant_id == "sage"

    def test_second_event_has_modality_change(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_manipulation_events(story)
        events = chain.get_events_sorted()
        assert events[1].action_type == "desire"
        assert any(mc.modality == "wanting" and mc.to_state == "desires" for mc in events[1].modality_changes)

    def test_third_event_creates_obligation(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_manipulation_events(story)
        events = chain.get_events_sorted()
        assert events[2].action_type == "accept_contract"
        assert any(mc.modality == "having_to" and mc.to_state == "obligated" for mc in events[2].modality_changes)

    def test_all_events_have_goal_outcome_perception_internal(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_manipulation_events(story)
        for event in chain.get_events_sorted():
            assert event.goal, f"Event {event.action_type} missing goal"
            assert event.outcome, f"Event {event.action_type} missing outcome"
            assert event.perception, f"Event {event.action_type} missing perception"
            assert event.internal_element, f"Event {event.action_type} missing internal_element"

    def test_causal_links_present(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_manipulation_events(story)
        events = chain.get_events_sorted()
        assert len(events[1].causal_predecessors) >= 1
        assert len(events[2].causal_predecessors) >= 1

    def test_chain_phase_is_correct(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_manipulation_events(story)
        assert chain.phase == CanonicalPhase.MANIPULATION

    def test_all_events_inherit_phase(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_manipulation_events(story)
        for event in chain.get_events_sorted():
            assert event.phase == CanonicalPhase.MANIPULATION


class TestGolemGeneratorCompetence:
    def test_generates_three_events(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_competence_events(story)
        events = chain.get_events_sorted()
        assert len(events) == 3

    def test_first_event_gains_knowledge(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_competence_events(story)
        e1 = chain.get_events_sorted()[0]
        assert e1.action_type == "seek_knowledge"
        assert any(mc.modality == "knowing" and mc.to_state == "knows" for mc in e1.modality_changes)

    def test_second_event_grants_ability(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_competence_events(story)
        e2 = chain.get_events_sorted()[1]
        assert e2.action_type == "grant_ability"
        assert e2.actant_id == "ally"
        assert any(mc.modality == "being_able" and mc.to_state == "able" for mc in e2.modality_changes)

    def test_third_event_demonstrates_readiness(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_competence_events(story)
        e3 = chain.get_events_sorted()[2]
        assert e3.action_type == "demonstrate_readiness"

    def test_with_subject_character(self):
        story = _make_story()
        char = CharacterContract(
            name="hero",
            description="The hero of the story",
            core_desires=["power"],
        )
        chain = GolemEventGenerator.generate_competence_events(story, char)
        assert len(chain.get_events_sorted()) == 3

    def test_golem_fields_present(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_competence_events(story)
        for event in chain.get_events_sorted():
            assert event.goal
            assert event.outcome
            assert event.perception
            assert event.internal_element


class TestGolemGeneratorPerformance:
    def test_generates_three_events(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_performance_events(story)
        events = chain.get_events_sorted()
        assert len(events) == 3

    def test_first_event_confronts(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_performance_events(story)
        e1 = chain.get_events_sorted()[0]
        assert e1.action_type == "confront"
        assert e1.propp_function == "struggle"

    def test_second_event_struggles(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_performance_events(story)
        e2 = chain.get_events_sorted()[1]
        assert e2.action_type == "struggle"
        assert e2.propp_function == "victory"
        assert e2.value_object_change == "transferred"

    def test_third_event_liquidates_lack(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_performance_events(story)
        e3 = chain.get_events_sorted()[2]
        assert e3.action_type == "liquidate_lack"
        assert e3.propp_function == "liquidation"

    def test_with_episode(self):
        story = _make_story()
        ep = EpisodeContract(
            title="The Final Battle",
            sequence_number=3,
            canonical_phase=CanonicalPhase.PERFORMANCE,
        )
        chain = GolemEventGenerator.generate_performance_events(story, ep)
        assert len(chain.get_events_sorted()) == 3

    def test_propp_functions_are_set(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_performance_events(story)
        for e in chain.get_events_sorted():
            assert e.propp_function


class TestGolemGeneratorSanction:
    def test_generates_two_events(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_sanction_events(story)
        events = chain.get_events_sorted()
        assert len(events) == 2

    def test_first_event_evaluates(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_sanction_events(story)
        e1 = chain.get_events_sorted()[0]
        assert e1.action_type == "evaluate"
        assert e1.actant_id == "sage"

    def test_second_event_receives_sanction(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_sanction_events(story)
        e2 = chain.get_events_sorted()[1]
        assert e2.action_type == "receive_sanction"
        assert e2.propp_function == "recognition"

    def test_blocks_set_on_final_event(self):
        story = _make_story()
        chain = GolemEventGenerator.generate_sanction_events(story)
        e2 = chain.get_events_sorted()[1]
        assert e2.blocks


class TestGolemGeneratorAll:
    def test_generate_all_produces_11_events(self):
        story = _make_story()
        events = GolemEventGenerator.generate_all_events(story)
        assert len(events) == 11  # 3 + 3 + 3 + 2

    def test_all_events_have_unique_ids(self):
        story = _make_story()
        events = GolemEventGenerator.generate_all_events(story)
        ids = [e.id for e in events]
        assert len(set(ids)) == len(ids)

    def test_all_events_have_sequence_numbers(self):
        story = _make_story()
        events = GolemEventGenerator.generate_all_events(story)
        for i, e in enumerate(events):
            assert e.sequence_number == i

    def test_all_events_have_actant_id(self):
        story = _make_story()
        events = GolemEventGenerator.generate_all_events(story)
        for e in events:
            assert e.actant_id, f"Event {e.sequence_number} missing actant_id"

    def test_all_events_have_action_type(self):
        story = _make_story()
        events = GolemEventGenerator.generate_all_events(story)
        for e in events:
            assert e.action_type, f"Event {e.sequence_number} missing action_type"

    def test_all_events_have_golem_fields(self):
        story = _make_story()
        events = GolemEventGenerator.generate_all_events(story)
        for e in events:
            assert e.goal, f"Event {e.sequence_number} ({e.action_type}) missing goal"
            assert e.outcome, f"Event {e.sequence_number} ({e.action_type}) missing outcome"
            assert e.perception, f"Event {e.sequence_number} ({e.action_type}) missing perception"
            assert e.internal_element, f"Event {e.sequence_number} ({e.action_type}) missing internal_element"

    def test_all_events_have_causal_predecessors_except_first(self):
        story = _make_story()
        events = GolemEventGenerator.generate_all_events(story)
        for i, e in enumerate(events):
            if i > 0:
                assert len(e.causal_predecessors) >= 1, f"Event {i} ({e.action_type}) has no causal predecessors"

    def test_to_dict_all(self):
        story = _make_story()
        events = GolemEventGenerator.generate_all_events(story)
        dicts = [e.to_dict() for e in events]
        assert len(dicts) == 11
        assert all(d["phase"] for d in dicts)

    def test_with_characters(self):
        story = _make_story()
        char = CharacterContract(name="hero", description="The hero")
        events = GolemEventGenerator.generate_all_events(story, characters=[char])
        assert len(events) == 11

    def test_with_episodes(self):
        story = _make_story()
        ep = EpisodeContract(title="Manipulation", canonical_phase=CanonicalPhase.MANIPULATION)
        events = GolemEventGenerator.generate_all_events(story, episodes=[ep])
        assert len(events) == 11

    def test_no_subject_fallback(self):
        story = _make_story(subject_id="")
        events = GolemEventGenerator.generate_all_events(story)
        assert len(events) == 11
        # All events should have some actant fallback
        for e in events:
            assert e.actant_id

    def test_no_sender_fallback(self):
        story = _make_story(sender_id="")
        events = GolemEventGenerator.generate_all_events(story)
        assert len(events) == 11


class TestGolemIntegration:
    def test_golem_events_pass_coherence_golem_check(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine

        story = _make_story()
        events = GolemEventGenerator.generate_all_events(story)
        golem_dicts = [e.to_dict() for e in events]

        report = FabulaCoherenceEngine.run_all_checks(golem_events=golem_dicts)
        golem_check = [c for c in report.checks if c.name == "golem_event_validation"]
        assert len(golem_check) == 1
        assert golem_check[0].passed is True

    def test_golem_events_with_missing_fields_fail_check(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine

        bad_events = [
            {"id": "bad1", "action_type": "act"},
        ]
        report = FabulaCoherenceEngine.run_all_checks(golem_events=bad_events)
        golem_check = [c for c in report.checks if c.name == "golem_event_validation"]
        assert len(golem_check) == 1
        assert golem_check[0].passed is False

    def test_golem_events_with_all_fields_pass_check(self):
        from src.engine.fabula.coherence import FabulaCoherenceEngine

        good_events = [
            {
                "id": "good1",
                "goal": "Find the artifact",
                "action_type": "seek",
                "outcome": "Found it",
                "perception": "Sees it glow",
                "internal_element": "Hope rises",
            },
        ]
        report = FabulaCoherenceEngine.run_all_checks(golem_events=good_events)
        golem_check = [c for c in report.checks if c.name == "golem_event_validation"]
        assert golem_check[0].passed is True
