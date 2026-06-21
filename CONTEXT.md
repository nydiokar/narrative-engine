# Context — Narrative Engine

## Current Status (June 21, 2026)

All 435 tests pass. Full pipeline runs clean with real LLM (llama3.2 @ localhost:11434, OpenCode big-pickle).
Branching (sequential + parallel) works with correct contract seeding + variant comparison.
ROADMAP.md and CONTEXT.md aligned. 3 power moves defined and documented.

## Recent Work

### Session: Roadmap Alignment + Power Moves Defined

**Goal:** Align ROADMAP.md with actual project state. Define the next 3 power moves in CONTEXT.md for immediate forward reference.

**Achievements:**

1. **Phase J updated** in ROADMAP.md — 4 must-haves and 1 nice-to-have marked done based on verified code inspection (real-LLM end-to-end, structured output enforcement, timeout+retry layer, parallel tree execution). Remaining 2 nice-to-haves preserved.
2. **Phase K added** — "Output Quality & Medium Completeness" with 3 power moves as the active next phase.
3. **3 power moves written into CONTEXT.md** — non-book assemblers, discourse contract wiring, quality baseline + regression suite.
4. **Known Issues updated** in CONTEXT.md to reflect actual remaining gaps.
5. **Design debt updated** in ROADMAP.md — stale "Pipeline not battle-tested" entry removed, replaced with current state.

**Next action:** Start Power Move #1 — ship non-book assemblers.

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

## Next Power Moves

| # | Move | Why | Status |
|---|------|-----|--------|
| 1 | **Ship non-book assemblers** — `_assemble_script`, `_assemble_screenplay`, `_assemble_teleplay` write real output files (currently counting stubs at `showrunner.py:172–194`) | Only book medium produces a readable file (`output/draft.md`). Animation/movie/series produce nothing. | 🔴 Not started |
| 2 | **Wire discourse contract** — `DiscourseContract` defined but zero agents call `write_contract("discourse", ...)`. Connect it to scene writer prompts so POV/tense/voice settings are respected. | Structural gap affecting all mediums. Author intent (voice, perspective) is invisible to the pipeline. | 🔴 Not started |
| 3 | **Quality baseline + regression suite** — Run 3 genres full pipeline with real LLM, collect soft gate scores. Snapshot LLM output parsing per agent. | No data-driven measure of output quality. Changes can regress without detection. | 🔴 Not started |

## Key Commands
```
python -m src branch --vary genre --values fantasy,scifi --from premise --to structure --tree-load state.json --tree-save tree.json --provider opencode
python -m src branch --vary genre --values fantasy,scifi,horror --parallel --max-workers 3 --tree-load state.json --tree-save tree.json
python -m src compare --labels fantasy,scifi --tree-load tree.json --detail
python -m pytest tests/ -q
```

## Known Issues
- `_assemble_script`, `_assemble_screenplay`, `_assemble_teleplay` stubs — produce no output file
- `DiscourseContract` registered but never populated by any agent
- No quality baseline: soft gate scores from real LLM never collected
- ContractStore singleton leaks state across tests
- 25 Python modules lack dedicated unit tests
