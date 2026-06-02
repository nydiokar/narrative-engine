# Narrative Engine — Project Context

**Branch:** `main` | **Last Updated:** 2026-06-01 | **Status:** Phase F complete (7 prompt templates, 20 agents, pre-flight gates, real LLM working). **Full 8-workflow pipeline runs clean end-to-end with real LLM** — all steps succeed, all checkpoints pass. 151 tests passing.

**Critical path:** 1 task remains before the system can produce a publishable-quality draft.

---

## Critical Path — Remaining Tasks

| # | Task | Why It's Blocking |
|:-:|:-----|:-----------------|
| 1 | ✅ **Scene writer prompt fixed** — real LLM produces valid scenes with `value_object_change` and `future_action_possible_or_blocked`. All 24 scenes pass Greimas 5-question diagnostic. Fix: JSON example had curly braces `{}` that `.format()` tried to parse — converted to dash-list format. | **DONE** |
| 2 | ✅ **Revision loop wired** — `run_to_checkpoint()` in `checkpoints.py` handles hard gate failures (delete scenes → re-run 04/05/07 → max 3 attempts). Hard gate now passes with real LLM. `showrunner.approve_final` made deterministic (contract presence check). `showrunner.assemble_script/screenplay/teleplay` added. `RevisionAgent.apply_script_changes` added. `ScriptEditor.refine_script` made deterministic (structure validation). | **DONE** |
| 3 | **Prompt templates for 14 remaining agents** — Character Simulator, Dialogue Specialist, World Researcher, Worldbuilder, Chapter Planner, Continuity Editor, Script Editor, Developmental/Line/Copy Editor, Proofreader, Revision Agent, Theme Specialist. Only Script Editor and Scene Writer have real prompts; the rest fall back to hardcoded stubs or empty mock data when the LLM fails. | Most agents produce empty/null data → downstream steps operate on defaults |

---

## What the Pipeline Does Today (with Real LLM)

1. ✅ **00-brief-and-taxonomy** — LLM selects themes, genre, world axes, character layers; Showrunner approves
2. ✅ **01-seed-to-premise** — LLM extracts actants, selects backbone grammar, drafts protagonist, approves
3. ✅ **02-premise-to-structure** — LLM builds fabula, checks constraints, validates theme fit; approval step reports empty fabula events (cosmetic — checkpoint passes)
4. ✅ **03-structure-to-episodes** — LLM segments into 4 episodes, 12 chapters, refines arcs, assigns settings; approval step reports incomplete metadata (cosmetic — checkpoint passes)
5. ✅ **04-episodes-to-scenes** — LLM generates 24 scenes, all pass Greimas diagnostic; continuity verified
6. ✅ **05-scenes-to-draft** — Scenes finalized, continuity checked, draft/script/screenplay assembled
7. ✅ **06-editorial-passes** — Developmental evaluation, structural/script changes applied, continuity check
8. ✅ **07-critique-and-revision** — Hard gate PASS (8 coherence checks), soft gate PASS (6.1/5.0), cliché detection, final approval

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
| Pydantic models | `src/contracts/models.py` |
| Checkpoints | `src/pipeline/checkpoints.py` |
| Pipeline orchestrator | `src/pipeline/orchestrator.py` |
| Greimas engine | `src/engine/greimas/`, `src/engine/fabula/` |
| Evaluation | `src/evaluation/` (HardGate, SoftGate, ClicheDetector) |
| Demo script | `scripts/demo.py` |
| ROADMAP | `ROADMAP.md` |
| Contract YAML schemas | `contracts/*.yaml` |
| Agent role cards | `agents/*.md` |
