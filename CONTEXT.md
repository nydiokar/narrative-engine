# Narrative Engine — Project Context

**Branch:** `main` | **Last Updated:** 2026-05-31 | **Status:** Phase A (types integration) complete. Phase B (Python scaffold) next.

---

## Active Work

| ID | Task | Priority |
|:--:|:-----|:--------:|
| INT-1 | ✅ **[TYPES-INTEGRATION]** types_maps.md integrated — 9 new research files, 6 updated, 4 contracts extended with concrete enums | 🟢 DONE |
| INT-2 | **[ARCHITECTURE-PHASE-1]** Build Python project scaffold (`pyproject.toml`, Pydantic models from YAML contracts, YAML loaders, logging, config) | 🔴 NOW |
| INT-3 | **[ARCHITECTURE-PHASE-2]** Implement core Greimas Fabula Coherence Engine — 8 diagnostic checks, 5-question scene diagnostic, action/state validation | 🟡 |
| INT-4 | **[ARCHITECTURE-PHASE-3]** Implement agent modules — Showrunner orchestration loop, contract read/write for each agent, LLM call stubs | 🟡 |
| INT-5 | **[ARCHITECTURE-PHASE-4]** Implement two-gate evaluation system (hard gate + soft gate), editorial pass pipeline, cliché detection | ⚪ |
| INT-6 | **[ARCHITECTURE-PHASE-5]** Integration test: generate a complete story from seed to final draft through the full pipeline | ⚪ |
| INT-7 | **[PIPELINE-IMPLEMENTATION]** Convert 8 workflow specs (00-07) into executable Python pipeline | ⚪ |

---

## Pending (carry-over)

| Status | Task | Notes |
|:------:|:-----|:------|
| ⚪ | **[TYPES-EXTRA]** Additional type maps from user (if any beyond types_maps.md) | Wait for user |
| ⚪ | **Stories/_template update** | Must match new contract YAML schemas after types integration |
| ⚪ | **Release package generation** | Blurb, metadata, BISAC tags, series bible update — workflow described but not implemented |
| ⚪ | **Plagiarism/bias/legal check module** | Referenced in evaluation rubric but no agent/contract exists |

---

## Recent Activity

### May 31, 2026 — Scaffold Completed + Greimas Overhaul + Full Ontology Integration ✅

**Status:** Specification phase complete. Ready for implementation.

The narrative-engine repository was scaffolded from scratch in this session:

| Phase | Description | Files |
|:------|:------------|:------|
| **Scaffold** | Initial directory tree (13 dirs, 50 files) with placeholder content | README, ROADMAP, docs/, research/, core/, contracts/, agents/, workflows/, templates/, stories/ |
| **Greimas Upgrade** | Replaced placeholder Greimas content with full formulation: value-states (not physical items), canonical narrative schema (Manipulation → Competence → Performance → Sanction), action/state distinction (действие/състояние), 5-question scene diagnostic, 8 Fabula Coherence Engine checks | `core/greimas/*` (3 files), `core/story-logic/*` (2 files), `docs/theory-notes.md` |
| **Ontology Expansion** | Integrated complete research from conceptual document: 10 new research files (theme ontology/LTO, BISAC genre taxonomy, character layers/FFM/Schwartz/RMT/attachment, motivation stack/SDT/Reiss, emotion/Plutchik, 7 conflict types, worldbuilding dimensions, evaluation rubric/hard+soft gate, cliché definition, discourse layer) | `research/*` (10 new), `contracts/*` (4 new: theme, conflict, discourse, chapter), `agents/*` (12 new) |
| **Professional Role Stack** | Replaced simple agent list with full production pipeline: Showrunner → Script Editor → Theme Specialist → Structuralist → Character Simulator → Dialogue Specialist → World Researcher → Outline/Chapter Planners → Continuity Editor → Critic → Editorial Editors (developmental/line/copy/proof) → Revision Agent | `agents/*` (12 new, 8 updated) |
| **Workflow Restructure** | Re-aligned 8 workflows (00-07) to the operating sequence from the research: brief/taxonomy → seed → structure → episodes → scenes → draft → editorial passes → critique/revision | `workflows/*` (8 files, 6 superseded originals removed) |
| **User types_maps.md received** | 1130-line type map received at end of session (premise types, scene types, sequence types, stakes, endings, character taxonomies, conflict operations, world types, theme families, tone/style/voice maps, relationship archetypes, symbolism, selection logic, cliché/freshness, integrated Greimas+Propp contracts, full agent role definitions, LLM pipeline spec, story quality definition, master prompt structure) | `types_maps.md` (in repo root, not yet integrated) |

### May 31, 2026 — Phase A: types_maps.md Integrated ✅

**9 new research files:** `premise-types.md`, `scene-types.md`, `sequence-types.md`, `stakes-types.md`, `ending-types.md`, `tone-style-maps.md`, `relationship-archetypes.md`, `symbolism-motifs.md`, `story-definition.md`

**6 updated research files:** `character-layers.md` (dramatic roles, Jungian, Enneagram), `motivation-stack.md` (desires, fears, wounds, needs), `conflict-types.md` (classical types, operations, quality levels), `worldbuilding-dimensions.md` (world types, spectrums, functions), `theme-ontology.md` (theme families, moral questions, expression channels), `genre-taxonomy.md` (genre promises, selection logic), `selection-logic.md` (matrix compatibility, rejection rules), `cliche-definition.md` (signals, generators, formula), `story-components.md` (plot structure systems)

**4 contracts extended:** `story-contract.yaml` (premise_type, ending_type), `scene-contract.yaml` (scene_type), `episode-contract.yaml` (sequence_type, stakes_type), `conflict-contract.yaml` (classical_type, operations, quality_level)

**Pending for Phase B:** Python project scaffold

**Key decisions:**
- Greimas sits above Propp in the pipeline: Greimas defines *why* (structural necessity); Propp defines *how* (functional morphology).
- Characters are layered: function (Propp/Greimas) + personality (FFM) + values (Schwartz) + social mode (RMT) + attachment + motivation (SDT+Reiss) + emotion (Plutchik).
- Evaluation is two-gate: hard gate (structural soundness) rejects; soft gate (novelty, genre fit, thematic clarity) ranks.
- Cliché = high-frequency genre defaults without inversion, escalation, recombination, or thematic necessity.
- The system simulates a professional publishing production line, not "one writer agent."

---

## Architecture Decisions

### Pipeline Order
```
00 Brief/Taxonomy → 01 Seed/Premise → 02 Structure → 03 Episodes → 04 Scenes → 05 Draft → 06 Editorial → 07 Critique
```

### Greimas/Propp Integration
```
Greimas layer defines structural necessity (actants, value-objects, canonical schema).
Propp layer provides one possible functional morphology (sequence of 32 functions).
A Propp function is only valid if it serves an active Greimasian narrative program.
```

### Actor/Actant Separation
```
A character is a psychological construct (personality, values, motivation, emotion, attachment).
An actant is a structural position (Subject, Object, Sender, Receiver, Helper, Opponent).
One character can shift actantial positions across narrative programs.
One actant can be distributed across multiple characters, institutions, objects, or internal forces.
```

### Contract-Driven Data Flow
```
All agents communicate through typed YAML contracts.
Contracts are the source of truth — not agent memory.
New contracts added: theme, conflict, discourse, chapter.
```

---

## Quick Reference

### Key Locations

| Area | Path | Notes |
|:-----|:-----|:------|
| Core models | `core/greimas/`, `core/propp/`, `core/story-logic/` | Structural narratology |
| Contracts | `contracts/*.yaml` | 10 YAML schemas for all data flow |
| Agents | `agents/*.md` | 20 role cards with responsibilities |
| Workflows | `workflows/*.md` | 8 pipeline stages |
| Research | `research/*.md` | 15 domain research files |
| Docs | `docs/` | System overview, theory notes, glossary |
| Templates | `templates/` | 6 YAML templates |
| Types (pending) | `../types_maps.md` | 1130-line user type map (not yet integrated) |

### Repository Growth

| Metric | Value |
|:-------|:------|
| Total files | 81 |
| Research files | 15 |
| Agent role cards | 20 |
| Contract schemas | 10 |
| Workflow stages | 8 |
| Template files | 6 |
| Core model files | 8 |

---

## Usage Guide

**When to update:**
- After completing tasks → add to Recent Activity
- Starting new work → add to Active Work
- Architectural decisions → add to Architecture Decisions

**Priority levels:**
- 🔴 NOW — blocking, work on this first
- 🟡 NEXT — queued after current work
- ⚪ ON_DECK — available but not urgent

**Scope labels for entries:**
- S = Small (<50 lines, <1hr, single file)
- M = Medium (2-5 files, <4hrs, cross-file change)
- L = Large (5+ files, multi-day, new subsystem)
