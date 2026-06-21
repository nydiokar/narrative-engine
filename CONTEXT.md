# Context — Narrative Engine

## Current Status (June 21, 2026)

All 435 tests pass. Full pipeline runs clean with real LLM (llama3.2 @ localhost:11434).
Branching (sequential + parallel) works with correct contract seeding + variant comparison.

## Recent Work

### Session: Branch Seed Fix + Test Debt Cleanup

**Goal:** Fix branch snapshot seeding, eliminate 3 pre-existing test failures.

**Achievements:**

1. **Branch seed fix** (`src/cli.py`):
   - Root cause: `cmd_branch` filtered seed contracts to only `{"story"}`.
   - Fixed: use `expected_contracts_at_checkpoint(branch_from)` to include all contract types (story+theme+character for `premise`).

2. **Orphan node fallback** (`src/tree/executor.py:116`):
   - `_find_root_seed` now returns `self.tree.root` when a node's `parent_id` doesn't match any tree node.

3. **Rich markup escaping** (`src/tree/executor.py:630`):
   - `_print_comparison` uses `rich.markup.escape(label)` so node labels with brackets aren't consumed as Rich markup tags.

4. **Scene writer retry fix** (`src/agents/scene_writer.py:241–264`):
   - Only retry on LLM exceptions (transient errors), not empty/parse-failure responses.
   - Saves ~6s of backoff sleep per episode when LLM returns empty data.

5. **Test assertion fixes** (4 tests):
   - Scene count 24→36 (12 chapters × 3 fallback scenes).
   - All 9 scene writer tests now pass in 0.18s (was hanging >5s).

## All Tests (435 passed)

| Suite | Count | Status |
|-------|-------|--------|
| Tree tests | 58 | ✅ |
| Pipeline/Showrunner/Store | 36 | ✅ |
| Scene writer | 9 | ✅ |
| Full pipeline integration | 4 | ✅ |
| All others | 328 | ✅ |

## Key Commands
```
python -m src branch --vary genre --values fantasy,scifi --from premise --to structure --tree-load state.json --tree-save tree.json --provider opencode
python -m src branch --vary genre --values fantasy,scifi,horror --parallel --max-workers 3 --tree-load state.json --tree-save tree.json
python -m src compare --labels fantasy,scifi --tree-load tree.json --detail
python -m pytest tests/ -q
```

## Known Issues
- None (all 435 tests pass)
