# Pipeline Map — Narrative Engine

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NARRATIVE ENGINE PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WF 00: BRIEF & TAXONOMY                      ┌── Prompt: theme_specialist  │
│  ────────────────────────                      │── Prompt: world_researcher │
│  theme_specialist: select_themes               │── Prompt: character_arch   │
│  theme_specialist: select_genre                │── Prompt: showrunner       │
│  world_researcher: set_world_axes              │   (LLM role-play, not      │
│  character_architect: prepare_layers           │    raw API calls)          │
│  showrunner: approve_brief ──→ [StoryContract] │                            │
│                                                                             │
│  WF 01: SEED → PREMISE                                                    │
│  ──────────────────────                                                    │
│  showrunner: review_brief                     ┌── "The Crystal Key" seed   │
│  structuralist: analyze_premise               │── Premise type detected    │
│  structuralist: select_backbone               │── Actantial model: Subject │
│  character_architect: draft_protagonists      │   Object, Sender, Receiver │
│  showrunner: approve_premise ──→ [CharacterContract + StoryContract]       │
│                                                                             │
│  WF 02: PREMISE → STRUCTURE                                                │
│  ──────────────────────────                                                │
│  structuralist: build_fabula                   ┌── Fabula coherence checks │
│  structuralist: check_constraints              │── World rules established │
│  theme_specialist: validate_thematic_fit       │── Narrative programs set  │
│  showrunner: approve_structure ──→ [WorldContract + FabulaChain]           │
│                                                                             │
│  WF 03: STRUCTURE → EPISODES                                              │
│  ──────────────────────────                                                │
│  outline_planner: segment_fabula              ┌── 3 episodes by default    │
│  chapter_planner: divide_episodes             │── Each episode: sequence   │
│  character_architect: refine_arcs             │   type, stakes, phase      │
│  world_researcher: assign_settings            │── Propp functions assigned │
│  showrunner: approve_episodes ──→ [EpisodeContract + ChapterContract]     │
│                                                                             │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║          MEDIUM-SPECIFIC RENDERING (WF 04–06)                       ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║  BOOK    │  ANIM   │  MOVIE   │  SERIES  │  GAME*  │  DRAMA*       ║   │
│  ║──────────┼─────────┼──────────┼──────────┼─────────┼───────────────║   │
│  ║ render_  │ render_ │ render_  │ render_  │  (same  │  (same as     ║   │
│  ║ prose    │ visual  │ cinematic│ television│ as anim)│  animation)   ║   │
│  ║ finalize_│ finalize│ finalize │ finalize │         │               ║   │
│  ║ prose    │ _script │ _screen  │ _teleplay│         │               ║   │
│  ║ editorial │ script │ script   │ script   │         │               ║   │
│  ║ (prose)  │ edit    │ edit     │ edit     │         │               ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                             │
│  WF 04: EPISODES → SCENES                                                 │
│  ──────────────────────────                                                │
│  character_simulator: enact_episode           ┌── Prompt: character_sim    │
│  dialogue_specialist: plan_speech_acts         │── Prompt: dialogue        │
│  scene_writer: render_{medium}_scene           │── Prompt: scene_writer    │
│  scene_writer: run_greimas_diagnostic          │── Greimas diagnostic per  │
│  continuity_editor: check_consistency          │   scene (action/state)    │
│                    ──→ [SceneContract + ConflictLoad + GreimasDiag]        │
│                                                                             │
│  WF 05: SCENES → DRAFT                                                    │
│  ──────────────────────                                                    │
│  scene_writer: finalize_{medium}              ┌── Discourse contract: POV │
│  continuity_editor: final_check               │   tense, focalisation,    │
│  showrunner: assemble_draft                   │   voice register...       │
│                    ──→ [DiscourseContract + Draft]                         │
│                                                                             │
│  WF 06: EDITORIAL PASSES                                                  │
│  ────────────────────────                                                  │
│  developmental_editor → revision_agent         ┌── Structural revisions   │
│  line_editor → revision_agent                  │── Prose refinements      │
│  copy_editor → revision_agent                  │── Copy-level fixes       │
│  proofreader: final_check                      │── Final proof            │
│                                                                             │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║  TWO-GATE EVALUATION + REVISION LOOP                                ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║  WF 07: CRITIQUE & REVISION                                         ║   │
│  ║  ╔══════════════════════════════════════════════════════════════════╗ ║   │
│  ║  ║  HARD GATE — Structural Soundness (10 checks)                  ║ ║   │
│  ║  ║  1. Causal Soundness         6. Conflict Active                ║ ║   │
│  ║  ║  2. Character Intentionality 7. Continuity                     ║ ║   │
│  ║  ║  3. World Rule Consistency   8. Event Necessity                ║ ║   │
│  ║  ║  4. Stakes Presence          9. Propp Sequence                 ║ ║   │
│  ║  ║  5. Contradiction Free      10. Todorov Equilibrium            ║ ║   │
│  ║  ╚══════════════════════════════════════════════════════════════════╝ ║   │
│  ║                               │                                       ║   │
│  ║                          ┌────┴────┐                                  ║   │
│  ║                     FAIL │         │ PASS                              ║   │
│  ║                     ┌────┘         └────┐                              ║   │
│  ║                     ▼                    ▼                              ║   │
│  ║           Revision Loop          SOFT GATE — Quality Scoring           ║   │
│  ║           ┌──────────┐           ╔═══════════════════════════════╗      ║   │
│  ║           │ attempt 1│           ║ 9 Dimensions (0-10 each):    ║      ║   │
│  ║           │ (targeted│           ║ genre_fit, novel,            ║      ║   │
│  ║           │  edit)   │           ║ thematic_clarity,            ║      ║   │
│  ║           ├──────────┤           ║ conflict_density,            ║      ║   │
│  ║           │ attempt 2│           ║ relationship_tension,        ║      ║   │
│  ║           │ (targeted│           ║ suspense_curiosity_surprise, ║      ║   │
│  ║           │  edit)   │           ║ emotional_transport,         ║      ║   │
│  ║           ├──────────┤           ║ scene_level_purpose,         ║      ║   │
│  ║           │ attempt 3│           ║ prose_distinctiveness,       ║      ║   │
│  ║           │ (full re-│           ║ (weighted composite)         ║      ║   │
│  ║           │  generate│           ╚═══════════════════════════════╝      ║   │
│  ║           │  scenes) │                    │                            ║   │
│  ║           └──────────┘              ┌─────┴─────┐                      ║   │
│  ║            still fail →        BELOW│         │ABOVE                  ║   │
│  ║            FAIL SILENTLY      ┌────┘          └────┐                  ║   │
│  ║                               ▼                    ▼                  ║   │
│  ║                        needs_revision             PASS                ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                             │
│                      TREE BRANCHING SYSTEM                                  │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  branch --vary genre --values fantasy,scifi                        │     │
│  │  ┌──── root (premise seed) ────┐                                  │     │
│  │  │   checkpoint=""             │                                  │     │
│  │  │   store=story+theme+chars   │                                  │     │
│  │  └────────┬─────────┬─────────┘                                  │     │
│  │           │         │                                            │     │
│  │      fantasy    scifi    horror  ← children, each has full       │     │
│  │           │         │           │   store snapshot               │     │
│  │      promote → active path      │   can branch deeper             │     │
│  │      compare → side-by-side     │   (vary world, character, etc) │     │
│  │      prune   → delete subtree   │                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quirks & Known Gaps

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | **`src/contracts/loader.py` — YAML loader** | Never imported by any active pipeline code | Dead code — YAML contract loading is wired but called by nothing |
| 2 | **`agents/*.md` (20 files, top-level)** | Root `agents/` directory | Orphaned copies — active prompts live in `src/agents/prompts/*.md` |
| 3 | **Episode count hardcoded in fallback** | `src/agents/outline_planner.py` — `_fallback_episodes()` | 4 episodes with fixed Greimas phase mapping. Not configurable through CLI or contract |
| 4 | **Revision loop raises after max retries** | `src/pipeline/checkpoints.py:187-189` | Raises RuntimeError after 3 failed revision attempts. Previously silent |
| 5 | **MockLLMProvider brittle matching** | `src/agents/llm.py` — string-based trigger→response matching | Tests break easily when prompt text changes |
| 6 | **Book editorial has 7 steps, script mediums 5** | `src/agents/director.py` lines 83-91 vs 111-117 | Scripts lack line/copy/proofreading passes |
| 7 | **`_ALL_WORKFLOW_IDS` is hardcoded copy** | `src/agents/director.py:185-188` | Adding a workflow to a registry dict without updating this list silently skips it in full pipeline |
