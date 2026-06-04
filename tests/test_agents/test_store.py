"""Tests for the contract store."""

from uuid import uuid4

import pytest

from src.agents.store import ContractStore, get_store, reset_store
from src.contracts.models import StoryContract


class TestContractStore:
    def setup_method(self):
        reset_store()

    def test_put_and_get(self):
        store = get_store()
        story = StoryContract(title="Test", premise="A story")
        cid = store.put("story", story)
        retrieved = store.get("story", cid)
        assert retrieved is not None
        assert retrieved.title == "Test"

    def test_history_tracking(self):
        store = get_store()
        story = StoryContract(title="V1", premise="Version 1")
        cid = store.put("story", story, agent="test_agent")
        story.title = "V2"
        store.put("story", story, agent="test_agent")
        history = store.get_history("story", cid)
        assert len(history) == 2
        assert history[0].version == 1
        assert history[1].version == 2

    def test_list_by_type(self):
        store = get_store()
        store.put("story", StoryContract(title="A", premise="P1"))
        store.put("story", StoryContract(title="B", premise="P2"))
        store.put("character", StoryContract(title="C", premise="P3"))
        stories = store.list_by_type("story")
        assert len(stories) == 2

    def test_list_all(self):
        store = get_store()
        store.put("story", StoryContract(title="A", premise="P"))
        store.put("character", StoryContract(title="B", premise="P"))
        all_items = store.list_all()
        assert "story" in all_items
        assert "character" in all_items

    def test_lock_prevents_update(self):
        store = get_store()
        story = StoryContract(title="Locked", premise="Test")
        cid = store.put("story", story)
        store.lock("story", cid)
        # Create a separate contract with the same UUID to simulate LLM output
        import copy
        changed = copy.deepcopy(story)
        changed.title = "Changed"
        returned_cid = store.put("story", changed)
        retrieved = store.get("story", cid)
        assert retrieved.title == "Locked"  # unchanged
        assert returned_cid == cid

    def test_unlock_allows_update(self):
        store = get_store()
        story = StoryContract(title="Locked", premise="Test")
        cid = store.put("story", story)
        store.lock("story", cid)
        store.unlock("story", cid)
        story.title = "Changed"
        store.put("story", story)
        retrieved = store.get("story", cid)
        assert retrieved.title == "Changed"

    def test_subscriber_notified(self):
        store = get_store()
        notifications = []
        store.subscribe(lambda tk, cid, action, agent: notifications.append((tk, cid, action, agent)))
        story = StoryContract(title="Notify", premise="Test")
        cid = store.put("story", story, agent="tester")
        assert len(notifications) == 1
        assert notifications[0][0] == "story"
        assert notifications[0][2] == "created"

    def test_get_nonexistent(self):
        store = get_store()
        result = store.get("story", str(uuid4()))
        assert result is None

    def test_count(self):
        store = get_store()
        assert store.count() == 0
        store.put("story", StoryContract(title="A", premise="P"))
        assert store.count() == 1

    def test_clear(self):
        store = get_store()
        store.put("story", StoryContract(title="A", premise="P"))
        store.clear()
        assert store.count() == 0
