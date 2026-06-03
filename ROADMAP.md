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

## Phase G (Latest) — Prompt Templates for All Agents + Persistence

- [x] 12 new prompt templates written (Character Simulator, Dialogue Specialist, World Researcher, Worldbuilder, Chapter Planner, Continuity Editor, Developmental Editor, Line Editor, Copy Editor, Proofreader, Revision Agent, Theme Specialist)
- [x] All 19 workflow-active agents now call the LLM through their prompt
- [x] Scene Writer prompt enhanced: minimum 100 words of real content per scene
- [x] ContractStore.save(path) / ContractStore.load(path) — full JSON serialization
- [x] demo.py --save <path> / --load <path> flags
- [x] 151 / 151 tests passing

---

## Phase H — Narrative Simulation Workbench (Next Major Feature)

The goal: turn the pipeline from a linear generator into an **interactive creative lab** where you can explore, compare, freeze, and combine.

### Core Capabilities

| Capability | What It Means |
|:-----------|:--------------|
| **Fork at any checkpoint** | `--to premise --variants 5` generates 5 different structural approaches from the same premise |
| **Vary creative parameters** | Per-variant: temperature, top_p, top_k, genre override, tone injection, seed prompt |
| **Rank and compare** | Side-by-side table with hard gate + soft gate scores per variant |
| **Cherry-pick** | Take variant A's premise, variant B's structure, variant C's episodes — merge into a single path |
| **Freeze / lock** | Lock contracts you're happy with so subsequent passes don't overwrite them |
| **Continue from any point** | Load a saved state, fork from it, run forward to a target checkpoint |

### Why This Matters

The current pipeline is deterministic once you pick a premise and model. A human writer explores 10+ structural approaches before committing. The workbench makes this possible:

```
# Example session
$ python scripts/demo.py --model qwen3-coder --to premise --variants 3
  # → sees 3 different actant configurations, picks the best

$ python scripts/demo.py --load best_premise.json --to structure --variants 5 --vary genre
  # → tries 5 genres on the same premise, ranks them

$ python scripts/demo.py --load best_structure.json --to final
  # → locks it, runs through full pipeline
```

### LLM Parameters Gap

Currently `OpenAILLMProvider` only exposes `temperature` and `max_tokens`. To support creative variance we need:
- [ ] `top_p` (nucleus sampling)
- [ ] `top_k` (top-k sampling)
- [ ] `frequency_penalty`
- [ ] `presence_penalty`
- [ ] Seed parameter (for reproducible variance)
- [ ] Per-call parameter override (not just global defaults)

---

## Downstream (future)

| Area | What |
|:-----|:------|
| Quality & Iteration | Revisit triggers, editorial passes with real analysis, showrunner final approval |
| Infrastructure | ModalityState split, Propp/Todorov/GOLEM models, save/load, CLI, test coverage |
| Human Interface | Intake form, release package, legal/bias check |
| Concept Branching | Multi-draft comparison, "generate 3 concepts" workflow variant |

---

## Known Design Debt

- ModalityState single enum allows invalid cross-modality states — split into per-modality enums deferred
- Propp function sequence validation and Todorov equilibrium validation stubbed but not implemented
- ContractStore singleton leaks state across tests — safe in serial, unsafe in parallel
- GOLEM event model (goal→action→outcome→event→perception→internal element) referenced in specs, not coded
- 25 Python modules lack dedicated unit tests
