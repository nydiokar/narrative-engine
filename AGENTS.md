# Agent Notes — Narrative Engine

## Canonical Entry Point

**ALWAYS use `python -m src` — NOT `scripts/demo.py`.**

The CLI lives in `src/cli.py` and dispatches subcommands:

| Command | Example |
|---------|---------|
| `run` | `python -m src run --to premise` |
| `branch` | `python -m src branch --vary genre --values fantasy,scifi,horror` |
| `branch` (parallel) | `python -m src branch --vary genre --values fantasy,scifi,horror --parallel --max-workers 4` |
| `compare` | `python -m src compare --labels fantasy,scifi --tree-load tree.json` |
| `compare` (detail) | `python -m src compare --labels fantasy,scifi --tree-load tree.json --detail` |
| `diff` | `python -m src diff fantasy scifi --tree-load tree.json` |
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
| LLM providers | `src/agents/llm.py` — `OpenAILLMProvider`, `SubprocessLLMProvider`, `MockLLMProvider` |
| Atomic commit | `src/pipeline/commit.py` — `commit_agent_output()`, `validate_output()`, `check_referential_integrity()` |
| Semantic agents | `.opencode/agents/*.md` — 18 agent configs (model, temp, permissions, system prompt) |
| Project config | `opencode.json` — default model provider config |
| Tests | `tests/test_tree/test_node.py`, `tests/test_tree/test_executor.py` |

## Tree Commands

Run pipeline, save state, then branch:
```
python -m src run --to premise --save trunk.json
python -m src branch --vary genre --values fantasy,scifi --tree-load trunk.json --tree-save tree.json
python -m src compare --labels fantasy,scifi --tree-load tree.json
python -m src diff fantasy scifi --tree-load tree.json
python -m src promote fantasy --tree-load tree.json --tree-save tree.json
python -m src show --tree-load tree.json
```

## Vary Fields

Handled in `src/tree/executor.py:_apply_variant_static()`:

- `genre` — sets `story.genre.primary_bisac`
- `premise` — sets `story.premise` + `story.title`
- `world` — sets `world.name` + `world.description`
- `character` — sets `character.name` + `character.description` (name-only; use `--set` for deeper field tweaks)
- `conflict` — sets `episode.dominant_conflict` on all episodes

`seed`, `tone`, and `theme` have no corresponding contract fields — removed as vary field options.

## Provider Selection

Three LLM backends, switchable at runtime:

| Provider | Flag | Backend |
|----------|------|---------|
| OpenCode | `--provider opencode` | `SubprocessLLMProvider` — calls `opencode run --agent <role>` (uses `.opencode/agents/*.md` semantic agent configs) |
| OpenAI | `--provider openai` | `OpenAILLMProvider` — standard OpenAI-compatible HTTP (Ollama, OpenAI, etc.) |
| Mock | `--provider mock` | `MockLLMProvider` — canned responses for testing |

Examples:
```
python -m src run --to premise --provider opencode
python -m src run --to final --provider openai --model qwen3-coder
python -m src run --to scene --provider mock
```

The `LLM_PROVIDER` env var can also set it: `export LLM_PROVIDER=opencode`

## Architecture: Logic Agents + Semantic Agents

Every pipeline role has **two** agent configs:

| Layer | File | Purpose |
|-------|------|---------|
| Logic agent | `src/agents/*.py` | Python class — validation, routing, diagnostics, fallbacks, assembly. Owns the logic. |
| Semantic agent | `.opencode/agents/*.md` | OpenCode config — model binding, temperature, permissions, system prompt. Owns the model interface. |

The flow is:
```
Director → logic agent (Python) → LLMProvider → semantic agent (OpenCode agent config) → backend model
```

To connect the semantic agent config for a new backend, just change the `model` field in `.opencode/agents/*.md` or the default in `opencode.json`.

## Run Directory Structure

When using `--provider opencode`, each LLM call creates an isolated run directory:
```
runs/
  run_20260608_125530_001/
    step_select_themes/
      task.md                     # instruction for the agent
      input/
        system_prompt.md          # system prompt from role template
        call_metadata.json        # step, role, workflow info
      output/
        result.json               # agent writes output here
      logs/
        stdout.txt                # captured stdout
        stderr.txt                # captured stderr
        metadata.json             # execution metadata
    step_analyze_premise/
      ...
  store/
    committed/
      story/{id}.json
      character/{id}.json
      ...
    commits/commit.log.jsonl
```

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

## Session Protocol

After every session, update `CONTEXT.md` with:
- New features, fixed bugs, and changed behaviour
- Updated test counts and status
- Any changes to the Known Design Debt or roadmap

This file (`AGENTS.md`) is the operational manual. `CONTEXT.md` is the canonical hot-context file for continuity across sessions. Do not skip the update.
