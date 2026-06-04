"""Tree executor — branch, compare, promote operations.

Wraps the pipeline Director in tree-aware operations. Each branch creates
N children by running the pipeline from a parent checkpoint forward with
different variant parameters, then saving the resulting ContractStore state.
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


@dataclass
class BranchConfig:
    """Configuration for a branch operation.

    Attributes:
        checkpoint: Which pipeline checkpoint to branch from.
            Must be one of CHECKPOINT_ORDER.
        vary_field: What to vary between variants
            ("genre", "seed", "premise", "tone").
        values: List of values to try (one per variant).
        medium: Output medium for the pipeline.
        labels: Optional human-readable labels (one per value).
            Auto-generated from values if not provided.
    """
    checkpoint: str
    vary_field: str = "genre"
    values: list[str] = None
    medium: Medium = Medium.BOOK
    labels: list[str] = None


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

    def branch(
        self,
        parent: TreeNode,
        config: BranchConfig,
    ) -> list[TreeNode]:
        """Create N children from a parent by varying parameters.

        For each value in config.values:
        1. Restore parent's store snapshot into a fresh store
        2. Apply the variant parameter to the store contracts
        3. Create a Director and run from parent's checkpoint forward
        4. Snapshot the result into a new TreeNode

        Returns the list of newly created child nodes.
        """
        if config.values is None:
            config.values = ["default"]
        labels = config.labels or [str(v) for v in config.values]
        if len(labels) != len(config.values):
            labels = [str(v) for v in config.values]

        # Determine which workflow to start from
        parent_checkpoint = parent.checkpoint or ""
        parent_idx = CHECKPOINT_ORDER.index(parent_checkpoint) if parent_checkpoint in CHECKPOINT_ORDER else -1

        # Workflows to run from this point forward
        target_checkpoint = "final"
        start_idx = parent_idx + 1 if parent_idx >= 0 else 0
        end_idx = CHECKPOINT_ORDER.index(target_checkpoint) if target_checkpoint in CHECKPOINT_ORDER else len(CHECKPOINT_ORDER) - 1

        children: list[TreeNode] = []

        for i, value in enumerate(config.values):
            label = labels[i] if i < len(labels) else str(value)

            # Fresh store for this variant
            reset_store()
            store = get_store()

            # Restore parent state
            store.restore(parent.store_snapshot)

            # Apply variant parameter
            self._apply_variant(store, config.vary_field, value, label)

            # Build director and run
            director = Director(
                self.agents,
                store=store,
                medium=config.medium,
            )

            # Run workflows from parent's checkpoint forward
            self._run_from_checkpoint(director, parent_checkpoint, target_checkpoint)

            # Snapshot result
            child_snapshot = store.snapshot()

            # Extract scores from critique contracts
            scores = self._extract_scores(store)

            child = TreeNode(
                id=uuid4(),
                parent_id=parent.id,
                depth=parent.depth + 1,
                checkpoint=target_checkpoint,
                label=label,
                variant_params={config.vary_field: value, **parent.variant_params},
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

            # Extract key contracts
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

        # Print comparison table
        self._print_comparison(summaries)
        return summaries

    def promote(self, node: TreeNode) -> None:
        """Mark a node as the active path.

        Deactivates all other nodes and marks this one active.
        """
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
        elif vary_field == "seed":
            pass

    def _run_from_checkpoint(
        self,
        director: Director,
        from_checkpoint: str,
        to_checkpoint: str,
    ) -> None:
        """Run pipeline workflows from one checkpoint to another."""
        start_idx = CHECKPOINT_ORDER.index(from_checkpoint) if from_checkpoint in CHECKPOINT_ORDER else -1
        end_idx = CHECKPOINT_ORDER.index(to_checkpoint) if to_checkpoint in CHECKPOINT_ORDER else len(CHECKPOINT_ORDER) - 1

        for idx in range(start_idx + 1, end_idx + 1):
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
            print(f"    Genre:        {s.get('genre', '?')}")
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
