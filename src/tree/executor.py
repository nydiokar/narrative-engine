"""Tree executor — branch, compare, promote operations.

Each branch creates N children by reconstructing the full parameter path
from root to parent, applying all variant params, and running the pipeline
from scratch. This avoids stale-contract issues in multi-depth trees.
"""

from __future__ import annotations

from dataclasses import dataclass
from logging import Logger
from typing import Any
from uuid import UUID, uuid4

from src.agents.director import Director, _ALL_WORKFLOW_IDS
from src.agents.store import ContractStore, get_store, reset_store
from src.contracts.models import Medium, StoryContract
from src.pipeline.checkpoints import (
    CHECKPOINT_ORDER,
    WORKFLOW_FOR_CHECKPOINT,
    run_to_checkpoint,
)
from src.tree.node import TreeNode, TreeStore


# Mapping: vary_field → checkpoint to re-run from
_VARY_FROM_CHECKPOINT: dict[str, str] = {
    "genre": "brief",
    "tone": "brief",
    "theme": "brief",
    "premise": "premise",
    "world": "structure",
    "character": "episodes",
    "conflict": "episodes",
    "seed": "brief",
}


@dataclass
class BranchConfig:
    """Configuration for a branch operation.

    Attributes:
        checkpoint: Which pipeline checkpoint to branch from
            ("brief", "premise", "structure", "episodes", etc).
            If empty, auto-detected from vary_field.
        vary_field: What to vary between variants
            ("genre", "seed", "premise", "tone", "world", "character").
        values: List of values to try (one per variant).
        medium: Output medium for the pipeline.
        labels: Optional human-readable labels (one per value).
            Auto-generated from values if not provided.
        target_checkpoint: Where to stop running ("final" by default).
    """
    checkpoint: str = ""
    vary_field: str = "genre"
    values: list[str] = None
    medium: Medium = Medium.BOOK
    labels: list[str] = None
    target_checkpoint: str = "final"

    @property
    def effective_checkpoint(self) -> str:
        """Return the resolved checkpoint, auto-detected from vary_field if not set."""
        if self.checkpoint:
            return self.checkpoint
        return _VARY_FROM_CHECKPOINT.get(self.vary_field, "brief")


class TreeExecutor:
    """Orchestrates tree operations on the story development tree.

    Usage:
        executor = TreeExecutor(tree_store, agent_registry)
        children = executor.branch(parent_node, config)
        executor.compare(children)
        executor.promote(child_node)
    """

    def __init__(
        self,
        tree: TreeStore,
        agent_registry: dict[str, Any],
        logger: Logger | None = None,
    ) -> None:
        self.tree = tree
        self.agents = agent_registry
        self.logger = logger

    def _collect_params_to_root(self, node: TreeNode) -> dict[str, Any]:
        """Walk from node up to root, collecting all variant_params.

        Earlier params (closer to root) are overridden by later ones
        (closer to the node), which is the correct semantics.
        """
        params: dict[str, Any] = {}
        current = node
        while current:
            params.update(current.variant_params)
            current = self.tree.get(current.parent_id) if current.parent_id else None
        return params

    def _find_root_seed(self, node: TreeNode) -> TreeNode:
        """Walk up to the root node."""
        current = node
        root = self.tree.root
        while current.parent_id:
            parent = self.tree.get(current.parent_id)
            if not parent:
                break
            current = parent
        return root or current

    def branch(
        self,
        parent: TreeNode,
        config: BranchConfig,
    ) -> list[TreeNode]:
        """Create N children from a parent by varying parameters.

        Strategy: for each variant value:
        1. Go up to the root and collect ALL params (ancestor path)
        2. Restore the root's store (which is the seed state)
        3. Apply ancestor params + the new variant param
        4. Run the full pipeline from config.checkpoint forward
        5. Snapshot into a child TreeNode
        """
        if config.values is None:
            config.values = ["default"]
        labels = config.labels or [str(v) for v in config.values]
        if len(labels) != len(config.values):
            labels = [str(v) for v in config.values]

        # Collect all params from the parent path
        inherited_params = self._collect_params_to_root(parent)

        # Find root node with the seed store
        root = self._find_root_seed(parent)
        if not root or not root.store_snapshot:
            msg = "Cannot branch: root node has no store snapshot"
            raise RuntimeError(msg)

        children: list[TreeNode] = []

        for i, value in enumerate(config.values):
            label = labels[i] if i < len(labels) else str(value)

            # Fresh store from root seed
            reset_store()
            store = get_store()
            store.restore(root.store_snapshot)

            # Apply ALL params: inherited + new variant
            all_params = dict(inherited_params)
            all_params[config.vary_field] = value
            for field, val in all_params.items():
                self._apply_variant(store, field, val, label)

            # Build director and run
            director = Director(
                self.agents,
                store=store,
                medium=config.medium,
            )

            # Run pipeline from the resolved checkpoint forward
            self._run_from_checkpoint(
                director,
                config.effective_checkpoint,
                config.target_checkpoint,
            )

            # Snapshot result
            child_snapshot = store.snapshot()

            # Extract scores
            scores = self._extract_scores(store)

            child = TreeNode(
                id=uuid4(),
                parent_id=parent.id,
                depth=parent.depth + 1,
                checkpoint=config.target_checkpoint,
                label=label,
                variant_params={config.vary_field: value, **inherited_params},
                store_snapshot=child_snapshot,
                scores=scores,
                active=False,
            )

            self.tree.add(child)
            parent.children.append(child.id)
            children.append(child)

        return children

    def compare(self, nodes: list[TreeNode]) -> list[dict[str, Any]]:
        """Compare sibling nodes side-by-side.

        Returns a list of dicts with key contract data for each node.
        Also prints a human-readable comparison table.
        """
        summaries = []
        for node in nodes:
            store = ContractStore()
            store.restore(node.store_snapshot)

            summary = {
                "label": node.label,
                "checkpoint": node.checkpoint,
                "variant_params": node.variant_params,
                "scores": node.scores,
            }

            stories = store.list_by_type("story")
            if stories:
                s = stories[0]
                d = s.model_dump(mode="json") if hasattr(s, "model_dump") else {}
                summary["premise"] = (d.get("premise") or "")[:80]
                summary["genre"] = d.get("genre", {}).get("primary_bisac", "?")
                summary["title"] = d.get("title", "?")

            characters = store.list_by_type("character")
            if characters:
                c = characters[0]
                cd = c.model_dump(mode="json") if hasattr(c, "model_dump") else {}
                summary["protagonist"] = cd.get("name", "?")
                summary["protagonist_role"] = cd.get("actant_roles", [])

            worlds = store.list_by_type("world")
            if worlds:
                w = worlds[0]
                wd = w.model_dump(mode="json") if hasattr(w, "model_dump") else {}
                summary["world_name"] = wd.get("name", "?")
                summary["world_axes"] = wd.get("axes", [])

            critiques = store.list_by_type("critique")
            if critiques:
                cr = critiques[-1]
                crd = cr.model_dump(mode="json") if hasattr(cr, "model_dump") else {}
                summary["critique_verdict"] = crd.get("verdict", "?")
                summary["critique_summary"] = (crd.get("summary") or "")[:80]

            summaries.append(summary)

        self._print_comparison(summaries)
        return summaries

    def promote(self, node: TreeNode) -> None:
        """Mark a node as the active path."""
        current_active = self.tree.get_active()
        if current_active:
            current_active.active = False
        node.active = True

    def _apply_variant(
        self,
        store: ContractStore,
        vary_field: str,
        value: str,
        label: str,
    ) -> None:
        """Modify store contracts to reflect a variant parameter."""
        if vary_field == "genre":
            stories = store.list_by_type("story")
            if stories:
                story = stories[0]
                if hasattr(story, "genre") and story.genre:
                    story.genre.primary_bisac = value
                    story.genre.secondary_bisac = story.genre.secondary_bisac or ""
                    store.put("story", story, agent="tree_branch")
        elif vary_field == "premise":
            stories = store.list_by_type("story")
            if stories:
                story = stories[0]
                if hasattr(story, "premise"):
                    story.premise = value
                    store.put("story", story, agent="tree_branch")
                if hasattr(story, "title") and label:
                    story.title = label
                    store.put("story", story, agent="tree_branch")
        elif vary_field == "tone":
            themes = store.list_by_type("theme")
            if themes:
                theme = themes[0]
                if hasattr(theme, "tone"):
                    theme.tone = value
                    store.put("theme", theme, agent="tree_branch")

    def _run_from_checkpoint(
        self,
        director: Director,
        from_checkpoint: str,
        to_checkpoint: str,
    ) -> None:
        """Run pipeline workflows from one checkpoint to another.

        Runs from ``from_checkpoint`` (inclusive) through ``to_checkpoint``.
        If from_checkpoint is empty ("seed"), runs from the beginning.
        """
        start_idx = 0
        if from_checkpoint in CHECKPOINT_ORDER:
            start_idx = CHECKPOINT_ORDER.index(from_checkpoint)

        end_idx = len(CHECKPOINT_ORDER) - 1
        if to_checkpoint in CHECKPOINT_ORDER:
            end_idx = CHECKPOINT_ORDER.index(to_checkpoint)

        for idx in range(start_idx, end_idx + 1):
            ck_name = CHECKPOINT_ORDER[idx]
            wid = WORKFLOW_FOR_CHECKPOINT.get(ck_name)
            if wid and wid in director.registry:
                director.run_workflow(wid)

    def _extract_scores(self, store: ContractStore) -> dict[str, Any]:
        """Extract evaluation scores from critique contracts."""
        scores: dict[str, Any] = {}
        critiques = store.list_by_type("critique")
        if critiques:
            last = critiques[-1]
            d = last.model_dump(mode="json") if hasattr(last, "model_dump") else {}
            scores["verdict"] = d.get("verdict", "?")
            scores["summary"] = (d.get("summary") or "")[:100]
            scores["hard_gate_pass"] = d.get("verdict") == "pass"
        return scores

    def _print_comparison(self, summaries: list[dict[str, Any]]) -> None:
        """Print a human-readable side-by-side comparison."""
        sep = "-" * 72
        print(f"\n{sep}")
        print(f"  SIDE-BY-SIDE COMPARISON ({len(summaries)} variants)")
        print(f"{sep}")

        for s in summaries:
            print(f"\n  [{s['label']}]")
            print(f"    Checkpoint:   {s['checkpoint']}")
            print(f"    Params:       {s['variant_params']}")
            print(f"    Title:        {s.get('title', '?')}")
            genre = s.get("genre", "")
            if genre:
                print(f"    Genre:        {genre}")
            premise = s.get("premise", "")
            if premise:
                print(f"    Premise:      {premise}")
            print(f"    Protagonist:  {s.get('protagonist', '?')}")
            if s.get("world_name"):
                print(f"    World:         {s['world_name']}")
            if s.get("world_axes"):
                print(f"    World axes:    {', '.join(str(a) for a in s['world_axes'])}")
            if s.get("scores"):
                score_str = ", ".join(f"{k}={v}" for k, v in s["scores"].items())
                print(f"    Scores:        {score_str}")
            if s.get("critique_verdict"):
                print(f"    Verdict:       {s['critique_verdict']}")
            if s.get("critique_summary"):
                print(f"    Summary:       {s['critique_summary']}")
        print(f"{sep}\n")
