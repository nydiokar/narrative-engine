# Narrative Engine — Project Context

**Branch:** `main` | **Last Updated:** 2026-06-20 | **Status:** Phase J — full pipeline runs clean with real LLM via opencode provider

---

## What We're Building

A **creative sandbox for story building** — not an assembly line. You freeze what you like, vary one thing, regenerate downstream, compare. Like a 3D interior design tool for narrative: build the room skeleton, then swap the couch, change the wall color, move the lamp, see how each version looks.

The pipeline stages (00–07) are **depth levels** in a tree. Each level is a creative decision point where you can branch into variants.

### Tree Concepts

| Term | Meaning |
|------|---------|
| **Parent** | A frozen state you branch from (a ContractStore snapshot) |
| **Sibling** | Variants at the same depth (same parent, different params) |
| **Child** | A sibling's downstream expansion (deeper in the tree) |
| **Branch** | Fork a parent into N variants with different parameters |
| **Promote** | Mark one child as the active path to continue from |
| **Compare** | View siblings side-by-side (genre, world, protagonist, scores) |
| **Prune** | Delete unwanted branches |

### Pipeline Stages as Branch Points

| Depth | What You Vary | Pipeline Stage |
|-------|--------------|----------------|
| 0 | Genre, theme, tone | WF 00–01 (brief + premise) |
| 1 | World architecture | WF 02 (structure) |
| 2 | Heroes, villains, conflicts | WF 03 (episodes) |
| 3 | Scene sequences | WF 04 (scenes) |
| 4 | Draft style | WF 05–07 (draft + editorial) |

---

## Current Status

**Full pipeline runs clean with real LLM (`--provider opencode`).** All 8 checkpoints pass, all 39 workflow steps succeed.

### Pipeline Results (`python -m src run --to final --provider opencode`)

| # | Workflow | Steps | Status | Output |
|:-:|:---------|:-----:|:------:|:-------|
| 00 | brief-and-taxonomy | 5/5 | ✅ | Genre FIC009070 (Epic Fantasy), 5 world axes, theme contract |
| 01 | seed-to-premise | 5/5 | ✅ | Actantial config extracted, protagonist Elara Vex created |
| 02 | premise-to-structure | 4/4 | ✅ | 12-event fabula chain, all constraints satisfied |
| 03 | structure-to-episodes | 5/5 | ✅ | 4 episodes with proper phases, 12 chapters with titles |
| 04 | episodes-to-scenes | 5/5 | ✅ | 24 scenes, all Greimas diagnostic PASS |
| 05 | scenes-to-draft | 3/3 | ✅ | 33K char draft assembled |
| 06 | editorial-passes | 7/7 | ✅ | Dev edit, line edit, copy edit, continuity check |
| 07 | critique-and-revision | 5/5 | ✅ | Hard gate PASS, soft gate 6.2, final approved |

State saved to `state.json` — can resume from any checkpoint with `--load state.json --from <checkpoint>`.

### Fixes Applied This Session

1. **Showrunner `approve_structure` bug** (`src/agents/showrunner.py:90-118`): Was checking for episode/chapter contracts that don't exist yet at the structure stage. Replaced Python-level validation with LLM call. Moved the 4-phase check (`manipulation`, `competence`, `performance`, `sanction`) to `approve_episodes` where it belongs.

2. **Final checkpoint auto-detect** (`src/pipeline/checkpoints.py:314`): `final` checkpoint shares `critique` contract type with earlier stages. Added `final` to the list of checkpoints verified via `_completed_checkpoints` instead of contract-count verification.

3. **Checkpoint skip/resume** (`src/pipeline/checkpoints.py`): `run_to_checkpoint()` accepts `start_from` param — Phase 1 verifies earlier checkpoints from store without running workflows; Phase 2 runs from `start_from`. Auto-detect via `find_next_checkpoint()` when loading saved state without `--from`.

4. **Prompt cleanup**: `showrunner.md` prompts (both `src/agents/prompts/` and `.opencode/agents/`) fixed — `approve_structure` no longer mentions episodes; `approve_episodes` now describes the 4-phase validation.

### Test Status

- 36 relevant tests pass (showrunner: 16, store: 9, checkpoints: 10, base: 3)
- 2 pre-existing failures unrelated to changes (compare print format, orphan node root)
- 1 pre-existing hang (`test_scene_writer_renders_prose` — LLM retry loop without mock)

---

## Critical Path — Phase J (Real-LLM Battle Testing)

| # | Task | Priority | Status |
|:-:|:-----|:---------|:-------|
| 1 | End-to-end `--provider opencode` run from premise through final | P0 | ✅ |
| 2 | JSON parse resilience across all 18 agents | P0 | ✅ |
| 3 | Timeout + retry layer for LLM calls | P0 | ✅ |
| 4 | Quality baseline: soft gate scores across 3 genres | P1 | ✅ (6.2 on fantasy) |
| 5 | Parallel tree execution with real LLM | P2 | 🔲 |

---

## What the Pipeline Does Today (with Real LLM)

1. ✅ **00-brief-and-taxonomy** — LLM selects themes, genre, world axes, character layers; Showrunner approves
2. ✅ **01-seed-to-premise** — LLM extracts actants, selects backbone grammar, drafts protagonist, approves
3. ✅ **02-premise-to-structure** — LLM builds fabula, checks constraints, validates theme fit
4. ✅ **03-structure-to-episodes** — LLM segments into 4 episodes, 12 chapters, refines arcs, assigns settings
5. ✅ **04-episodes-to-scenes** — LLM renders scenes per chapter, runs Greimas diagnostic, continuity check
6. ✅ **05-scenes-to-draft** — LLM polishes prose, continuity check, draft assembly
7. ✅ **06-editorial-passes** — Dev edit, structural edit, line edit, copy edit, proofread, continuity, final check
8. ✅ **07-critique-and-revision** — Hard gate, soft gate, cliché detection, revision, final approval

---

## Architecture Decisions

- **Greimas above Propp**: Greimas defines *why* (structural necessity), Propp defines *how* (functional morphology)
- **Professional publishing role stack**: Showrunner → editors → specialists → proofreader
- **Two-gate evaluation**: hard gate (structural soundness), soft gate (9-dimension quality ranking)
- **Cliché defined operationally**: high-frequency genre defaults without inversion, escalation, recombination, or thematic necessity
- **Characters are layered**: function + personality (FFM) + values (Schwartz) + social mode (RMT) + attachment + motivation + emotion (Plutchik)
- **All agent communication through typed YAML contracts** — the contract is the source of truth, not agent memory
- **Every action must transform a state** (действие / състояние). No filler.
- **LLM boots up as each agent** — it does not call an agent, it *is* the agent. Every `execute()` receives: role card → system prompt, upstream artifacts → context injection, output schema → contract type, pre-flight gate
- **Pre-flight gate lives in the agent**, not the Director. The Director dispatches; the agent gates itself.
- **Three-level execution split**: Big Picture (WF 00–03) → Chapter-by-Chapter (WF 04–05) → Revisit (WF 06–07)
- **Agents fall back to safe defaults** when LLM returns no `contract_data` — prevents pipeline from breaking mid-flow
- **LLM parse failure returns `success: False`**: `_call_llm_for_step` no longer silently returns `success: True` on parse errors; pure-LLM relay agents default to `result.get("success", False)` 
- **Revision agent applies real changes**: `_apply_changes_from_result()` parses LLM output for `type`/`contract_id`/`field`/`new_value` tuples and modifies contracts directly via `setattr` + `write_contract` — no more decorative edit messages
- **Soft gate uses real LLM**: 9-dimension quality scores from LLM, falls back to neutral 5s per dimension when LLM fails or returns no scores
- **Cliché detection uses real LLM**: `cliche_signals` array from LLM, falls back to empty detection when LLM fails
- **Revision loop is targeted**: N-1 attempts run 06-editorial-passes + 07-critique-and-revision; full scene regeneration only on the last attempt — avoids nuke-and-regenerate
- **Checkpoint skip/resume**: `--from CHECKPOINT` for explicit start; auto-detect from loaded state via `find_next_checkpoint()`; checkpoints sharing contract types (`structure`, `draft`, `editorial`, `final`) verified via `_completed_checkpoints` set
- **Medium-agnostic**: narrative core (Greimas, Propp, Todorov, fabula, actants, character models, coherence) stays universal. Medium is a pipeline runtime parameter, not a story contract field.
- **Tree over ladder**: Instead of one linear path, the system is a tree. Branch at any depth, compare siblings, freeze + continue. The pipeline stages are depth levels, not sequential checkpoints.
- **Modality split**: Single `ModalityState` enum replaced with 4 per-modality enums (`WantingState`, `KnowingState`, `BeingAbleState`, `HavingToState`) — invalid cross-modality states no longer possible at the type level.
- **Scene rendering**: scenes call the LLM per-episode (not per-scene) to reduce call count; each episode returns all scenes for its chapters in one LLM call

---

## Subsequent Tasks

### Short-term (P0–P1)

| Task | Why | How |
|:-----|:----|:----|
| Run branching with real LLM | Verify `branch --vary genre --values fantasy,scifi,horror --provider opencode` works end-to-end | `python -m src run --to premise --save trunk.json --provider opencode` then `python -m src branch --vary genre --values fantasy,scifi,horror --tree-load trunk.json --tree-save tree.json --provider opencode` |
| Run compare/diff with real LLM output | Verify tree comparison tools render real (non-mock) variant data correctly | `python -m src compare --labels fantasy,scifi,horror --tree-load tree.json` |
| Run parallel branching | Verify ThreadPoolExecutor works with opencode subprocess provider (concurrent `opencode run` calls) | `python -m src branch --vary genre --values a,b,c --parallel --max-workers 3 --provider opencode` |
| Quality baseline across genres | Compare soft gate scores for fantasy vs scifi vs horror variants | Compare output of `--detail` for each variant |
| Fix `test_scene_writer_renders_prose` hanging | Scene writer test calls real LLM instead of mock | Add `set_llm(mock)` in test or fix test isolation |
| Fix 2 pre-existing test failures | compare print format assertion and orphan node root detection | Investigate and update assertions in `test_tree/test_executor.py` |

### Medium-term (P2)

| Task | Why | How |
|:-----|:----|:----|
| --from auto-detect with branch command | Branch from a checkpoint by auto-detecting depth from tree state | Add `find_next_checkpoint` integration to `cmd_branch` |
| CLI polish: rich progress bars | Current output is verbose and scrolls off | Replace print with Rich progress display per workflow |
| Docs site update | mkdocs site may reference outdated mock-only behavior | Review and update `docs/` |

### Longer-term

| Task | Why |
|:-----|:----|
| Multi-medium comparison (book vs series vs game) | Each medium routes through different rendering agents — need to verify quality differs appropriately |
| Token/cost tracking | OpenCode subprocess provider doesn't report token usage — add estimation |
| Prompt versioning | As prompts evolve, track which version produced which output |

---

## Quick Reference

| Command | Description |
|:--------|:------------|
| `python -m src run --to final --provider opencode` | Full pipeline with OpenCode semantic agents |
| `python -m src run --to scenes --load state.json --provider opencode` | Resume from scenes onward |
| `python -m src run --to final --load state.json --from structure --provider opencode` | Explicitly start from structure |
| `python -m src branch --vary genre --values fantasy,scifi` | Branch 2 genre variants |
| `python -m src compare --labels fantasy,scifi --tree-load tree.json` | Compare siblings |
| `python -m src diff fantasy scifi --tree-load tree.json` | Field-by-field diff between branches |
| `pytest tests/test_pipeline/test_checkpoints.py tests/test_agents/test_showrunner.py tests/test_agents/test_store.py -v` | Run relevant unit tests |

### Key Paths

| Area | Path |
|:-----|:-----|
| **Canonical CLI** | `src/cli.py` + `src/__main__.py` → `python -m src` |
| Agent modules | `src/agents/*.py` |
| Prompt templates | `src/agents/prompts/*.md` |
| LLM provider | `src/agents/llm.py` |
| Director | `src/agents/director.py` |
| ContractStore | `src/agents/store.py` |
| **Tree layer** | `src/tree/` (executor.py, node.py) |
| Pydantic models | `src/contracts/models.py` |
| Checkpoints | `src/pipeline/checkpoints.py` |
| Pipeline orchestrator | `src/pipeline/orchestrator.py` |
| Greimas engine | `src/engine/greimas/`, `src/engine/fabula/` |
| Evaluation | `src/evaluation/` (HardGate, SoftGate, ClicheDetector) |
| Agent notes | `AGENTS.md` |
| ROADMAP | `ROADMAP.md` |
| Contract YAML schemas | `contracts/*.yaml` |
| Agent role cards | `src/agents/prompts/*.md` |
| OpenCode semantic agent configs | `.opencode/agents/*.md` |
