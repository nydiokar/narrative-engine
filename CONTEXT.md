# Narrative Engine — Project Context

**Branch:** `main` | **Last Updated:** 2026-06-08 | **Status:** Phase I — editorial/revision real-LLM wiring + Propp + Todorov + Modality split complete; Phase H tree workbench live.

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

- **Pipeline (linear path)**: Full 8-workflow pipeline runs clean end-to-end with real LLM — all steps succeed, all checkpoints pass. **254 tests passing**.
- **Editorial/Revision**: Soft gate and cliché detection now call the real LLM for evaluation scores. Revision agent applies real contract modifications. Revision loop uses targeted editorial passes (N-1) before full regeneration instead of nuke-and-regenerate.
- **Tree layer**: All core operations implemented. Canonical CLI (`python -m src`) has `run`, `branch`, `compare`, `promote`, `prune`, `show`, `set`, `lock`, `unlock` commands.

### Critical Path — Phase H

| # | Task | Status |
|:-:|:-----|:-------|
| 1 | `TreeNode` model + store snapshot/restore | ✅ Done |
| 2 | Branch executor — run N variants from any node | ✅ Done |
| 3 | Compare — side-by-side contract viewer | ✅ Done |
| 4 | Promote/prune — navigate the tree | ✅ Done |
| 5 | Canonical CLI — `python -m src branch/compare/promote/prune/show` | ✅ Done |


---

## What the Pipeline Does Today (with Real LLM)

1. ✅ **00-brief-and-taxonomy** — LLM selects themes, genre, world axes, character layers; Showrunner approves
2. ✅ **01-seed-to-premise** — LLM extracts actants, selects backbone grammar, drafts protagonist, approves
3. ✅ **02-premise-to-structure** — LLM builds fabula, checks constraints, validates theme fit
4. ✅ **03-structure-to-episodes** — LLM segments into 3 episodes, 9 chapters, refines arcs, assigns settings
5. ✅ **04-episodes-to-scenes** — LLM generates 2+ scenes per episode, all pass Greimas diagnostic; continuity verified
6. ✅ **05-scenes-to-draft** — Scenes finalized, continuity checked, draft assembled
7. ✅ **06-editorial-passes** — Developmental, structural, line, copy, proofread passes; revision agent applies LLM-generated changes to contracts
8. ✅ **07-critique-and-revision** — Hard gate (structural), soft gate (LLM-evaluated 9-dimension scores, fallback to neutral 5s), cliché detection (LLM-signaled, fallback to empty), revision loop (N-1 targeted editorial passes, then full regeneration)

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
- **Deterministic administrative steps**: `approve_final`, `assemble_*`, `refine_script` use structure validation instead of LLM calls for reliability
- **Medium-agnostic**: narrative core (Greimas, Propp, Todorov, fabula, actants, character models, coherence) stays universal. Medium is a pipeline runtime parameter, not a story contract field.
- **Tree over ladder**: Instead of one linear path, the system is a tree. Branch at any depth, compare siblings, freeze + continue. The pipeline stages are depth levels, not sequential checkpoints.
- **Modality split**: Single `ModalityState` enum replaced with 4 per-modality enums (`WantingState`, `KnowingState`, `BeingAbleState`, `HavingToState`) — invalid cross-modality states no longer possible at the type level.

---

## Quick Reference

| Command | Description |
|:--------|:------------|
| `python -m src run --to premise` | Run pipeline with mock LLM to premise |
| `python -m src branch --vary genre --values fantasy,scifi` | Branch 2 genre variants |
| `python -m src compare --labels fantasy,scifi --tree-load tree.json` | Compare siblings |
| `python -m src promote fantasy --tree-load tree.json --tree-save tree.json` | Promote a branch |
| `python -m src show --tree-load tree.json` | ASCII tree visualization |
| `python -m src set story.genre.primary_bisac=FIC002000` | Set a contract field |
| `python -m src lock story.genre` | Lock a field |
| `pytest tests/ -q` | Run all 254 tests |

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
| Legacy demo | `scripts/demo.py` (use `python -m src` instead) |
| Agent notes | `AGENTS.md` |
| ROADMAP | `ROADMAP.md` |
| Contract YAML schemas | `contracts/*.yaml` |
| Agent role cards | `src/agents/prompts/*.md` (root `agents/*.md` is orphaned) |
