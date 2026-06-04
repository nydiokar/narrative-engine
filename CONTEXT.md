# Narrative Engine — Project Context

**Branch:** `main` | **Last Updated:** 2026-06-04 | **Status:** Phase H in progress — tree-based narrative workbench.

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

- **Pipeline (linear path)**: Full 8-workflow pipeline runs clean end-to-end with real LLM — all steps succeed, all checkpoints pass. 151 tests passing.
- **Tree layer**: Node model + ContractStore snapshot/restore done. Branch executor, compare, promote, CLI in progress.

### Critical Path — Phase H

| # | Task | Status |
|:-:|:-----|:-------|
| 1 | `TreeNode` model + store snapshot/restore | ✅ Done |
| 2 | Branch executor — run N variants from any node | 🚧 In progress |
| 3 | Compare — side-by-side contract viewer | ⬜ Pending |
| 4 | Promote/prune — navigate the tree | ⬜ Pending |
| 5 | Interactive CLI — demo.py branch commands | ⬜ Pending |
| 6 | LLM parameter variance (seed, top_p, etc.) | ⬜ Pending |

---

## What the Pipeline Does Today (with Real LLM)

1. ✅ **00-brief-and-taxonomy** — LLM selects themes, genre, world axes, character layers; Showrunner approves
2. ✅ **01-seed-to-premise** — LLM extracts actants, selects backbone grammar, drafts protagonist, approves
3. ✅ **02-premise-to-structure** — LLM builds fabula, checks constraints, validates theme fit
4. ✅ **03-structure-to-episodes** — LLM segments into 4 episodes, 12 chapters, refines arcs, assigns settings
5. ✅ **04-episodes-to-scenes** — LLM generates 24 scenes, all pass Greimas diagnostic; continuity verified
6. ✅ **05-scenes-to-draft** — Scenes finalized, continuity checked, draft/script/screenplay assembled
7. ✅ **06-editorial-passes** — Developmental evaluation, structural/script changes applied, continuity check
8. ✅ **07-critique-and-revision** — Hard gate PASS, soft gate PASS, cliché detection, final approval

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
- **Agents fall back to hardcoded generation** when LLM returns no `contract_data` — prevents pipeline from breaking mid-flow
- **Deterministic administrative steps**: `approve_final`, `assemble_*`, `refine_script` use structure validation instead of LLM calls for reliability
- **Medium-agnostic**: narrative core (Greimas, Propp, fabula, actants, character models, coherence) stays universal. Medium is a pipeline runtime parameter, not a story contract field.
- **Tree over ladder**: Instead of one linear path, the system is a tree. Branch at any depth, compare siblings, freeze + continue. The pipeline stages are depth levels, not sequential checkpoints.

---

## Quick Reference

| Command | Description |
|:--------|:------------|
| `python scripts/demo.py` | Full pipeline with mock LLM |
| `python scripts/demo.py --model qwen3-coder --medium animation` | Real LLM, animation workflow |
| `python scripts/demo.py --to scenes` | Stop after scenes checkpoint |
| `pytest tests/ -q` | Run all 151 tests |

### Key Paths

| Area | Path |
|:-----|:-----|
| Agent modules | `src/agents/*.py` |
| Prompt templates | `src/agents/prompts/*.md` |
| LLM provider | `src/agents/llm.py` |
| Director | `src/agents/director.py` |
| ContractStore | `src/agents/store.py` |
| **Tree layer** | `src/tree/` |
| Pydantic models | `src/contracts/models.py` |
| Checkpoints | `src/pipeline/checkpoints.py` |
| Pipeline orchestrator | `src/pipeline/orchestrator.py` |
| Greimas engine | `src/engine/greimas/`, `src/engine/fabula/` |
| Evaluation | `src/evaluation/` (HardGate, SoftGate, ClicheDetector) |
| Demo script | `scripts/demo.py` |
| ROADMAP | `ROADMAP.md` |
| Contract YAML schemas | `contracts/*.yaml` |
| Agent role cards | `agents/*.md` |
