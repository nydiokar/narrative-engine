"""Smoke tests for contract models."""

from uuid import UUID

import pytest

from src.contracts.models import (
    CanonicalPhase,
    ChapterContract,
    CharacterContract,
    ConflictContract,
    CritiqueContract,
    EpisodeContract,
    ObjectOfValueContract,
    SceneContract,
    StoryContract,
    ThemeContract,
    ValueState,
)


class TestStoryContract:
    def test_default_minimal(self):
        s = StoryContract(title="Test Story", premise="A test premise.")
        assert s.title == "Test Story"
        assert isinstance(s.id, UUID)
        assert s.status.value == "seed"

    def test_actantial_fields(self):
        s = StoryContract(
            title="Test",
            premise="P",
            subject_id="hero",
            object_of_value_type=ValueState.FREEDOM,
            object_of_value_description="escape from bondage",
            sender_id="oracle",
            receiver_id="villagers",
        )
        assert s.object_of_value_type == ValueState.FREEDOM
        assert len(s.helper_ids) == 0


class TestCharacterContract:
    def test_default_minimal(self):
        c = CharacterContract(name="Aragorn")
        assert c.name == "Aragorn"
        assert c.personality.openness == 5

    def test_attahcment(self):
        c = CharacterContract(
            name="Elsa",
            attachment_pattern="fearful_avoidant",
            goal_polarity="leave",
        )
        assert c.goal_polarity.value == "leave"


class TestObjectOfValueContract:
    def test_minimal(self):
        o = ObjectOfValueContract(name="Freedom", type=ValueState.FREEDOM)
        assert o.type == ValueState.FREEDOM


class TestEpisodeContract:
    def test_defaults(self):
        e = EpisodeContract(sequence_number=1)
        assert e.canonical_phase == CanonicalPhase.MANIPULATION


class TestSceneContract:
    def test_defaults(self):
        s = SceneContract(sequence_number=1)
        assert s.status == "draft"
        assert s.conflict_load.internal.value == "none"


class TestChapterContract:
    def test_defaults(self):
        c = ChapterContract(sequence_number=1)
        assert c.status == "outline"


class TestThemeContract:
    def test_defaults(self):
        t = ThemeContract()
        assert len(t.primary_themes) == 0


class TestConflictContract:
    def test_defaults(self):
        c = ConflictContract()
        assert len(c.global_conflicts) == 0


class TestCritiqueContract:
    def test_defaults(self):
        c = CritiqueContract()
        assert c.verdict == "fail"
