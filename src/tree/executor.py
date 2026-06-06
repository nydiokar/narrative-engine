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
from src.contracts.models import ConflictType, Medium, StoryContract
from src.pipeline.checkpoints import (
    CHECKPOINT_ORDER,
    WORKFLOW_FOR_CHECKPOINT,
    run_to_checkpoint,
)
from src.tree.node import TreeNode, TreeStore


# Mapping: vary_field → checkpoint to re-run from
_VARY_FROM_CHECKPOINT: dict[str, str] = {
    "genre": "brief",
    "premise": "premise",
    "world": "structure",
    "character": "episodes",
    "conflict": "episodes",
    "seed": "brief",       # reserved — tied to LLM param variance (not yet implemented)
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
        """Walk from root to node, collecting all variant_params.

        Params closer to the node override those closer to root,
        so children can override parent choices.
        """
        path: list[TreeNode] = []
        current = node
        while current:
            path.append(current)
            current = self.tree.get(current.parent_id) if current.parent_id else None
        path.reverse()

        params: dict[str, Any] = {}
        for n in path:
            params.update(n.variant_params)
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
                summary["world_dimensions"] = [d.get("axis", "") for d in wd.get("dimensions", []) if isinstance(d, dict)]

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

    def prune(self, node: TreeNode) -> int:
        """Remove a node and its entire subtree from the tree.

        If the active node is removed, the nearest ancestor becomes
        the new active path. Returns the count of removed nodes.
        """
        removed = self.tree.prune(node.id)
        # If active was in the pruned subtree, promote nearest ancestor
        if self.tree.get_active() is None:
            ancestor = self.tree.get(node.parent_id) if node.parent_id else self.tree.root
            if ancestor:
                ancestor.active = True
        return removed

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
                changed = False
                if hasattr(story, "premise"):
                    story.premise = value
                    changed = True
                if hasattr(story, "title") and label:
                    story.title = label
                    changed = True
                if changed:
                    store.put("story", story, agent="tree_branch")
        elif vary_field == "world":
            worlds = store.list_by_type("world")
            if worlds:
                world = worlds[0]
                world.name = label or value
                world.description = f"World variant: {value}"
                store.put("world", world, agent="tree_branch")
        elif vary_field == "character":
            characters = store.list_by_type("character")
            if characters:
                char = characters[0]
                self._apply_character_variant(char, value, label)
                store.put("character", char, agent="tree_branch")
        elif vary_field == "conflict":
            episodes = store.list_by_type("episode")
            if not episodes:
                return
            conflict_value = ConflictType.INTERPERSONAL
            try:
                conflict_value = ConflictType(value.lower())
            except ValueError:
                pass
            for ep in episodes:
                ep.dominant_conflict = conflict_value
                store.put("episode", ep, agent="tree_branch")

    def _apply_character_variant(
        self,
        char: Any,
        value: str,
        label: str,
    ) -> None:
        """Apply a character archetype variant to the protagonist."""
        archetypes: dict[str, dict] = {
            "heroic": {
                "personality": {"openness": 7, "conscientiousness": 8, "extraversion": 6, "agreeableness": 7, "neuroticism": 3},
                "core_desires": ["justice", "protection"],
                "core_fears": ["failure", "cowardice"],
                "wound_types": ["loss", "injustice"],
                "need_types": ["purpose", "belonging"],
                "social_mode_default": "equality_matching",
                "attachment_pattern": "secure",
            },
            "reluctant": {
                "personality": {"openness": 5, "conscientiousness": 6, "extraversion": 3, "agreeableness": 5, "neuroticism": 7},
                "core_desires": ["peace", "normalcy"],
                "core_fears": ["responsibility", "loss"],
                "wound_types": ["betrayal", "failure"],
                "need_types": ["acceptance", "safety"],
                "social_mode_default": "market_pricing",
                "attachment_pattern": "fearful_avoidant",
            },
            "tragic": {
                "personality": {"openness": 8, "conscientiousness": 4, "extraversion": 2, "agreeableness": 4, "neuroticism": 9},
                "core_desires": ["redemption", "meaning"],
                "core_fears": ["repeating mistakes", "condemnation"],
                "wound_types": ["betrayal_self", "failure"],
                "need_types": ["atonement", "connection"],
                "social_mode_default": "authority_ranking",
                "attachment_pattern": "fearful_avoidant",
            },
            "antihero": {
                "personality": {"openness": 6, "conscientiousness": 3, "extraversion": 3, "agreeableness": 3, "neuroticism": 7},
                "core_desires": ["control", "survival"],
                "core_fears": ["vulnerability", "betrayal"],
                "wound_types": ["betrayal", "injustice"],
                "need_types": ["autonomy", "respect"],
                "social_mode_default": "market_pricing",
                "attachment_pattern": "dismissive_avoidant",
            },
            "mentor": {
                "personality": {"openness": 8, "conscientiousness": 7, "extraversion": 4, "agreeableness": 8, "neuroticism": 2},
                "core_desires": ["knowledge", "legacy"],
                "core_fears": ["obsolescence", "failing to teach"],
                "wound_types": ["loss", "regret"],
                "need_types": ["purpose", "generativity"],
                "social_mode_default": "authority_ranking",
                "attachment_pattern": "secure",
            },
            "trickster": {
                "personality": {"openness": 9, "conscientiousness": 3, "extraversion": 8, "agreeableness": 6, "neuroticism": 3},
                "core_desires": ["freedom", "chaos"],
                "core_fears": ["entrapment", "predictability"],
                "wound_types": ["boredom", "constraint"],
                "need_types": ["stimulation", "expression"],
                "social_mode_default": "equality_matching",
                "attachment_pattern": "dismissive_avoidant",
            },
        }

        archetype = archetypes.get(value)
        if archetype is None:
            char.name = label or value
            char.description = f"Character variant: {value}"
            return

        char.name = label or value
        char.description = f"{value.capitalize()} archetype protagonist"

        if hasattr(char, "personality") and char.personality:
            for trait, score in archetype.get("personality", {}).items():
                setattr(char.personality, trait, score)

        if "core_desires" in archetype:
            char.core_desires = list(archetype["core_desires"])
        if "core_fears" in archetype:
            char.core_fears = list(archetype["core_fears"])
        if "wound_types" in archetype:
            char.wound_types = list(archetype["wound_types"])
        if "need_types" in archetype:
            char.need_types = list(archetype["need_types"])
        if "social_mode_default" in archetype:
            from src.contracts.models import RelationalModel
            try:
                char.social_mode_default = RelationalModel(archetype["social_mode_default"])
            except ValueError:
                pass
        if "attachment_pattern" in archetype:
            from src.contracts.models import AttachmentPattern
            try:
                char.attachment_pattern = AttachmentPattern(archetype["attachment_pattern"])
            except ValueError:
                pass

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
            if s.get("world_dimensions"):
                print(f"    World axes:    {', '.join(str(a) for a in s['world_dimensions'])}")
            if s.get("scores"):
                score_str = ", ".join(f"{k}={v}" for k, v in s["scores"].items())
                print(f"    Scores:        {score_str}")
            if s.get("critique_verdict"):
                print(f"    Verdict:       {s['critique_verdict']}")
            if s.get("critique_summary"):
                print(f"    Summary:       {s['critique_summary']}")
        print(f"{sep}\n")
