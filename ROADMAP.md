# Roadmap — Narrative Engine

## Architectural Vision

The Narrative Engine is a **structured but not closed** system. The LLM boots up as each professional role — it does not call an LLM, it *is* the agent. Every agent gets:

1. Its **role card** — "You are the Structuralist. You do X, Y, Z."
2. **Upstream artifacts** — contracts from agents that must execute first
3. **Output schema** — the contract type it must produce
4. **Workflow context** — what stage of the pipeline we are in

### Three-Level Execution Split

```
BIG PICTURE (WF 00–03)
  Actantial model, narrative programs, episode architecture,
  conflict arcs, character arcs — the structural skeleton.
  Decided once, revisited after each episode or on hard-gate failure.

CHAPTER-BY-CHAPTER (WF 04–05)
  Per-chapter scenes, emotional arcs, discourse rendering —
  the local execution. Informed by Big Picture.

REVISIT (WF 06–07)
  Editorial passes and critique. Loops until gates pass.
  Can send back to Big Picture (structural) or Chapter-by-Chapter (prose/continuity).
```

---

## Phase A–E ✅ (Done)

Foundation: scaffold, 53+ models, YAML loader, Greimas Fabula Coherence Engine (8 checks), action/state validator, causality graph, modality validator, two-gate evaluation (HardGate + SoftGate + ClicheDetector), 20-agent framework with ContractStore/MockLLMProvider/Director/PipelineOrchestrator, full pipeline integration test (22 tests, all 8 workflows seed→draft), 149 tests passing.

---

## Phase F ✅ (Done)

Dynamic Agent System — LLM as role-booted agent.

- [x] Prompt engine (load templates, render with context injection)
- [x] Context injection via `_gather_upstream_yaml()`
- [x] Pre-flight gates in all 6 prompted agents
- [x] Structured output enforcement (JSON parsing + Pydantic validation)
- [x] Real LLM provider (OpenAI-compatible, tested with Ollama qwen3-coder)
- [x] 6 prompt templates: showrunner, structuralist, character_architect, outline_planner, scene_writer, critic
- [x] Fallback chain: LLM output → validate → graceful hardcoded fallback

---

## Critical Path — Next 3 Tasks

These are what blocks producing a valid draft from a real LLM. Everything else is downstream.

### 1. Fix Scene Writer Prompt
Real LLM produces scenes that pass Pydantic schema validation but fail the Greimas 5-question diagnostic. Root cause: the prompt template doesn't adequately constrain `value_object_change` and `future_action_possible_or_blocked` fields. Fix with better exemplars, explicit field descriptions, and a validation example demonstrating the required format.

### 2. Wire the Revision Loop
Workflow 07 (critique-and-revision) currently runs once — hard gate reports failures but the pipeline accepts them and moves on. Fix: when Critic returns hard gate violations, the Revision Agent must receive them and iterate (re-enter at the appropriate level) until all structural checks pass. This is the core quality mechanism of the entire system.

### 3. Prompt Templates for Remaining 14 Agents
The remaining agents (Character Simulator, Dialogue Specialist, World Researcher, Worldbuilder, Chapter Planner, Continuity Editor, Script Editor, Developmental Editor, Line Editor, Copy Editor, Proofreader, Revision Agent, Theme Specialist, Showrunner-extra steps) are hardcoded stubs. They return success messages but don't call the LLM or generate meaningful contract data. Writing prompt templates makes the full publishing stack LLM-driven end-to-end.

---

## Downstream (after critical path)

| Area | What |
|:-----|:------|
| Big Picture Planning | Actantial-level planning, episode goal setting, conflict architecture, character arc architecture |
| Chapter Writing | Per-chapter scenes, character simulation, dialogue planning, discourse rendering + actual prose |
| Quality & Iteration | Revisit triggers, editorial passes with real analysis, showrunner final approval |
| Infrastructure | ModalityState split, Propp/Todorov/GOLEM models, save/load, CLI, test coverage |
| Human Interface | Intake form, release package, legal/bias check |

---

## Known Design Debt

- ModalityState single enum allows invalid cross-modality states — split into per-modality enums deferred
- Propp function sequence validation and Todorov equilibrium validation stubbed but not implemented
- ContractStore singleton leaks state across tests — safe in serial, unsafe in parallel
- GOLEM event model (goal→action→outcome→event→perception→internal element) referenced in specs, not coded
- 25 Python modules lack dedicated unit tests
