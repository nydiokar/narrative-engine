# Context — Narrative Engine

## Current Status (June 20, 2026)

Full pipeline runs clean with real LLM (llama3.2 @ localhost:11434). All 8 checkpoints pass.

## Recent Work

### Session: Iterative Real-LLM Testing + Checkpoint Resume

**Goal:** Iterative stage-by-stage testing with a real LLM by adding checkpoint-aware
skip/resume to the pipeline.

**Achievements:**

1. **Checkpoint skip/resume** (`src/pipeline/checkpoints.py`):
   - `run_to_checkpoint()` accepts `start_from` param — Phase 1 verifies earlier
     checkpoints from store without running workflows; Phase 2 runs from `start_from`.
   - `find_next_checkpoint()` auto-detects resume point from loaded state.
   - `_checkpoint_introduces_new_types()` handles checkpoints that share contract
     type requirements with predecessors (`structure`, `draft`, `editorial`, `final`).
   - `_completed_checkpoints` set in `ContractStore` — serialized in snapshot/restore/save/load.

2. **Showrunner bug fix** (`src/agents/showrunner.py`):
   - `_approve_structure` was checking for episode/chapter contracts that don't exist
     yet at the structure stage (episodes are created in the next workflow).
   - Fixed: replaced Python-level episode validation with LLM call for structure approval.
   - Moved the 4-phase validation (`manipulation`, `competence`, `performance`, `sanction`)
     to `_approve_episodes` where it belongs.

3. **Prompt cleanup** (`src/agents/prompts/showrunner.md`, `.opencode/agents/showrunner.md`):
   - `approve_structure` no longer mentions "4 episodes should be present".
   - `approve_episodes` now explicitly describes phase validation.

4. **Final checkpoint auto-detect fix** (`src/pipeline/checkpoints.py:314`):
   - `final` checkpoint shares `critique` contract type with earlier stages (scenes
     produces critique via Greimas diagnostics).
   - Added `final` to the list of checkpoints that use `_completed_checkpoints`
     instead of contract-count verification.

**Pipeline verification (real LLM — llama3.2):**
- brief: 5/5 — PASS
- premise: 5/5 — PASS
- structure: 4/4 — PASS
- episodes: 5/5 (4 episodes, 12 chapters) — PASS
- scenes: 5/5 (36 scenes, all PASS diagnostics) — PASS
- draft: 3/3 — PASS
- editorial: 7/7 — PASS
- final: 5/5 (hard gate PASS, soft gate 5.0) — PASS

**Test status:**
- 36 relevant tests pass (showrunner: 16, store: 9, checkpoints: 10, base: 3)
- 2 pre-existing test failures unrelated to changes (compare print, orphan node)
- 1 pre-existing hanging test (test_scene_writer_renders_prose — LLM retry loop)

## Key Commands
```
python -m pytest tests/test_pipeline/test_checkpoints.py tests/test_agents/test_showrunner.py tests/test_agents/test_store.py -v
python -m src run --to <checkpoint> --provider openai --load state.json --save state.json
```

## Known Issues
- `test_scene_writer_renders_prose` hangs (LLM retry loop, not called with mock)
- `test_compare_print_does_not_crash` fails (output format mismatch in assertion)
- `test_orphan_node_returns_root` fails (expected behavior for orphan nodes)
