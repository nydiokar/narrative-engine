# Roadmap

## Architectural Vision

The Narrative Engine is a **structured but not closed** system. The LLM boots up as each professional role — it does not call an LLM, it *is* the agent. Every agent gets:

1. Its **role card** — "You are the Structuralist. You do X, Y, Z."
2. **Upstream artifacts** — contracts from agents that must execute first
3. **Output schema** — the contract type it must produce
4. **Workflow context** — what stage of the pipeline we are in

If an agent attempts to execute without all prerequisites present, a **pre-flight gate** catches it: *"You need the Character Architect's output first — go back."*

### Three-Level Execution Split

```
BIG PICTURE (WF 00–03)
  └─ Actantial model, narrative programs, episode architecture,
     conflict arcs, character arcs — the structural skeleton
     of the entire story. Decided once, revisited after each episode.

CHAPTER-BY-CHAPTER (WF 04–05)
  └─ Per-chapter scenes, emotional arcs, discourse rendering —
     the local execution. Informed by Big Picture, feeds back
     discoveries that may trigger a Big Picture revisit.

REVISIT (WF 06–07)
  └─ Editorial passes and critique. Can send you back to either
     Big Picture (structural failure) or Chapter-by-Chapter
     (prose/continuity failure). Loops until gates pass.
```

The system is **not a closed pipeline** — agents can work granularly, piece by piece. The Director manages the overall flow, but any agent can flag missing prerequisites and trigger a backstep.

---

## Phase A–E: Foundation ✅ (DONE)

- [x] Directory structure and scaffold (README, ROADMAP, docs, research, contracts, agents, workflows, templates, stories)
- [x] Greimas actantial model with value-states, canonical schema, action/state logic
- [x] Propp function mapping (32 functions) and Todorov equilibrium model
- [x] Story-logic constraints (causality, modality 4-axiom, no-filler, Greimas 5-question diagnostic)
- [x] Complete narrative ontology stack (12 layers: brief → evaluation)
- [x] 20 agent role cards (professional publishing role stack)
- [x] 8 workflow specifications (00–07)
- [x] types_maps.md integration — 9 new research files, 6 updated, 4 contracts extended
- [x] Python scaffold — pyproject.toml, 53+ Pydantic models, YAML loader, config
- [x] Greimas Fabula Coherence Engine — 8 diagnostic checks, action/state validator, causality graph, modality validator
- [x] Two-gate evaluation — HardGate (structural soundness), SoftGate (9-dimension quality scoring)
- [x] Cliché detection — 14-signal detector, novelty penalty, freshness generators
- [x] Agent framework — ContractStore, BaseAgent, MockLLMProvider, Director, PipelineOrchestrator
- [x] 20 agent Python modules — all importable, all dispatch correctly
- [x] Full pipeline integration test — 22 tests, all 8 workflows, seed→draft
- [x] **149 tests passing**

---

## Phase F: Dynamic Agent System 🔴 NEXT

The LLM becomes the agent. Replace all stub `execute()` methods with role-prompted LLM calls.

### F1 — Prompt Template Engine
- Each role card → a system prompt template that defines:
  - Professional identity ("You are the Character Architect.")
  - Core responsibilities (from the role card)
  - Quality standards (from research docs)
  - Tone and methodology guidance
- Template variables for dynamic injection: `{upstream_contracts}`, `{workflow_context}`, `{output_schema}`

### F2 — Context Injection
- Before each agent executes, gather all relevant upstream contracts from the store
- Inject into the prompt: "Here are the contracts available to you: [story, theme, genre, character...]"
- The agent sees only what it needs, but nothing is hidden — it can request more if needed

### F3 — Pre-Flight Gate
- Each agent declares its prerequisites (what contract types must exist before it can work)
- Before `execute()` runs, verify all prerequisites are in the store
- If missing: `AgentResult(success=False, errors=["Missing prerequisite: need 'chapter' contracts from Chapter Planner"])`
- The Director receives the failure and can re-route or pause

### F4 — Structured Output Enforcement
- Each agent's output schema = a contract type (StoryContract, CharacterContract, SceneContract, etc.)
- The LLM generates YAML conforming to the contract schema
- Validate output against Pydantic model before writing to store
- If output fails validation: return error, ask LLM to retry

### F5 — Real LLM Provider
- Wire OpenAI, Anthropic, or local models (Ollama, vLLM)
- The provider is a thin adapter — all agent logic lives in prompts, not code
- Fallback to MockLLMProvider for testing

**Checkpoint:** A real LLM (e.g. Claude, Hermes) can act as any single agent, take real contracts as input, and produce valid output contracts.

---

## Phase G: Big Picture Architecture 🟡 NEXT

The structural skeleton of the entire story — decided at the start, revisited after each episode or on hard-gate failure.

### G1 — Actantial-Level Planning (Structuralist)
- Receive premise → extract actantial configuration (Subject, Object, Sender, Receiver, Helper, Opponent)
- Define the canonical narrative program: Manipulation → Competence → Performance → Sanction
- Output: NarrativeProgram contracts with value-object trajectories

### G2 — Episode-Level Goal Setting (Outline Planner)
- Divide the fabula into 3-5 episodes
- Each episode has: dominant narrative program, conflict arc, emotional arc
- Each episode declares: "What must be true at the end of this episode for the next to begin?"
- Output: EpisodeContract with greimas_tracking and modality projections

### G3 — Conflict Architecture (Theme Specialist + Structuralist)
- Design the global conflict hierarchy: which conflicts are active per episode, how they escalate
- Classical conflict types + operations per episode
- Output: ConflictContract with per-episode conflict loads

### G4 — Character Arc Architecture (Character Architect)
- For each protagonist: initial state → desired state → terminal state (per episode)
- Modality shifts planned per episode (what changes, what triggers the change)
- Output: CharacterContract with arc, modality projections

### G5 — Revisit Triggers
- After each episode completes: run a "Big Picture sync" — does the episode's outcome still serve the overall actantial plan?
- If not: Structuralist re-evaluates, proposes adjustments
- Hard gate failure on continuity/causality: automatic Big Picture revisit

---

## Phase H: Chapter-by-Chapter Writing 🟡 NEXT

Local execution — each chapter's scenes, discourse, and prose.

### H1 — Per-Chapter Scene Planning (Chapter Planner)
- For each chapter: declare scenes, their Greimas function, conflict load, emotional arc
- Scene types selected from taxonomy (confrontation, discovery, reversal, etc.)
- Output: SceneContract per scene, linked to ChapterContract

### H2 — Character Simulation (Character Simulator)
- For each scene: simulate each character present → produce emotional state, modality state, likely action
- Flag character-inconsistent developments before writing
- Output: character state vectors per scene

### H3 — Dialogue Planning (Dialogue Specialist)
- Per scene: which characters speak, what speech acts, what narrative function
- Ensure each line serves a purpose (no filler dialogue)
- Output: dialogue annotations per scene

### H4 — Discourse Rendering (Scene Writer)
- Apply DiscourseContract (POV, focalisation, tense, voice) to each scene
- Render prose that satisfies the Greimas diagnostic (state before → action → state after)
- Output: SceneContract with content, word count, Greimas diagnostic

### H5 — Chapter-Level Quality Check (Continuity Editor)
- After each chapter: verify character consistency, causality, world rules, discourse consistency
- If issues found: flag and route to Scene Writer for fixes, or to Big Picture if structural

---

## Phase I: Revision Loop 🟡 NEXT

The critique feedback cycle — not a single pass, but a loop until gates clear.

### I1 — Hard Gate Drives Rejection
- Critic runs HardGate on the draft
- If any structural check fails: Revision Agent receives specific violations
- Revision Agent applies targeted fixes and loops back
- Loop continues until all hard gates pass

### I2 — Soft Gate Drives Improvement
- Once hard gates clear, Critic runs SoftGate
- Composite score + per-dimension scores + notes
- Revision Agent prioritizes lowest-scoring dimensions
- Iterative improvement until threshold cleared or diminishing returns

### I3 — Editorial Passes (Developmental → Line → Copy → Proof)
- Each pass is a mini-loop: editor evaluates → Revision Agent applies → editor re-checks
- Developmental: structure, pacing, genre delivery
- Line: sentence rhythm, diction, metaphor density
- Copy: grammar, spelling, timeline, terminology
- Proof: residual typos, formatting, metadata

### I4 — Showrunner Final Approval
- After all gates pass and editorial passes complete
- Showrunner reviews final artifact, signs off
- Story status → FINAL

---

## Phase J: Human Interface & Release 🟢 ON DECK

The outer shell — how a human seeds the system and what comes out.

### J1 — Human Intake Form
- CLI or YAML-based intake: medium, audience, premise, constraints, desired emotions, etc.
- Validates input against contract schemas before injecting into the store

### J2 — Release Package Generation
- Blurb generation from premise + genre + themes
- Metadata packet: BISAC tags, comp titles, audience band, target word count
- Series bible update (if part of a series)

### J3 — Plagiarism / Bias / Legal Check
- Compare generated content against known works
- Flag obvious similarity
- Check for bias markers in character representation, conflict framing

---

## Stretch / Known Design Debt

- [ ] Split `ModalityState` into per-modality enums (`WantingState`, `KnowingState`, `BeingAbleState`, `HavingToState`) — current single enum allows invalid cross-modality states
- [ ] Implement Propp function sequence validation (32-function morphology with transition rules)
- [ ] Implement GOLEM event model (goal → action → outcome → event → perception → internal element)
- [ ] Implement Todorov equilibrium macro-arc validation
- [ ] Add missing unit tests for `loader.py`, `config.py`, `orchestrator.py`
- [ ] Fix ContractStore singleton being test-hostile — state leaks without `reset_store()`
- [ ] Make `ModalityState` enum split backward-compatible with existing contract YAML files

---

## Quick Reference

| Phase | What | Status |
|:------|:-----|:-------|
| A–E | Foundation: scaffold, models, engine, agents, integration tests | ✅ DONE |
| F | Dynamic Agent System: LLM as role-booted agent, prompts, pre-flight gates | 🔴 NEXT |
| G | Big Picture Architecture: actantial plan, episode goals, revisit triggers | 🟡 NEXT |
| H | Chapter-by-Chapter Writing: scenes, simulation, discourse rendering | 🟡 NEXT |
| I | Revision Loop: critique-driven iteration until gates pass | 🟡 NEXT |
| J | Human Interface & Release: intake form, release package, legal check | 🟢 ON DECK |
