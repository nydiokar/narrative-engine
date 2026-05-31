# Narrative Engine — Project Context

**Branch:** `main` | **Last Updated:** 2026-05-31 | **Status:** Phase F complete (6 prompt templates, pre-flight gates, real LLM working). Pipeline runs end-to-end with real LLM (qwen3-coder via Ollama) but scenes fail Greimas diagnostic and hard gate rejects without iterating. 149 tests passing.

**Critical path:** 3 tasks remain before the system can produce a valid draft from a real LLM.

---

## Critical Path — What Must Be Done

| # | Task | Why It's Blocking |
|:-:|:-----|:-----------------|
| 1 | **Fix scene writer prompt** — real LLM produces scenes with empty `value_object_change` and `future_action_possible_or_blocked`, causing the Greimas 5-question diagnostic to fail all 6 scenes | Pipeline accepts bad data → every downstream check fails |
| 2 | **Wire the revision loop** — workflow 07 runs critique once, reports hard gate failure, then passes. Must iterate (critique → revision → re-critique) until all structural checks pass | No quality mechanism exists without this — the system can't improve its own output |
| 3 | **Prompt templates for 14 remaining agents** — Character Simulator, Dialogue Specialist, World Researcher, Worldbuilder, Chapter Planner, Continuity Editor, Script Editor, Developmental/Line/Copy Editor, Proofreader, Revision Agent, Theme Specialist | Pipeline works but most agents are pass-through stubs that generate no meaningful data |

---

## What the Pipeline Does Today

1. ✅ Brief & taxonomy — story seeded, themes selected, genre set
2. ✅ Seed → premise — actants extracted, protagonist drafted
3. ✅ Fabula structure — 8 coherence checks pass, LLM builds fabula
4. ✅ Episodes — LLM generates 4 episodes with real titles ("The Trap Revealed", "The Final Ascent")
5. ❌ Scenes — LLM generates scenes but they fail Greimas diagnostic (missing value_object_change)
6. ✅ Draft — assembled from scenes
7. ✅ Editorial passes — all hardcoded stubs, always pass
8. ❌ Critique — hard gate rejects scenes but pipeline continues, no iteration

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

---

## Quick Reference

| Command | Description |
|:--------|:------------|
| `python scripts/demo.py` | Full pipeline with mock LLM |
| `python scripts/demo.py --model qwen3-coder` | Full pipeline with real LLM |
| `python scripts/demo.py --to scenes` | Stop after scenes checkpoint |
| `pytest tests/ -q` | Run all 149 tests |

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
