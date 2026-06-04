"""Narrative Engine — canonical CLI.

Commands:
    run         Run pipeline to a checkpoint
    branch      Create N variant children from a node
    compare     Compare siblings side-by-side
    promote     Mark a node as active path
    lock        Lock contract types so workflows skip them
    unlock      Unlock contract types

Global flags:
    --model TEXT       LLM model name (implies real LLM)
    --medium TEXT      Output medium: book, animation, movie, series
    --premise TEXT     Custom premise string
    --save PATH        Save pipeline state after run
    --load PATH        Load pipeline state before run

Per-command flags:
    run [--to CHECKPOINT]
    branch [--from CHECKPOINT] [--vary FIELD] [--values LIST]
           [--to CHECKPOINT] [--tree-load PATH] [--tree-save PATH]
    compare [--tree-load PATH] --labels LIST
    promote [--tree-load PATH] [--tree-save PATH] LABEL
    lock TYPE [TYPE ...]
    unlock TYPE [TYPE ...]

Checkpoints: brief, premise, structure, episodes, scenes, draft, editorial, final
"""

from __future__ import annotations

import os
import sys

_proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

import json

from src.agents.director import Director
from src.agents.llm import MockLLMProvider, OpenAILLMProvider, set_llm, reset_llm
from src.agents.store import get_store, reset_store
from src.contracts.models import Medium, StoryContract
from src.pipeline.checkpoints import CHECKPOINT_ORDER, run_to_checkpoint
from src.pipeline.orchestrator import default_agent_registry
from src.tree.executor import BranchConfig, TreeExecutor
from src.tree.node import TreeNode, TreeStore


DEFAULT_PREMISE = (
    "A disgraced mage, stripped of her powers after a catastrophic experiment, "
    "must retrieve three scattered fragments of an ancient crystal before a "
    "rival cabal assembles them to unleash a world-ending blight. She has only "
    "the whispered guidance of a long-dead archivist and a stolen map that "
    "might be a trap."
)

CHECKPOINT_HELP = ", ".join(CHECKPOINT_ORDER)


def _setup_llm(use_real_llm: bool, model_name: str | None):
    reset_llm()
    if use_real_llm:
        provider = OpenAILLMProvider(model=model_name)
        print(f"\nReal LLM: {provider.model} @ {provider.client.base_url}\n")
        set_llm(provider)
        return
    from scripts.demo import MOCK_RESPONSES
    mock = MockLLMProvider()
    for trigger, response in MOCK_RESPONSES.items():
        mock.add_rule(trigger, response)
    set_llm(mock)


def _print_store(store):
    """Pretty-print the current contract store contents."""
    all_items = store.list_all()
    for type_key, contracts in sorted(all_items.items()):
        print(f"\n  -- {type_key.upper()} ({len(contracts)} contract(s)) --")
        for c in contracts:
            d = c.model_dump(mode="json") if hasattr(c, "model_dump") else {}
            title = d.get("title") or d.get("name") or str(d.get("id", "?"))[:8]
            locked = " [LOCKED]" if store.is_type_locked(type_key) else ""
            print(f"    [{type_key}] {title}{locked}")
            if type_key == "story":
                p = d.get("premise", "")
                print(f"      premise: {p[:60] + '...' if len(p) > 60 else p}")
                if d.get("genre", {}).get("primary_bisac"):
                    print(f"      genre: {d['genre']['primary_bisac']}")
            elif type_key == "character":
                print(f"      role: {d.get('actant_roles', [])}")
            elif type_key == "critique":
                print(f"      verdict: {d.get('verdict', '?')}")
            elif type_key == "episode":
                print(f"      phase: {d.get('canonical_phase', '?')}")
            elif type_key == "scene":
                diag = d.get("greimas_diagnostic", {})
                if diag:
                    print(f"      diagnostic: {'PASS' if diag.get('diagnostic_pass') else 'FAIL'}")


def cmd_run(args: list[str]):
    """python -m src run [--to CHECKPOINT] [--model NAME] [--premise TEXT] [--save PATH] [--load PATH] [--lock TYPE]"""
    target = None
    premise = DEFAULT_PREMISE
    use_real_llm = False
    model_name = None
    medium = Medium.BOOK
    save_path = None
    load_path = None
    lock_types: list[str] = []

    for i, arg in enumerate(args):
        if arg == "--to" and i + 1 < len(args):
            target = args[i + 1]
        elif arg == "--premise" and i + 1 < len(args):
            premise = args[i + 1]
        elif arg == "--model" and i + 1 < len(args):
            use_real_llm = True
            model_name = args[i + 1]
        elif arg == "--medium" and i + 1 < len(args):
            medium = Medium(args[i + 1])
        elif arg == "--save" and i + 1 < len(args):
            save_path = args[i + 1]
        elif arg == "--load" and i + 1 < len(args):
            load_path = args[i + 1]
        elif arg == "--lock" and i + 1 < len(args):
            lock_types = [t.strip() for t in args[i + 1].split(",")]

    if target and target not in CHECKPOINT_ORDER:
        print(f"Unknown checkpoint '{target}'")
        print(f"Available: {CHECKPOINT_HELP}")
        sys.exit(1)

    reset_store()
    store = get_store()

    _setup_llm(use_real_llm, model_name)

    if load_path:
        if os.path.exists(load_path):
            store.load(load_path)
            print(f"\nLoaded pipeline state from {load_path}")
        else:
            print(f"\nLoad path {load_path} not found — starting fresh")

    if not load_path:
        story = StoryContract(
            title="The Crystal Key",
            premise=premise,
            logline="A disgraced mage races to assemble an ancient crystal before her rivals weaponize it.",
        )
        store.put("story", story)
        print(f"\nSeeded story: {story.title}")

    # Apply locks from --lock flag
    for t in lock_types:
        n = store.lock_all(t)
        if n > 0:
            print(f"  Locked {n} {t} contract(s)")

    agents = default_agent_registry(store=store)
    director = Director(agents, store=store, medium=medium)

    reports = run_to_checkpoint(director, target or "final", verbose=True)

    if save_path:
        store.save(save_path)
        print(f"\nSaved pipeline state to {save_path}")

    print(f"\n{'='*50}")
    print("STORE STATE:")
    _print_store(store)

    all_passed = all(r.passed for r in reports)
    print(f"\n{'='*50}")
    print(f"RESULT: {'ALL PASS' if all_passed else 'SOME FAILED'}")
    for r in reports:
        print(f"  {'PASS' if r.passed else 'FAIL'} {r.stage}")
    if not all_passed:
        sys.exit(1)


def cmd_branch(args: list[str]):
    """python -m src branch --vary FIELD --values LIST [--from Ck] [--to Ck] [--tree-load P] [--tree-save P] [--lock TYPE]"""
    branch_from = "premise"
    branch_to = "final"
    vary_field = "genre"
    values_str = None
    labels_str = None
    use_real_llm = False
    model_name = None
    medium = Medium.BOOK
    tree_load_path = None
    tree_save_path = None
    lock_types: list[str] = []

    for i, arg in enumerate(args):
        if arg == "--from" and i + 1 < len(args):
            branch_from = args[i + 1]
        elif arg == "--to" and i + 1 < len(args):
            branch_to = args[i + 1]
        elif arg == "--vary" and i + 1 < len(args):
            vary_field = args[i + 1]
        elif arg == "--values" and i + 1 < len(args):
            values_str = args[i + 1]
        elif arg == "--labels" and i + 1 < len(args):
            labels_str = args[i + 1]
        elif arg == "--model" and i + 1 < len(args):
            use_real_llm = True
            model_name = args[i + 1]
        elif arg == "--medium" and i + 1 < len(args):
            medium = Medium(args[i + 1])
        elif arg == "--tree-load" and i + 1 < len(args):
            tree_load_path = args[i + 1]
        elif arg == "--tree-save" and i + 1 < len(args):
            tree_save_path = args[i + 1]
        elif arg == "--lock" and i + 1 < len(args):
            lock_types = [t.strip() for t in args[i + 1].split(",")]

    _setup_llm(use_real_llm, model_name)
    agents = default_agent_registry(store=get_store())

    tree = TreeStore()
    if tree_load_path and os.path.exists(tree_load_path):
        tree.load(tree_load_path)
        print(f"Loaded tree from {tree_load_path} ({tree.size()} nodes)")
    else:
        store = get_store()
        story_contracts = store.list_by_type("story")
        if not story_contracts:
            print("No story in store. Run 'python -m src run --to <checkpoint>' first.")
            sys.exit(1)

        full_snapshot = store.snapshot()
        seed_snapshot = {k: v for k, v in full_snapshot.items() if k in {"story"}}
        root = TreeNode(label="root", checkpoint="", store_snapshot=seed_snapshot, active=True)
        tree.root = root
        print(f"Created root from current store")

    # Apply locks from --lock flag
    if lock_types:
        store = get_store()
        for t in lock_types:
            n = store.lock_all(t)
            print(f"  Locked {n} {t} contract(s)")

    if not values_str:
        print("--values is required. Example: --values fantasy,scifi,horror")
        sys.exit(1)

    values = [v.strip() for v in values_str.split(",")]
    labels_list = None
    if labels_str:
        labels_list = [l.strip() for l in labels_str.split(",")]

    active = tree.get_active()
    parent = active or tree.root
    if not parent:
        print("No parent node found")
        sys.exit(1)

    print(f"\nBranching from [{parent.label}] @ depth {parent.depth}")
    print(f"  Vary: {vary_field} = {values}")

    config = BranchConfig(
        checkpoint=branch_from,
        vary_field=vary_field,
        values=values,
        medium=medium,
        labels=labels_list,
        target_checkpoint=branch_to,
    )

    executor = TreeExecutor(tree, agents)
    children = executor.branch(parent, config)

    print(f"\nCreated {len(children)} children:")
    for c in children:
        print(f"  [{c.label}] depth={c.depth} params={c.variant_params}")
    executor.promote(children[0])
    print(f"Active: {children[0].label}")

    if tree_save_path:
        tree.save(tree_save_path)
        print(f"Saved tree ({tree.size()} nodes) to {tree_save_path}")


def cmd_compare(args: list[str]):
    """python -m src compare --labels LIST [--tree-load PATH]"""
    labels_str = None
    tree_load_path = None

    for i, arg in enumerate(args):
        if arg == "--labels" and i + 1 < len(args):
            labels_str = args[i + 1]
        elif arg == "--tree-load" and i + 1 < len(args):
            tree_load_path = args[i + 1]

    if not labels_str:
        print("--labels is required. Example: --labels fantasy-v1,scifi-v1")
        sys.exit(1)

    labels = [l.strip() for l in labels_str.split(",")]

    tree = TreeStore()
    if tree_load_path and os.path.exists(tree_load_path):
        tree.load(tree_load_path)
    else:
        print("No tree loaded — use --tree-load")
        sys.exit(1)

    nodes = []
    for label in labels:
        node = tree.get_by_label(label)
        if node:
            nodes.append(node)
        else:
            print(f"Node '{label}' not found")

    if nodes:
        executor = TreeExecutor(tree, {})
        executor.compare(nodes)


def cmd_promote(args: list[str]):
    """python -m src promote LABEL [--tree-load PATH] [--tree-save PATH]"""
    tree_load_path = None
    tree_save_path = None
    label = None

    for i, arg in enumerate(args):
        if arg == "--tree-load" and i + 1 < len(args):
            tree_load_path = args[i + 1]
        elif arg == "--tree-save" and i + 1 < len(args):
            tree_save_path = args[i + 1]
        elif not arg.startswith("--"):
            label = arg

    if not label:
        print("Usage: python -m src promote LABEL [--tree-load PATH]")
        sys.exit(1)

    tree = TreeStore()
    if tree_load_path and os.path.exists(tree_load_path):
        tree.load(tree_load_path)
    else:
        print("No tree loaded — use --tree-load")
        sys.exit(1)

    node = tree.get_by_label(label)
    if not node:
        print(f"Node '{label}' not found")
        sys.exit(1)

    executor = TreeExecutor(tree, {})
    executor.promote(node)
    print(f"Promoted '{label}' to active path")
    for p in tree.path_to_root(node.id):
        print(f"  [{p.label}] depth={p.depth} params={p.variant_params}")

    if tree_save_path:
        tree.save(tree_save_path)
        print(f"Saved tree to {tree_save_path}")


def _parse_keyword_args(args: list[str]) -> tuple[list[str], dict[str, str]]:
    """Split args into positional and keyword.

    Returns (positional, {flag: value}) where flags start with --
    and consume the following arg.
    """
    positional: list[str] = []
    kwargs: dict[str, str] = {}
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--") and i + 1 < len(args):
            kwargs[arg[2:]] = args[i + 1]  # strip leading --
            i += 2
        elif not arg.startswith("--"):
            positional.append(arg)
            i += 1
        else:
            i += 1
    return positional, kwargs


def cmd_lock(args: list[str]):
    """python -m src lock TYPE [TYPE ...] [--load PATH] [--save PATH]"""
    positional, kwargs = _parse_keyword_args(args)
    types = positional
    load_path = kwargs.get("load")
    save_path = kwargs.get("save")

    if not types:
        print("Usage: python -m src lock story character [--load PATH]")
        print("Available types: story, theme, character, world, episode, chapter, scene, discourse, critique")
        sys.exit(1)

    reset_store()
    store = get_store()
    if load_path and os.path.exists(load_path):
        store.load(load_path)
        print(f"Loaded from {load_path}")

    for t in types:
        n = store.lock_all(t)
        print(f"  Locked {n} {t} contract(s)")

    if save_path:
        store.save(save_path)
        print(f"Saved to {save_path}")


def cmd_unlock(args: list[str]):
    """python -m src unlock TYPE [TYPE ...] [--load PATH] [--save PATH]"""
    positional, kwargs = _parse_keyword_args(args)
    types = positional
    load_path = kwargs.get("load")
    save_path = kwargs.get("save")

    if not types:
        print("Usage: python -m src unlock story character")
        sys.exit(1)

    reset_store()
    store = get_store()
    if load_path and os.path.exists(load_path):
        store.load(load_path)
        print(f"Loaded from {load_path}")

    for t in types:
        n = store.unlock_all(t)
        print(f"  Unlocked {n} {t} contract(s)")

    if save_path:
        store.save(save_path)
        print(f"Saved to {save_path}")


COMMANDS = {
    "run": cmd_run,
    "branch": cmd_branch,
    "compare": cmd_compare,
    "promote": cmd_promote,
    "lock": cmd_lock,
    "unlock": cmd_unlock,
}


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return

    command = args[0]
    rest = args[1:]

    if command in COMMANDS:
        COMMANDS[command](rest)
    else:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(COMMANDS)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
