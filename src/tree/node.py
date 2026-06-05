"""Tree node model — a snapshot of story state at a branch point."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


@dataclass
class TreeNode:
    """A node in the story development tree.

    Each node represents a frozen story state (ContractStore snapshot) at a
    specific pipeline checkpoint, reachable by following a specific set of
    variant parameter choices from the root.

    Attributes:
        id: Unique node identifier.
        parent_id: ID of the parent node, or None for the root.
        depth: How many branch operations from root (0 = root).
        checkpoint: Pipeline checkpoint name (brief, premise, structure, etc.).
        label: Human-readable label (e.g. "fantasy", "world-3", "revenge-arc").
        variant_params: What was varied to reach this node
            (e.g. {"genre": "fantasy", "world_seed": 42}).
        store_snapshot: Serialized ContractStore state at this node.
        scores: Evaluation scores for this variant
            (e.g. {"soft_gate": 7.2, "hard_gate_pass": True}).
        children: IDs of child nodes.
        active: Whether this node is the active path.
        created_at: When the node was created.
    """

    id: UUID = field(default_factory=uuid4)
    parent_id: UUID | None = None
    depth: int = 0
    checkpoint: str = ""
    label: str = ""
    variant_params: dict[str, Any] = field(default_factory=dict)
    store_snapshot: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    scores: dict[str, Any] = field(default_factory=dict)
    children: list[UUID] = field(default_factory=list)
    active: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_root(self) -> bool:
        return self.parent_id is None

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def to_dict(self) -> dict[str, Any]:
        d = {
            "id": str(self.id),
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "depth": self.depth,
            "checkpoint": self.checkpoint,
            "label": self.label,
            "variant_params": self.variant_params,
            "store_snapshot": self.store_snapshot,
            "scores": self.scores,
            "children": [str(c) for c in self.children],
            "active": self.active,
            "created_at": self.created_at.isoformat(),
        }
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TreeNode:
        return cls(
            id=UUID(d["id"]),
            parent_id=UUID(d["parent_id"]) if d.get("parent_id") else None,
            depth=d["depth"],
            checkpoint=d.get("checkpoint", ""),
            label=d.get("label", ""),
            variant_params=d.get("variant_params", {}),
            store_snapshot=d.get("store_snapshot", {}),
            scores=d.get("scores", {}),
            children=[UUID(c) for c in d.get("children", [])],
            active=d.get("active", False),
            created_at=datetime.fromisoformat(d["created_at"]) if "created_at" in d else datetime.now(timezone.utc),
        )


class TreeStore:
    """In-memory registry of all tree nodes + active path tracking."""

    def __init__(self) -> None:
        self._nodes: dict[UUID, TreeNode] = {}
        self._root_id: UUID | None = None

    @property
    def root(self) -> TreeNode | None:
        return self._nodes.get(self._root_id) if self._root_id else None

    @root.setter
    def root(self, node: TreeNode) -> None:
        self._root_id = node.id
        self._nodes[node.id] = node

    def add(self, node: TreeNode) -> None:
        self._nodes[node.id] = node

    def get(self, node_id: UUID) -> TreeNode | None:
        return self._nodes.get(node_id)

    def get_by_label(self, label: str) -> TreeNode | None:
        for node in self._nodes.values():
            if node.label == label:
                return node
        return None

    def get_active(self) -> TreeNode | None:
        for node in self._nodes.values():
            if node.active:
                return node
        return None

    def siblings(self, node_id: UUID) -> list[TreeNode]:
        node = self.get(node_id)
        if not node or not node.parent_id:
            return []
        parent = self.get(node.parent_id)
        if not parent:
            return []
        return [self.get(cid) for cid in parent.children if cid != node_id and self.get(cid) is not None]

    def path_to_root(self, node_id: UUID) -> list[TreeNode]:
        path: list[TreeNode] = []
        current = self.get(node_id)
        while current:
            path.append(current)
            current = self.get(current.parent_id) if current.parent_id else None
        path.reverse()
        return path

    def save(self, path: str) -> None:
        import json
        data = {
            "root_id": str(self._root_id) if self._root_id else None,
            "nodes": {str(k): v.to_dict() for k, v in self._nodes.items()},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: str) -> None:
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._nodes = {}
        for nid_str, node_dict in data["nodes"].items():
            node = TreeNode.from_dict(node_dict)
            self._nodes[node.id] = node
        root_str = data.get("root_id")
        self._root_id = UUID(root_str) if root_str else None

    def prune(self, node_id: UUID) -> int:
        """Remove a node and all its descendants from the tree.

        Returns the total number of nodes removed.
        """
        node = self.get(node_id)
        if not node:
            return 0

        # Collect all descendant IDs via BFS
        to_delete: set[UUID] = {node_id}
        queue = list(node.children)
        while queue:
            current = self.get(queue.pop(0))
            if current:
                to_delete.add(current.id)
                queue.extend(current.children)

        # Remove from parent's children list
        if node.parent_id:
            parent = self.get(node.parent_id)
            if parent:
                parent.children = [cid for cid in parent.children if cid != node_id]

        # Delete all collected nodes
        for nid in to_delete:
            self._nodes.pop(nid, None)

        # If root was pruned, clear the root
        if node_id == self._root_id:
            self._root_id = None

        return len(to_delete)

    def print_tree(self, node_id: UUID | None = None, prefix: str = "", is_last: bool = True) -> None:
        """Print an ASCII tree visualization starting from the given node.

        If node_id is None, starts from the root.
        Uses ASCII characters for cross-platform compatibility.
        """
        if node_id is None:
            node = self.root
        else:
            node = self.get(node_id)

        if not node:
            print("(empty tree)")
            return

        # Print current node
        connector = "+-- " if is_last else "|-- "
        active_marker = " [active]" if node.active else ""
        label_part = f"({node.label})" if node.label else f"({str(node.id)[:8]}...)"
        depth_part = f" d={node.depth}" if node.depth > 0 else ""
        checkpoint_part = f" @{node.checkpoint}" if node.checkpoint else ""
        print(f"{prefix}{connector}{label_part}{checkpoint_part}{depth_part}{active_marker}")

        # Print children
        if node.children:
            child_prefix = prefix + ("    " if is_last else "|   ")
            for i, cid in enumerate(node.children):
                c = self.get(cid)
                if c:
                    self.print_tree(c.id, child_prefix, i == len(node.children) - 1)

    def size(self) -> int:
        return len(self._nodes)

    def clear(self) -> None:
        self._nodes.clear()
        self._root_id = None
