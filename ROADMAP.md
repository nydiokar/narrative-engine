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

CHAPTER-BY-CHAPTER (WF 04–05)
  Per-chapter scenes, emotional arcs, discourse rendering —
  the local execution. Informed by Big Picture.

REVISIT (WF 06–07)
  Editorial passes and critique. Loops until gates pass.
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

## Phase G ✅ (Done)

- [x] 12 new prompt templates written (Character Simulator, Dialogue Specialist, World Researcher, Worldbuilder, Chapter Planner, Continuity Editor, Developmental Editor, Line Editor, Copy Editor, Proofreader, Revision Agent, Theme Specialist)
- [x] All 19 workflow-active agents now call the LLM through their prompt
- [x] Scene Writer prompt enhanced: minimum 100 words of real content per scene
- [x] ContractStore.save(path) / ContractStore.load(path) — full JSON serialization
- [x] demo.py --save <path> / --load <path> flags
- [x] 151 / 151 tests passing

---

## Phase H — Tree-Based Narrative Workbench (In Progress)

**Core insight**: The current pipeline is a **ladder** — climb from 00 to 07, one path. A writer needs a **tree** — branch at any node, compare siblings, freeze what works, keep branching.

### Concepts

| Term | Meaning | In Code |
|------|---------|---------|
| **Parent** | A frozen state you branch from | A `ContractStore` snapshot + metadata |
| **Sibling** | Variants at the same depth | Children of the same parent |
| **Child** | A sibling's downstream expansion | A node deeper in the tree |
| **Branch** | Fork a parent into N variants | `branch(node, vary=..., values=...)` |
| **Promote** | Make a child the active path | `promote(node)` |
| **Compare** | View siblings side-by-side | `compare(nodes)` |
| **Prune** | Delete unwanted branches | `prune(node)` |

### Pipeline Stages as Branch Points

| Depth | What You Vary | Pipeline Stage |
|-------|--------------|----------------|
| 0 | **Genre, theme, tone** | WF 00–01 (brief + premise) |
| 1 | **World architecture** | WF 02 (structure) |
| 2 | **Heroes, villains, conflicts** | WF 03 (episodes) |
| 3 | **Scene sequences** | WF 04 (scenes) |
| 4 | **Draft style** | WF 05–07 (draft + editorial) |

### Implementation Steps

#### Step 1 — Tree Node + Store Snapshot ✅
- [x] `src/tree/node.py` — `TreeNode` dataclass (id, parent_id, variant_params, store_snapshot, scores, children)
- [x] `ContractStore.snapshot()/restore()` — freeze/restore full store state
- [x] `ContractStore` variant_id namespace — siblings don't overwrite

#### Step 2 — Branch Executor ✅
- [x] `src/tree/executor.py` — `branch()` takes a node + vary config, runs N pipeline instances
- [x] Each variant clones the parent store, varies the specified parameter, runs from branch point
- [x] Returns N child nodes with their own stores

#### Step 3 — Compare + Promote
- [ ] `compare(nodes)` — side-by-side table: genre, world axes, protagonist, antagonist, soft gate score
- [ ] `promote(node)` — mark child as active path, continue branching from there
- [ ] `prune(node)` — delete a branch subtree

#### Step 4 — Interactive CLI
- [ ] `demo.py --branch` mode — interactive branching commands
- [ ] `demo.py --tree <path>` — load/save entire tree structure
- [ ] Tree visualization (ASCII or simple text)

#### Step 5 — LLM Parameter Variance
- [ ] Expose `seed`, `top_p`, `top_k`, `frequency_penalty`, `presence_penalty` in `LLMProvider.generate()`
- [ ] Per-call parameter override from variant config
- [ ] `--vary temperature` flag for creative variance

### Example Session

```
# Start with a premise
$ python scripts/demo.py --to premise --save trunk.json

# Branch 3 genres from the same premise
$ python scripts/demo.py --branch --from premise \
    --vary genre --values "fantasy,scifi,horror"

# Compare them side-by-side
$ python scripts/demo.py --compare

# Branch world architectures from the best genre
$ python scripts/demo.py --branch --node fantasy \
    --vary world --values 3

# Promote the best branch and continue to scenes
$ python scripts/demo.py --promote world-2 --to scenes
```

---

---

## Phase I — Editorial & Revision Real-LLM Wiring ✅ (Done)

- [x] Fix silent-success bug in `BaseAgent._call_llm_for_step` — LLM parse failure returns `success: False` with error message
- [x] All agent `result.get("success", True)` defaults changed to `False` for pure-LLM relay agents
- [x] Soft Gate calls real LLM for `dimension_scores` + `dimension_notes`; falls back to mid-range (5) neutral scores
- [x] Cliché detection calls real LLM for `cliche_signals` array; falls back to empty signals
- [x] Revision Agent applies real contract modifications via `_apply_changes_from_result()` (parses `type`/`contract_id`/`field`/`new_value` from LLM output)
- [x] Revision loop in checkpoints.py: targeted editorial passes (06 + 07) for N-1 attempts; full scene regeneration only on last attempt
- [x] MockLLMProvider: valid JSON default fallback, `agent.step` trigger matching by separate `Agent:` / `step:` lines
- [x] `critic.md` prompt specifies structured output for `dimension_scores`, `dimension_notes`, `cliche_signals`
- [x] Adversarial review: non-numeric severity/dimension score crash fixed, `setattr` field existence guard added
- [x] All 209 tests passing, demo pipeline end-to-end

---

## Downstream (future)

| Area | What |
|:-----|:------|
| Quality & Iteration | Revisit triggers, showrunner final approval, editorial pass depth tuning |
| Infrastructure | ModalityState split, Propp/Todorov/GOLEM models, save/load, CLI, test coverage |
| Human Interface | Intake form, release package, legal/bias check |
| LLM Parameters | Expose `seed`, `top_p`, `top_k`, `frequency_penalty`, `presence_penalty` for creative variance |

---

## Known Design Debt

- ModalityState single enum allows invalid cross-modality states — split into per-modality enums deferred
- Propp function sequence validation and Todorov equilibrium validation stubbed but not implemented
- ContractStore singleton leaks state across tests — safe in serial, unsafe in parallel
- GOLEM event model (goal→action→outcome→event→perception→internal element) referenced in specs, not coded
- 25 Python modules lack dedicated unit tests
