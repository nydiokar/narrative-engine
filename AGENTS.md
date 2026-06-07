# Agent Notes — Narrative Engine

## Canonical Entry Point

**ALWAYS use `python -m src` — NOT `scripts/demo.py`.**

The CLI lives in `src/cli.py` and dispatches subcommands:

| Command | Example |
|---------|---------|
| `run` | `python -m src run --to premise` |
| `branch` | `python -m src branch --vary genre --values fantasy,scifi,horror` |
| `compare` | `python -m src compare --labels fantasy,scifi --tree-load tree.json` |
| `promote` | `python -m src promote fantasy --tree-load tree.json --tree-save tree.json` |
| `prune` | `python -m src prune bad-branch --tree-load tree.json --tree-save tree.json` |
| `show` | `python -m src show --tree-load tree.json` |
| `set` | `python -m src set story.genre.primary_bisac=FIC009000` |
| `lock` / `unlock` | `python -m src lock story.genre` |

`scripts/demo.py` is legacy — kept for smoke-testing but all new work goes in `src/cli.py`.

## Key Paths

| What | Where |
|------|-------|
| CLI dispatcher | `src/cli.py` |
| Subcommands | `cmd_run`, `cmd_branch`, `cmd_compare`, etc. in `src/cli.py` |
| Tree executor | `src/tree/executor.py` — `branch()`, `compare()`, `promote()`, `prune()` |
| Tree node + store | `src/tree/node.py` — `TreeNode`, `TreeStore` |
| Tests | `tests/test_tree/test_node.py`, `tests/test_tree/test_executor.py` |

## Tree Commands

Run pipeline, save state, then branch:
```
python -m src run --to premise --save trunk.json
python -m src branch --vary genre --values fantasy,scifi --tree-load trunk.json --tree-save tree.json
python -m src compare --labels fantasy,scifi --tree-load tree.json
python -m src promote fantasy --tree-load tree.json --tree-save tree.json
python -m src show --tree-load tree.json
```

## Vary Fields

Handled in `src/tree/executor.py:_apply_variant()`:

- `genre` — sets `story.genre.primary_bisac`
- `premise` — sets `story.premise` + `story.title`
- `world` — sets `world.name` + `world.description`
- `character` — sets `character.name` + `character.description` (name-only; use `--set` for deeper field tweaks)
- `conflict` — sets `episode.dominant_conflict` on all episodes

`seed`, `tone`, and `theme` have no corresponding contract fields — removed as vary field options.

## Building Docs

```
python -m mkdocs build --strict     # build site/
python -m mkdocs serve               # live preview at http://127.0.0.1:8000
```

## Running Tests

```
pytest tests/ -q
```

Tree-specific: `pytest tests/test_tree/ -q`
Adversarial review pass after any tree/CLI changes.
