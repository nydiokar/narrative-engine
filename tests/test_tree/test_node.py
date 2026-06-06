"""Tests for TreeNode and TreeStore."""
from uuid import UUID, uuid4

from src.tree.node import TreeNode, TreeStore


class TestTreeNode:
    def test_create_root(self):
        node = TreeNode(label="root", checkpoint="")
        assert node.is_root
        assert node.is_leaf
        assert node.depth == 0
        assert node.active is False
        assert isinstance(node.id, UUID)

    def test_create_child(self):
        parent = TreeNode(label="parent", checkpoint="brief")
        child = TreeNode(
            label="fantasy",
            checkpoint="final",
            parent_id=parent.id,
            depth=1,
            variant_params={"genre": "fantasy"},
        )
        assert not child.is_root
        assert child.is_leaf
        assert child.depth == 1
        assert child.parent_id == parent.id

    def test_to_dict_roundtrip(self):
        original = TreeNode(
            label="test",
            checkpoint="premise",
            depth=2,
            variant_params={"genre": "scifi"},
            scores={"verdict": "pass"},
            active=True,
        )
        d = original.to_dict()
        restored = TreeNode.from_dict(d)
        assert restored.id == original.id
        assert restored.label == "test"
        assert restored.checkpoint == "premise"
        assert restored.depth == 2
        assert restored.variant_params == {"genre": "scifi"}
        assert restored.scores == {"verdict": "pass"}
        assert restored.active is True

    def test_to_dict_includes_children(self):
        parent = TreeNode(label="parent", checkpoint="brief")
        child = TreeNode(
            label="child",
            checkpoint="final",
            parent_id=parent.id,
            depth=1,
        )
        parent.children.append(child.id)
        d = parent.to_dict()
        assert len(d["children"]) == 1
        assert UUID(d["children"][0]) == child.id

    def test_from_dict_without_optional_fields(self):
        minimal = {
            "id": str(uuid4()),
            "parent_id": None,
            "depth": 0,
            "checkpoint": "",
            "label": "root",
            "variant_params": {},
            "store_snapshot": {},
            "scores": {},
            "children": [],
            "active": False,
            "created_at": "2025-01-01T00:00:00+00:00",
        }
        node = TreeNode.from_dict(minimal)
        assert node.label == "root"
        assert node.depth == 0
        assert node.children == []


class TestTreeStore:
    def test_empty_store(self):
        tree = TreeStore()
        assert tree.root is None
        assert tree.size() == 0
        assert tree.get_active() is None

    def test_set_root(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        assert tree.root is not None
        assert tree.root.label == "root"
        assert tree.size() == 1

    def test_add_and_get(self):
        tree = TreeStore()
        node = TreeNode(label="fantasy", checkpoint="final")
        tree.add(node)
        retrieved = tree.get(node.id)
        assert retrieved is not None
        assert retrieved.label == "fantasy"

    def test_get_by_label(self):
        tree = TreeStore()
        tree.add(TreeNode(label="a", checkpoint=""))
        tree.add(TreeNode(label="b", checkpoint=""))
        assert tree.get_by_label("a") is not None
        assert tree.get_by_label("b") is not None
        assert tree.get_by_label("nonexistent") is None

    def test_get_by_label_returns_first_match(self):
        tree = TreeStore()
        n1 = TreeNode(label="dup", checkpoint="brief")
        n2 = TreeNode(label="dup", checkpoint="final")
        tree.add(n1)
        tree.add(n2)
        assert tree.get_by_label("dup").checkpoint == "brief"

    def test_active_path(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="", active=True)
        tree.root = root
        assert tree.get_active() is root
        child = TreeNode(label="child", checkpoint="final", parent_id=root.id, depth=1, active=True)
        tree.add(child)
        root.active = False
        assert tree.get_active() is child

    def test_siblings(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        a = TreeNode(label="a", checkpoint="final", parent_id=root.id, depth=1)
        b = TreeNode(label="b", checkpoint="final", parent_id=root.id, depth=1)
        tree.add(a)
        tree.add(b)
        root.children = [a.id, b.id]
        siblings = tree.siblings(a.id)
        assert len(siblings) == 1
        assert siblings[0].label == "b"

    def test_siblings_root(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        assert tree.siblings(root.id) == []

    def test_path_to_root(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        mid = TreeNode(label="mid", checkpoint="structure", parent_id=root.id, depth=1)
        tree.add(mid)
        leaf = TreeNode(label="leaf", checkpoint="final", parent_id=mid.id, depth=2)
        tree.add(leaf)
        mid.children.append(leaf.id)
        root.children.append(mid.id)
        path = tree.path_to_root(leaf.id)
        assert len(path) == 3
        assert path[0].label == "root"
        assert path[1].label == "mid"
        assert path[2].label == "leaf"

    def test_prune_leaf(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        child = TreeNode(label="child", checkpoint="final", parent_id=root.id, depth=1)
        tree.add(child)
        root.children.append(child.id)
        assert tree.size() == 2
        removed = tree.prune(child.id)
        assert removed == 1
        assert tree.size() == 1
        assert root.children == []

    def test_prune_subtree(self):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="")
        tree.root = root
        mid = TreeNode(label="mid", checkpoint="structure", parent_id=root.id, depth=1)
        tree.add(mid)
        leaf = TreeNode(label="leaf", checkpoint="final", parent_id=mid.id, depth=2)
        tree.add(leaf)
        mid.children.append(leaf.id)
        root.children.append(mid.id)
        assert tree.size() == 3
        removed = tree.prune(mid.id)
        assert removed == 2
        assert tree.size() == 1

    def test_prune_root(self):
        tree = TreeStore()
        tree.root = TreeNode(label="root", checkpoint="")
        assert tree.size() == 1
        removed = tree.prune(tree.root.id)
        assert removed == 1
        assert tree.size() == 0
        assert tree.root is None

    def test_prune_nonexistent(self):
        tree = TreeStore()
        tree.root = TreeNode(label="root", checkpoint="")
        removed = tree.prune(uuid4())
        assert removed == 0

    def test_save_and_load_json(self, tmp_path):
        tree = TreeStore()
        root = TreeNode(label="root", checkpoint="", active=True)
        tree.root = root
        child = TreeNode(label="child", checkpoint="final", parent_id=root.id, depth=1)
        tree.add(child)
        root.children.append(child.id)

        path = str(tmp_path / "tree.json")
        tree.save(path)
        loaded = TreeStore()
        loaded.load(path)
        assert loaded.size() == 2
        assert loaded.root is not None
        assert loaded.root.label == "root"
        assert loaded.root.active is True
        child_loaded = loaded.get(child.id)
        assert child_loaded is not None
        assert child_loaded.label == "child"
        assert child_loaded.parent_id == root.id

    def test_clear(self):
        tree = TreeStore()
        tree.root = TreeNode(label="root", checkpoint="")
        tree.add(TreeNode(label="a", checkpoint=""))
        assert tree.size() == 2
        tree.clear()
        assert tree.size() == 0
        assert tree.root is None

    def test_print_tree_does_not_crash(self, capsys):
        tree = TreeStore()
        tree.root = TreeNode(label="root", checkpoint="", active=True)
        child = TreeNode(label="child", checkpoint="final", parent_id=tree.root.id, depth=1)
        tree.add(child)
        tree.root.children.append(child.id)
        tree.print_tree()
        captured = capsys.readouterr()
        assert "root" in captured.out
        assert "child" in captured.out

    def test_print_tree_empty(self, capsys):
        tree = TreeStore()
        tree.print_tree()
        captured = capsys.readouterr()
        assert "empty" in captured.out
