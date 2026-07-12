"""Tree executor — branch, compare, promote operations.

Each branch creates N children by reconstructing the full parameter path
from root to parent, applying all variant params, and running the pipeline
from scratch. This avoids stale-contract issues in multi-depth trees.
"""

from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass
from logging import Logger
from typing import Any
from uuid import uuid4

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.agents.director import Director
from src.agents.store import ContractStore, get_store, reset_store
from src.contracts.models import ConflictType, Medium
from src.pipeline.checkpoints import (
    CHECKPOINT_ORDER,
    WORKFLOW_FOR_CHECKPOINT,
)
from src.pipeline.orchestrator import default_agent_registry
from src.tree.node import TreeNode, TreeStore


# Mapping: vary_field → checkpoint to re-run from
_VARY_FROM_CHECKPOINT: dict[str, str] = {
    "genre": "brief",
    "premise": "premise",
    "world": "structure",
    "character": "episodes",
    "conflict": "episodes",
}


@dataclass
class BranchConfig:
    """Configuration for a branch operation.

    Attributes:
        checkpoint: Which pipeline checkpoint to branch from
            ("brief", "premise", "structure", "episodes", etc).
            If empty, auto-detected from vary_field.
        vary_field: What to vary between variants
            ("genre", "premise", "world", "character", "conflict").
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
        while current.parent_id:
            parent = self.tree.get(current.parent_id)
            if not parent:
                return self.tree.root
            current = parent
        return current

    # ── Static variant runner (for parallel or sequential use) ────────

    @staticmethod
    def _execute_variant(
        root_snapshot: dict,
        all_params: dict,
        medium: Medium,
        from_checkpoint: str,
        to_checkpoint: str,
        label: str = "",
        logger: Logger | None = None,
    ) -> dict:
        """Run one variant in an isolated environment.

        Creates its own ``ContractStore``, agent registry, and ``Director``.
        Does **not** touch any module-level singletons, so safe to call from
        multiple threads.

        Returns ``{"snapshot": …, "scores": …}``.
        """
        store = ContractStore()
        store.restore(root_snapshot)

        TreeExecutor._apply_params_static(store, all_params, label=label)

        agents = default_agent_registry(store=store, logger=logger)
        director = Director(agents, store=store, medium=medium)

        start_idx = 0
        if from_checkpoint in CHECKPOINT_ORDER:
            start_idx = CHECKPOINT_ORDER.index(from_checkpoint)
        end_idx = len(CHECKPOINT_ORDER) - 1
        if to_checkpoint in CHECKPOINT_ORDER:
            end_idx = CHECKPOINT_ORDER.index(to_checkpoint)

        for idx in range(start_idx, end_idx + 1):
            ck_name = CHECKPOINT_ORDER[idx]
            wid = WORKFLOW_FOR_CHECKPOINT.get(ck_name)
            if wid and wid in agents:
                director.run_workflow(wid)

        return {
            "snapshot": store.snapshot(),
            "scores": TreeExecutor._extract_scores_static(store),
        }

    @staticmethod
    def _apply_params_static(
        store: ContractStore,
        params: dict,
        label: str = "",
    ) -> None:
        """Apply variant params to a store (static, no self needed)."""
        for field, val in params.items():
            TreeExecutor._apply_variant_static(store, field, val, label)

    @staticmethod
    def _apply_variant_static(
        store: ContractStore,
        vary_field: str,
        value: str,
        label: str,
    ) -> None:
        """Apply a single variant to the store (static equivalent of _apply_variant)."""
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
                TreeExecutor._apply_character_variant_static(char, value, label)
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

    @staticmethod
    def _apply_character_variant_static(char: Any, value: str, label: str) -> None:
        char.name = label or value
        char.description = f"Character variant: {value}"

    @staticmethod
    def _extract_scores_static(store: ContractStore) -> dict[str, Any]:
        """Extract evaluation scores from critique contracts (static)."""
        scores: dict[str, Any] = {}
        critiques = store.list_by_type("critique")
        if critiques:
            last = critiques[-1]
            d = last.model_dump(mode="json") if hasattr(last, "model_dump") else {}
            scores["verdict"] = d.get("verdict", "?")
            scores["summary"] = (d.get("summary") or "")[:100]
            scores["hard_gate_pass"] = d.get("verdict") == "pass"
        return scores

    # ── Branch ────────────────────────────────────────────────────────

    def branch(
        self,
        parent: TreeNode,
        config: BranchConfig,
        parallel: bool = False,
        max_workers: int = 4,
    ) -> list[TreeNode]:
        """Create N children from a parent by varying parameters.

        If *parallel* is ``True``, variants execute concurrently using a
        ``ThreadPoolExecutor`` (each variant runs in an isolated environment
        with its own ``ContractStore``).

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

        variant_tasks: list[tuple[str, str, dict]] = []
        for i, value in enumerate(config.values):
            label = labels[i] if i < len(labels) else str(value)
            all_params = dict(inherited_params)
            all_params[config.vary_field] = value
            variant_tasks.append((value, label, all_params))

        if parallel and len(variant_tasks) > 1:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(max_workers, len(variant_tasks))
            ) as pool:
                fut_to_idx: dict[concurrent.futures.Future, int] = {}
                for i, (value, label, all_params) in enumerate(variant_tasks):
                    fut = pool.submit(
                        TreeExecutor._execute_variant,
                        root.store_snapshot,
                        all_params,
                        config.medium,
                        config.effective_checkpoint,
                        config.target_checkpoint,
                        label,
                        self.logger,
                    )
                    fut_to_idx[fut] = i

                raw_results: list[dict | None] = [None] * len(variant_tasks)
                total = len(variant_tasks)
                done = 0
                console = Console()
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task_id = progress.add_task(
                        f"Running {total} variant(s) in parallel...",
                        total=total,
                    )
                    for fut in concurrent.futures.as_completed(fut_to_idx):
                        idx = fut_to_idx[fut]
                        try:
                            raw_results[idx] = fut.result()
                        except Exception as e:
                            raw_results[idx] = {"error": str(e)}
                        done += 1
                        label_done = variant_tasks[idx][1]
                        progress.update(
                            task_id,
                            advance=1,
                            description=f"[{done}/{total}] {label_done} done",
                        )

            for i, (value, label, all_params) in enumerate(variant_tasks):
                result = raw_results[i]
                if result is None or "error" in result:
                    msg = result.get("error", "unknown error") if result else "no result"
                    child = TreeNode(
                        id=uuid4(),
                        parent_id=parent.id,
                        depth=parent.depth + 1,
                        checkpoint=config.target_checkpoint,
                        label=label,
                        variant_params=all_params,
                        store_snapshot={},
                        scores={"error": msg},
                        active=False,
                    )
                else:
                    child = TreeNode(
                        id=uuid4(),
                        parent_id=parent.id,
                        depth=parent.depth + 1,
                        checkpoint=config.target_checkpoint,
                        label=label,
                        variant_params=all_params,
                        store_snapshot=result["snapshot"],
                        scores=result["scores"],
                        active=False,
                    )
                self.tree.add(child)
                parent.children.append(child.id)
                children.append(child)
        else:
            for i, (value, label, all_params) in enumerate(variant_tasks):
                # Fresh store from root seed
                reset_store()
                store = get_store()
                store.restore(root.store_snapshot)

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

                child_snapshot = store.snapshot()
                scores = self._extract_scores(store)

                child = TreeNode(
                    id=uuid4(),
                    parent_id=parent.id,
                    depth=parent.depth + 1,
                    checkpoint=config.target_checkpoint,
                    label=label,
                    variant_params=all_params,
                    store_snapshot=child_snapshot,
                    scores=scores,
                    active=False,
                )

                self.tree.add(child)
                parent.children.append(child.id)
                children.append(child)

        return children

    def compare(
        self,
        nodes: list[TreeNode],
        detail: bool = False,
    ) -> list[dict[str, Any]]:
        """Compare sibling nodes side-by-side.

        If *detail* is ``True``, prints an expanded view including episode,
        chapter, and scene counts per variant.

        Returns a list of dicts with key contract data for each node.
        Also prints a rich comparison table.
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
                summary["premise"] = (d.get("premise") or "")[:120]
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
                summary["world_dimensions"] = [
                    d.get("axis", "") for d in wd.get("dimensions", [])
                    if isinstance(d, dict)
                ]

            episodes = store.list_by_type("episode")
            summary["episode_count"] = len(episodes)
            chapters = store.list_by_type("chapter")
            summary["chapter_count"] = len(chapters)
            scenes = store.list_by_type("scene")
            summary["scene_count"] = len(scenes)

            critiques = store.list_by_type("critique")
            if critiques:
                cr = critiques[-1]
                crd = cr.model_dump(mode="json") if hasattr(cr, "model_dump") else {}
                summary["critique_verdict"] = crd.get("verdict", "?")
                summary["critique_summary"] = (crd.get("summary") or "")[:120]

            summaries.append(summary)

        self._print_comparison(summaries, detail=detail)
        return summaries

    def diff(
        self,
        node_a: TreeNode,
        node_b: TreeNode,
    ) -> dict[str, Any]:
        """Show contract-level differences between two nodes.

        Returns a structured dict of differences per contract type.
        Also prints a rich summary to the console.
        """
        store_a = ContractStore()
        store_a.restore(node_a.store_snapshot)
        store_b = ContractStore()
        store_b.restore(node_b.store_snapshot)

        contracts_a = store_a.list_all()
        contracts_b = store_b.list_all()

        all_types = sorted(set(contracts_a) | set(contracts_b))
        diffs: dict[str, list[dict]] = {}

        for type_key in all_types:
            typediffs: list[dict] = []
            list_a = contracts_a.get(type_key, [])
            list_b = contracts_b.get(type_key, [])

            # Compare counts
            if len(list_a) != len(list_b):
                typediffs.append({
                    "field": "_count",
                    "a": len(list_a),
                    "b": len(list_b),
                })

            # Compare key fields on first contract of each type
            if list_a and list_b:
                da = list_a[0].model_dump(mode="json") if hasattr(list_a[0], "model_dump") else {}
                db = list_b[0].model_dump(mode="json") if hasattr(list_b[0], "model_dump") else {}
                # Skip id and timestamps — they always differ
                skip_keys = {"id", "created_at", "timestamp"}
                for key in sorted(set(da) | set(db)):
                    if key in skip_keys:
                        continue
                    va = da.get(key)
                    vb = db.get(key)
                    if va != vb:
                        typediffs.append({
                            "field": key,
                            "a": va,
                            "b": vb,
                        })

            if typediffs:
                diffs[type_key] = typediffs

        # Print summary
        console = Console()
        if not diffs:
            console.print(Panel(
                "[green]No differences found between the two nodes.[/green]",
                title="Diff",
            ))
        else:
            console.print(Panel(
                f"[bold]Diff:[/bold] {escape(node_a.label)} vs {escape(node_b.label)}",
                style="yellow",
            ))
            for type_key, typediffs in diffs.items():
                table = Table(title=f"{type_key} differences")
                table.add_column("Field", style="cyan")
                table.add_column(escape(node_a.label), style="green")
                table.add_column(escape(node_b.label), style="yellow")
                for td in typediffs:
                    a_str = str(td["a"])[:60] if td["a"] is not None else "—"
                    b_str = str(td["b"])[:60] if td["b"] is not None else "—"
                    table.add_row(td["field"], a_str, b_str)
                console.print(table)

        return diffs

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
        if self.tree.get_active() is None:
            ancestor = self.tree.get(node.parent_id) if node.parent_id else self.tree.root
            if ancestor:
                ancestor.active = True
        return removed

    # ── Instance helpers (delegate to static versions) ────────────────

    def _apply_variant(
        self,
        store: ContractStore,
        vary_field: str,
        value: str,
        label: str,
    ) -> None:
        TreeExecutor._apply_variant_static(store, vary_field, value, label)

    def _apply_character_variant(
        self,
        char: Any,
        value: str,
        label: str,
    ) -> None:
        TreeExecutor._apply_character_variant_static(char, value, label)

    def _run_from_checkpoint(
        self,
        director: Director,
        from_checkpoint: str,
        to_checkpoint: str,
    ) -> None:
        """Run pipeline workflows from one checkpoint to another."""
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
        return TreeExecutor._extract_scores_static(store)

    # ── Rich comparison output ───────────────────────────────────────

    def _print_comparison(
        self,
        summaries: list[dict[str, Any]],
        detail: bool = False,
    ) -> None:
        """Print a side-by-side comparison using Rich tables."""
        console = Console()

        if not summaries:
            console.print("[yellow]No variants to compare.[/yellow]")
            return

        console.print()
        table = Table(
            title=f"Side-by-Side Comparison ({len(summaries)} variants)",
            show_lines=True,
        )
        table.add_column("Property", style="cyan", no_wrap=True)
        for s in summaries:
            label = s["label"]
            verdict = s.get("critique_verdict", "?")
            style = "green" if verdict == "pass" else "red"
            table.add_column(escape(label), style=style, no_wrap=False)

        PROPERTIES = [
            ("checkpoint", "Checkpoint"),
            ("title", "Title"),
            ("genre", "Genre"),
            ("premise", "Premise"),
            ("protagonist", "Protagonist"),
            ("world_name", "World"),
            ("episode_count", "Episodes"),
            ("chapter_count", "Chapters"),
            ("scene_count", "Scenes"),
            ("critique_verdict", "Verdict"),
            ("critique_summary", "Summary"),
        ]

        for key, display_name in PROPERTIES:
            row = [display_name]
            for s in summaries:
                val = s.get(key)
                if val is None or val == "?" or val == "":
                    row.append("—")
                elif isinstance(val, str) and len(val) > 55:
                    row.append(val[:52] + "...")
                else:
                    row.append(str(val))
            table.add_row(*row)

        # Scores row (always present)
        row = ["Scores"]
        for s in summaries:
            sc = s.get("scores", {})
            if sc and not sc.get("error"):
                parts = [f"{k}={v}" for k, v in sc.items()]
                row.append(", ".join(parts))
            else:
                row.append("—")
        table.add_row(*row)

        console.print(table)

        if detail:
            for s in summaries:
                console.print()
                panel_lines = [
                    f"  Label:       {s['label']}",
                    f"  Checkpoint:  {s['checkpoint']}",
                    f"  Params:      {s['variant_params']}",
                ]
                if s.get("world_dimensions"):
                    panel_lines.append(
                        f"  World axes:  {', '.join(str(a) for a in s['world_dimensions'])}"
                    )
                if s.get("protagonist_role"):
                    panel_lines.append(
                        f"  Role:        {', '.join(str(r) for r in s['protagonist_role'])}"
                    )
                console.print(Panel(
                    "\n".join(panel_lines),
                    title=f"[{s['label']}] Detail",
                    border_style="blue",
                ))
