"""Tests for TreeExecutor."""
from uuid import uuid4

import pytest

from src.contracts.models import (
    CharacterContract,
    ConflictType,
    EpisodeContract,
    StoryContract,
    WorldContract,
)
from src.tree.executor import BranchConfig, TreeExecutor
from src.tree.node import TreeNode, TreeStore


# ── Helpers ─────────────────────────────────────────────────────────────


def make_minimal_agents():
    """Return a minimal agent registry for executor tests.

    The registry must be non-empty so Director doesn't crash on init.
    """
    return {}


def make_snapshot_with(world=None, characters=None, episodes=None, story=None):
    """Build a snapshot dict in the format ContractStore.restore() expects.

    Each entry needs a "contract" key with the serialized model dump.
    """
    from src.agents.store import get_store, reset_store

    reset_store()
    store = get_store()
    if story:
        store.put("story", story)
    if world:
        store.put("world", world)
    if characters:
        for c in characters:
            store.put("character", c)
    if episodes:
        for e in episodes:
            store.put("episode", e)
    return store.snapshot()


# ── Test promote / prune (pure-tree operations) ────────────────────────


class TestTreeExecutorPromotePrune:
    def test_promote_sets_active(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="", active=True)
        tree.root = root
        child = TreeNode(label="child", checkpoint="final", parent_id=root.id, depth=1)
        tree.add(child)
        root.children.append(child.id)

        executor = TreeExecutor(tree, make_minimal_agents())
        executor.promote(child)
        assert child.active is True
        assert root.active is False

    def test_promote_noop_when_already_active(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="", active=True)
        tree.root = root
        executor = TreeExecutor(tree, make_minimal_agents())
        executor.promote(root)
        assert root.active is True

    def test_prune_removes_subtree(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        child = TreeNode(label="child", checkpoint="final", parent_id=root.id, depth=1)
        tree.add(child)
        root.children.append(child.id)

        executor = TreeExecutor(tree, make_minimal_agents())
        removed = executor.prune(child)
        assert removed == 1
        assert tree.size() == 1

    def test_prune_subtree_reparents_active(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        mid = TreeNode(label="mid", checkpoint="structure", parent_id=root.id, depth=1, active=True)
        tree.add(mid)
        leaf = TreeNode(label="leaf", checkpoint="final", parent_id=mid.id, depth=2)
        tree.add(leaf)
        mid.children.append(leaf.id)
        root.children.append(mid.id)

        executor = TreeExecutor(tree, make_minimal_agents())
        executor.prune(leaf)
        # mid was active and still exists -> active unchanged
        assert tree.get_active() is mid

    def test_prune_active_subtree_reparents_ancestor(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        child = TreeNode(label="child", checkpoint="final", parent_id=root.id, depth=1, active=True)
        tree.add(child)
        root.children.append(child.id)

        executor = TreeExecutor(tree, make_minimal_agents())
        executor.prune(child)
        assert tree.get_active() is root


# ── Test compare (store restoration + summary extraction) ──────────────


class TestTreeExecutorCompare:
    def test_compare_returns_summaries(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="", active=True)
        tree.root = root

        story = StoryContract(title="Test Story", premise="A test premise")
        snapshot = make_snapshot_with(story=story)

        child = TreeNode(
            label="variant",
            checkpoint="final",
            parent_id=root.id,
            depth=1,
            variant_params={"genre": "fantasy"},
            store_snapshot=snapshot,
        )
        tree.add(child)
        root.children.append(child.id)

        executor = TreeExecutor(tree, make_minimal_agents())
        summaries = executor.compare([child])
        assert len(summaries) == 1
        assert summaries[0]["label"] == "variant"
        assert summaries[0]["title"] == "Test Story"
        assert summaries[0]["premise"] == "A test premise"

    def test_compare_includes_scores(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root

        story = StoryContract(title="Test", premise="P")
        child = TreeNode(
            label="a",
            checkpoint="final",
            parent_id=root.id,
            depth=1,
            store_snapshot=make_snapshot_with(story=story),
            scores={"verdict": "pass", "summary": "All good"},
        )
        tree.add(child)
        root.children.append(child.id)

        executor = TreeExecutor(tree, make_minimal_agents())
        summaries = executor.compare([child])
        assert summaries[0]["scores"]["verdict"] == "pass"

    def test_compare_includes_world_dimensions(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root

        world = WorldContract(name="Test World", description="A world")
        story = StoryContract(title="Test", premise="P")
        snapshot = make_snapshot_with(story=story, world=world)
        child = TreeNode(
            label="w",
            checkpoint="final",
            parent_id=root.id,
            depth=1,
            store_snapshot=snapshot,
        )
        tree.add(child)
        root.children.append(child.id)

        executor = TreeExecutor(tree, make_minimal_agents())
        summaries = executor.compare([child])
        assert summaries[0]["world_name"] == "Test World"

    def test_compare_empty_snapshot(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        child = TreeNode(
            label="empty",
            checkpoint="final",
            parent_id=root.id,
            depth=1,
            store_snapshot={},
        )
        tree.add(child)
        root.children.append(child.id)

        executor = TreeExecutor(tree, make_minimal_agents())
        summaries = executor.compare([child])
        assert summaries[0]["label"] == "empty"
        assert "title" not in summaries[0]  # no story contract

    def test_compare_print_does_not_crash(self, capsys):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        story = StoryContract(title="Print Test", premise="Testing compare print")
        child = TreeNode(
            label="printme",
            checkpoint="final",
            parent_id=root.id,
            depth=1,
            store_snapshot=make_snapshot_with(story=story),
        )
        tree.add(child)
        root.children.append(child.id)

        executor = TreeExecutor(tree, make_minimal_agents())
        executor.compare([child])
        captured = capsys.readouterr()
        assert "Print Test" in captured.out
        assert "printme" in captured.out


# ── Test _apply_variant (unit-level, no Director) ──────────────────────


@pytest.fixture
def store():
    """Build a real ContractStore-like fixture via the real store module."""
    from src.agents.store import get_store, reset_store
    reset_store()
    store = get_store()
    store.put("story", StoryContract(title="Base", premise="Original premise"))
    store.put("world", WorldContract(name="Base World", description="Base description"))
    store.put("character", CharacterContract(name="Hero", description="A hero"))
    store.put(
        "episode",
        EpisodeContract(
            title="Ep1",
            sequence_number=0,
            dominant_conflict=ConflictType.INTERPERSONAL,
        ),
    )
    store.put(
        "episode",
        EpisodeContract(
            title="Ep2",
            sequence_number=1,
            dominant_conflict=ConflictType.ENVIRONMENTAL,
        ),
    )
    return store


class TestApplyVariant:
    def test_genre(self, store):
        executor = TreeExecutor(TreeStore(), {})
        executor._apply_variant(store, "genre", "FIC009000", "fantasy")
        stories = store.list_by_type("story")
        assert stories[0].genre.primary_bisac == "FIC009000"

    def test_premise(self, store):
        executor = TreeExecutor(TreeStore(), {})
        executor._apply_variant(store, "premise", "New premise", "new-title")
        stories = store.list_by_type("story")
        assert stories[0].premise == "New premise"
        assert stories[0].title == "new-title"

    def test_tone_noop_without_theme(self, store):
        """Tone variant does nothing if no theme contract exists."""
        executor = TreeExecutor(TreeStore(), {})
        executor._apply_variant(store, "tone", "dark", "dark")
        # No crash is the main test

    def test_world(self, store):
        executor = TreeExecutor(TreeStore(), {})
        executor._apply_variant(store, "world", "high_fantasy", "High Fantasy")
        worlds = store.list_by_type("world")
        assert worlds[0].name == "High Fantasy"
        assert "high_fantasy" in worlds[0].description

    def test_character_sets_name_and_description(self, store):
        executor = TreeExecutor(TreeStore(), {})
        executor._apply_variant(store, "character", "rogue", "Shadow")
        chars = store.list_by_type("character")
        c = chars[0]
        assert c.name == "Shadow"
        assert "rogue" in c.description

    def test_character_uses_value_when_no_label(self, store):
        executor = TreeExecutor(TreeStore(), {})
        executor._apply_variant(store, "character", "wanderer", "wanderer")
        chars = store.list_by_type("character")
        c = chars[0]
        assert c.name == "wanderer"

    def test_conflict(self, store):
        executor = TreeExecutor(TreeStore(), {})
        executor._apply_variant(store, "conflict", "internal", "internal")
        episodes = store.list_by_type("episode")
        assert all(ep.dominant_conflict == ConflictType.INTERNAL for ep in episodes)

    def test_conflict_invalid_value_defaults(self, store):
        executor = TreeExecutor(TreeStore(), {})
        executor._apply_variant(store, "conflict", "bogus", "bogus")
        episodes = store.list_by_type("episode")
        assert all(ep.dominant_conflict == ConflictType.INTERPERSONAL for ep in episodes)

    def test_unknown_vary_field_noop(self, store):
        executor = TreeExecutor(TreeStore(), {})
        executor._apply_variant(store, "unknown", "val", "label")
        stories = store.list_by_type("story")
        assert stories[0].genre.primary_bisac == ""


# ── Test BranchConfig ──────────────────────────────────────────────────


class TestBranchConfig:
    def test_effective_checkpoint_manual(self):
        config = BranchConfig(checkpoint="premise", vary_field="genre", values=["a"])
        assert config.effective_checkpoint == "premise"

    def test_effective_checkpoint_auto(self):
        config = BranchConfig(vary_field="world", values=["a"])
        assert config.effective_checkpoint == "structure"

    def test_effective_checkpoint_default(self):
        config = BranchConfig(vary_field="unknown", values=["a"])
        assert config.effective_checkpoint == "brief"

    def test_values_default(self):
        config = BranchConfig()
        assert config.values is None

    def test_labels_auto_generated(self):
        config = BranchConfig(values=["a", "b"])
        assert config.labels is None


# ── Test _collect_params_to_root ───────────────────────────────────────


class TestCollectParamsToRoot:
    def test_single_node(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="", variant_params={"genre": "fantasy"})
        tree.root = root
        executor = TreeExecutor(tree, {})
        params = executor._collect_params_to_root(root)
        assert params == {"genre": "fantasy"}

    def test_accumulates_up_tree(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="", variant_params={"genre": "fantasy"})
        tree.root = root
        mid = TreeNode(label="mid", checkpoint="structure", parent_id=root.id, depth=1, variant_params={"world": "high"})
        tree.add(mid)
        root.children.append(mid.id)
        leaf = TreeNode(label="leaf", checkpoint="final", parent_id=mid.id, depth=2, variant_params={"character": "heroic"})
        tree.add(leaf)
        mid.children.append(leaf.id)

        executor = TreeExecutor(tree, {})
        params = executor._collect_params_to_root(leaf)
        assert params["genre"] == "fantasy"
        assert params["world"] == "high"
        assert params["character"] == "heroic"

    def test_child_overrides_parent(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="", variant_params={"genre": "fantasy", "tone": "dark"})
        tree.root = root
        child = TreeNode(label="child", checkpoint="final", parent_id=root.id, depth=1, variant_params={"tone": "light"})
        tree.add(child)
        root.children.append(child.id)

        executor = TreeExecutor(tree, {})
        params = executor._collect_params_to_root(child)
        assert params["genre"] == "fantasy"
        assert params["tone"] == "light"  # child overrides

    def test_no_params(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        executor = TreeExecutor(tree, {})
        params = executor._collect_params_to_root(root)
        assert params == {}

    def test_deep_chain(self):
        tree = TreeStore()
        root = TreeNode(label="r", checkpoint="", variant_params={"a": "1"})
        tree.root = root
        n1 = TreeNode(label="n1", checkpoint="", parent_id=root.id, depth=1, variant_params={"b": "2"})
        tree.add(n1)
        root.children.append(n1.id)
        n2 = TreeNode(label="n2", checkpoint="", parent_id=n1.id, depth=2, variant_params={"c": "3"})
        tree.add(n2)
        n1.children.append(n2.id)
        n3 = TreeNode(label="n3", checkpoint="", parent_id=n2.id, depth=3, variant_params={"d": "4"})
        tree.add(n3)
        n2.children.append(n3.id)

        executor = TreeExecutor(tree, {})
        params = executor._collect_params_to_root(n3)
        assert params == {"a": "1", "b": "2", "c": "3", "d": "4"}


# ── Test _find_root_seed ───────────────────────────────────────────────


class TestFindRootSeed:
    def test_root_is_root(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        executor = TreeExecutor(tree, {})
        assert executor._find_root_seed(root) is root

    def test_finds_root_via_parent_chain(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        mid = TreeNode(label="mid", checkpoint="", parent_id=root.id, depth=1)
        tree.add(mid)
        root.children.append(mid.id)
        leaf = TreeNode(label="leaf", checkpoint="", parent_id=mid.id, depth=2)
        tree.add(leaf)
        mid.children.append(leaf.id)

        executor = TreeExecutor(tree, {})
        found = executor._find_root_seed(leaf)
        assert found is root

    def test_orphan_node_returns_root(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        orphan = TreeNode(label="orphan", checkpoint="", parent_id=uuid4(), depth=1)
        tree.add(orphan)

        executor = TreeExecutor(tree, {})
        found = executor._find_root_seed(orphan)
        assert found is root

    def test_empty_tree_returns_current_node(self):
        tree = TreeStore()
        node = TreeNode(label="lonely", checkpoint="")
        executor = TreeExecutor(tree, {})
        found = executor._find_root_seed(node)
        assert found is node


# ── Test _extract_scores ───────────────────────────────────────────────


class TestExtractScores:
    def test_no_critiques(self):
        executor = TreeExecutor(TreeStore(), {})
        from src.agents.store import get_store, reset_store
        reset_store()
        scores = executor._extract_scores(get_store())
        assert scores == {}

    def test_with_critique(self):
        executor = TreeExecutor(TreeStore(), {})
        from src.agents.store import get_store, reset_store
        from src.contracts.models import CritiqueContract
        reset_store()
        store = get_store()
        store.put("critique", CritiqueContract(verdict="pass", summary="Great"))
        scores = executor._extract_scores(store)
        assert scores["verdict"] == "pass"
        assert scores["hard_gate_pass"] is True

    def test_with_failed_critique(self):
        executor = TreeExecutor(TreeStore(), {})
        from src.agents.store import get_store, reset_store
        from src.contracts.models import CritiqueContract
        reset_store()
        store = get_store()
        store.put("critique", CritiqueContract(verdict="fail", summary="Issues found"))
        scores = executor._extract_scores(store)
        assert scores["verdict"] == "fail"
        assert scores["hard_gate_pass"] is False
