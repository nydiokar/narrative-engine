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
| 1 | **Hard Gate receives `events=[]`** | `src/agents/critic.py:47` — `gate.evaluate(scenes=scenes_data, events=[])` | Checks 1,2,3,5,7,8 never validate — only 4 checks (stakes, conflict, Propp, Todorov) actually run |
| 2 | **Worldbuilder registered, never dispatched** | `src/pipeline/orchestrator.py:53` vs `src/agents/director.py` — no workflow step calls `worldbuilder` | Dead registration — LLM capacity allocated but never used. World researcher handles world creation instead |
| 3 | **`src/contracts/loader.py` — YAML loader** | Never imported by any active pipeline code | Dead code — YAML contract loading is wired but called by nothing |
| 4 | **`agents/*.md` (20 files, top-level)** | Root `agents/` directory | Orphaned copies — active prompts live in `src/agents/prompts/*.md` |
| 5 | **3 episodes hardcoded** | `src/agents/outline_planner.py` | Episode count not configurable through CLI or contract |
| 6 | **ContractStore singleton** | `src/agents/store.py:478-491` — `_store` module global | Leaks state across parallel test runs — safe in serial only |
| 7 | **Revision loop FAIL SILENTLY** | `src/pipeline/checkpoints.py:187-189` — `else: pass` | After 3 failed revision attempts, pipeline continues instead of raising |
| 8 | **MockLLMProvider brittle matching** | `src/agents/llm.py` — string-based trigger→response matching | Tests break easily when prompt text changes |
