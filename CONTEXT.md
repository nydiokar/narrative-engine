# Context — Narrative Engine

## Current Status (June 21, 2026)

Full pipeline runs clean with real LLM (llama3.2 @ localhost:11434). All 8 checkpoints pass.
Branching now correctly seeds all contract types expected at the branch-from checkpoint.

## Recent Work

### Session: Branch Snapshot Seed Fix

**Goal:** Fix branch snapshot seeding so root snapshots include all contract types expected at the branch-from checkpoint, not just `story`.

**Achievements:**

1. **Branch seed fix** (`src/cli.py:444, 459`):
   - Root cause: `cmd_branch` filtered seed contracts to only `{"story"}` when creating root snapshots from store files or the current store.
   - When branching from `premise`, the seed was missing `theme` and `character` contracts — workflows 01–02 couldn't find their prerequisites and failed silently.
   - Fixed: use `expected_contracts_at_checkpoint(branch_from)` to determine which contract types to include in the seed snapshot.
   - Added warning for existing tree files whose root snapshot is missing expected contracts.

2. **Test verification:**
   - 56 tree tests pass (2 pre-existing failures unchanged).
   - 26 pipeline/showrunner tests pass (`python -m pytest`).

## Key Commands
```
python -m src branch --vary genre --values fantasy,scifi --from premise --to structure --tree-load state.json --tree-save tree.json --provider mock
python -m src compare --labels fantasy,scifi --tree-load tree.json
python -m pytest tests/test_tree/ -q
python -m src run --to <checkpoint> --provider openai --load state.json --save state.json
```

## Known Issues
- `test_scene_writer_renders_prose` hangs (LLM retry loop, not called with mock)
- `test_compare_print_does_not_crash` fails (output format mismatch in assertion)
- `test_orphan_node_returns_root` fails (expected behavior for orphan nodes)
