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

## Phase H — Tree-Based Narrative Workbench ✅ (Done)

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
| **Diff** | View two children field-by-field | `diff(node_a, node_b)` |
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
- [x] `--parallel` flag for concurrent variant execution via `ThreadPoolExecutor`

#### Step 3 — Compare + Promote + Diff ✅
- [x] `compare(nodes)` — side-by-side Rich table: genre, world axes, protagonist, antagonist, soft gate score
- [x] `compare --detail` — expanded panels with world dimensions, protagonist roles per variant
- [x] `diff(node_a, node_b)` — contract-level field-by-field differences via Rich tables
- [x] `promote(node)` — mark child as active path, continue branching from there
- [x] `prune(node)` — delete a branch subtree

#### Step 4 — Interactive CLI ✅
- [x] Canonical CLI (`python -m src`) with all subcommands: `branch`, `compare`, `diff`, `promote`, `prune`, `show`, `set`, `lock`, `unlock`
- [x] `show` — ASCII tree visualization with depth, label, active status
- [x] `--tree-load` / `--tree-save` for persistence

### Example Session

```
# Run pipeline, save state
$ python -m src run --to premise --save trunk.json

# Branch 3 genres from the same premise
$ python -m src branch --vary genre --values fantasy,scifi,horror --tree-load trunk.json --tree-save tree.json

# Compare them side-by-side
$ python -m src compare --labels fantasy,scifi,horror --tree-load tree.json

# Diff two specific branches
$ python -m src diff fantasy horror --tree-load tree.json

# Promote the best branch and continue
$ python -m src promote fantasy --tree-load tree.json --tree-save tree.json
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

## Phase J — Real-LLM Battle Testing & End-to-End Output ✅ (Done)

**Goal**: Prove the pipeline produces coherent narrative output on a real LLM. Run from premise through all 18 agents, 8 workflows, two gates. Fix real-LLM fragility in prompt templates, parse resilience, timeout handling, and revision loop.

### Must-Have

- [x] **Real-LLM end-to-end run**: `python -m src run --to final --provider opencode` produces a draft from premise through all 18 agents, 8 workflows, two gates (tested with llama3.2 @ localhost:11434 + OpenCode big-pickle)
- [x] **Structured output enforcement**: All 18 agents call `BaseAgent._call_llm_for_step()` with `parse_json_output()` — handles markdown fences, extra text, incomplete fields, and field-level remapping (`_normalize_scene` for scene-specific, generic fallback chain in base)
- [x] **Timeout + retry layer**: `_call_llm_for_step` retries 3× with exponential backoff (`base.py:124–198`); `SubprocessLLMProvider` has configurable 300s timeout (`LLM_SUBPROCESS_TIMEOUT` env var); scene writer has independent retry loop for episode rendering (`scene_writer.py:241–264`); all failures gracefully fall back to error dict
- [ ] **Output quality baseline**: Moved to Phase K (Power Move #3)

### Nice-to-Have

- [x] **Parallel tree execution with real LLM**: `--parallel` with `--provider opencode` — `ThreadPoolExecutor` in `executor.py:296–297`, CLI `--parallel` + `--max-workers` flags wired in, confirmed working with real LLM
- [ ] **Draft output formats**: epub, markdown, plain text — only book `output/draft.md` exists; screenplay/script/teleplay assemblers are stubs
- [ ] **Regression test suite**: snapshot-based tests for each agent's LLM output parsing

---

## Phase K — Output Quality & Medium Completeness (Next)

**Goal**: Deliver the first complete, readable narrative output across all 4 mediums. Close the gap between "pipeline runs with real LLM" and "a writer can read the result."

### Next Power Moves

1. **Ship non-book medium assemblers** — ✅ Done. `_assemble_script`, `_assemble_screenplay`, `_assemble_teleplay` now read scenes from store and write `output/script.md`, `output/screenplay.md`, `output/teleplay.md` respectively with medium-appropriate headers.

2. **Wire the discourse contract** — `DiscourseContract` is defined (`models.py:723`), registered in store, listed as WF05 output type — but no agent ever calls `write_contract("discourse", ...)`. The `story.discourse_contract_id` field (`models.py:477`) is always `None`. This is the bridge between "pipeline runs" and "story reads the way the author intends" (POV, tense, voice, exposition strategy).

3. **Establish quality baseline + regression suite** — Run 3 genres full pipeline with real LLM, capture soft gate scores as a repeatable baseline. Build snapshot-based regression tests for each agent's LLM output parsing so future changes cannot silently break output structure.

### Known Risks

- Non-book assemblers require knowledge of screenplay/script/teleplay formatting conventions
- Discourse contract wiring requires updating scene writer prompts to consume discourse settings
- Quality baseline is gated on having a real LLM available (big-pickle or qwen3-coder)

---

## Downstream (future)

| Area | What |
|:-----|:------|
| Quality & Iteration | Revisit triggers, showrunner final approval, editorial pass depth tuning, prose quality improvements |
| Infrastructure | Test coverage (25 modules gap), CI pipeline, release packaging |
| Human Interface | Intake form, legal/bias check, writer dashboard |

---

## Known Design Debt

### Fixed This Session
- Modality field name mismatch: coherence checks used `mc.get("actant"/"from"/"to")` but `ModalityChange` Pydantic model uses `actant_id`/`from_state`/`to_state` — 6 checks now fire on real GOLEM data
- Hard Gate received `events=[]` at runtime — critic now extracts world_rules, builds character ID map, passes scene+GOLEM events with actant metadata
- `_find_root_seed()` dead-code while loop in executor.py — now actually walks up the tree
- `--set` flag timing in `cmd_branch()` — applied after root snapshot, silently ignored; now applied before capture

### Remaining

- ContractStore singleton leaks state across tests — safe in serial, unsafe in parallel
- 25 Python modules lack dedicated unit tests
- Rich inline scene rendering not tested in editorial pipeline
- `src/contracts/loader.py` — dead code, deleted
