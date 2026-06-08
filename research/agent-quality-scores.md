# Agent Quality Scores — Registry v1

Scored 2026-06-09 against the [Quality Audit Framework](research/quality-audit-framework.md) (14 dimensions, 1-5).

## Overall Rankings

| Rank | Agent | Avg | Role | Std | Bnd | Sch | Ctx | Prq | Fal | Nrm | Map | Err | Fid | Hnd | Cns | Unq |
|------|-------|-----|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 1 | character_architect | 4.3 | 5 | 5 | 2 | 5 | 3 | 4 | 5 | 5 | 5 | 4 | 4 | 4 | 5 |
| 2 | theme_specialist | 4.3 | 5 | 5 | 3 | 5 | 3 | 3 | 4 | 5 | 5 | 4 | 5 | 4 | 5 |
| 3 | scene_writer | 4.2 | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | 5 | 3 | 5 | 4 | 4 |
| 4 | critic | 4.0 | 4 | 5 | 3 | 4 | 4 | 4 | 4 | 5 | 4 | 3 | 5 | 4 | 4 |
| 5 | structuralist | 3.9 | 5 | 4 | 2 | 5 | 3 | 4 | 3 | 4 | 5 | 3 | 4 | 4 | 5 |
| 6 | outline_planner | 3.8 | 4 | 4 | 2 | 4 | 3 | 4 | 4 | 5 | 5 | 3 | 4 | 4 | 4 |
| 7 | showrunner | 3.6 | 4 | 3 | 2 | 4 | 4 | 5 | 3 | 2 | 5 | 3 | 4 | 4 | 4 |
| 8 | world_researcher | 3.6 | 5 | 4 | 2 | 4 | 3 | 4 | 3 | 3 | 5 | 3 | 4 | 4 | 4 |
| 9 | continuity_editor | 3.4 | 4 | 4 | 2 | 3 | 4 | 4 | 3 | 2 | 4 | 3 | 4 | 3 | 4 |
| 10 | revision_agent | 3.2 | 3 | 3 | 3 | 4 | 3 | 2 | 3 | 3 | 4 | 3 | 4 | 4 | 3 |
| 11 | dialogue_specialist | 2.9 | 4 | 4 | 2 | 3 | 3 | 3 | 2 | 2 | 4 | 2 | 3 | 3 | 4 |
| 12 | character_simulator | 2.9 | 4 | 3 | 2 | 4 | 3 | 3 | 2 | 2 | 5 | 2 | 3 | 3 | 4 |
| 13 | script_editor | 2.9 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| 14 | chapter_planner | 2.8 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 2 | 5 | 3 | 2 | 4 | 2 |
| 15 | line_editor | 2.8 | 3 | 3 | 3 | 2 | 3 | 3 | 2 | 2 | 4 | 2 | 3 | 3 | 3 |
| 16 | developmental_editor | 2.8 | 4 | 4 | 2 | 3 | 3 | 3 | 1 | 2 | 5 | 2 | 2 | 3 | 2 |
| 17 | proofreader | 2.6 | 3 | 3 | 2 | 2 | 3 | 3 | 2 | 2 | 4 | 2 | 3 | 3 | 3 |
| 18 | copy_editor | 2.3 | 3 | 3 | 2 | 2 | 3 | 3 | 1 | 2 | 2 | 2 | 2 | 2 | 3 |

**Dimension keys:** Role=RoleIdentity, Std=Standards, Bnd=Boundaries, Sch=SchemaAlignment, Ctx=ContextUtilization, Prq=PrerequisiteGate, Fal=FallbackRobustness, Nrm=Normalization, Map=MappingAccuracy, Err=ErrorMessaging, Fid=Fidelity, Hnd=Handoff, Cns=ConstraintPropagation, Unq=UniqueValue

## Per-Dimension Averages

| Dimension | Avg | Strongest | Weakest |
|-----------|-----|-----------|---------|
| Role Identity | 3.8 | character_architect, structuralist, world_researcher (5) | copy_editor, chapter_planner, line_editor, proofreader (3) |
| Standards | 3.6 | character_architect, theme_specialist, critic (5) | showrunner, chapter_planner, script_editor, line_editor, proofreader, copy_editor (3) |
| Boundaries | 2.3 | scene_writer (5) | 14 agents scored 2 |
| Schema Alignment | 3.4 | character_architect, theme_specialist, structuralist (5) | proofreader, line_editor, copy_editor (2) |
| Context Utilization | 3.2 | showrunner, continuity_editor (4) | 12 agents scored 3 (generic `_gather_upstream_yaml` only) |
| Prerequisite Gate | 3.3 | showrunner (5) | revision_agent (2 — missing gate) |
| Fallback Robustness | 2.9 | character_architect (5) | copy_editor, developmental_editor (1) |
| Normalization | 3.1 | character_architect, theme_specialist, scene_writer, critic, outline_planner (5) | showrunner, continuity_editor, chapter_planner, character_simulator, proofreader, line_editor, developmental_editor, copy_editor, dialogue_specialist (2) |
| Mapping Accuracy | 4.3 | 12 agents scored 5 | copy_editor (2 — `contracts_data` bug) |
| Error Messaging | 2.8 | character_architect, theme_specialist (4) | character_simulator, line_editor, proofreader, developmental_editor, copy_editor, dialogue_specialist (2) |
| Fidelity | 3.4 | theme_specialist, scene_writer, critic (5) | copy_editor, developmental_editor (2) |
| Handoff | 3.4 | character_architect, theme_specialist, structuralist, outline_planner, showrunner, critic (4) | copy_editor (2) |
| Constraint Propagation | 3.2 | character_architect (4) | character_simulator, copy_editor (1) |
| Unique Value | 3.6 | character_architect, theme_specialist, structuralist (5) | chapter_planner, developmental_editor (2) |

## Registry — Per-Agent Detail

### 1. character_architect — 4.3 (overall)
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 5 | Distinctive architect voice, professional lineage signaled |
| Standards | 5 | FFM 1-10, valid Plutchik emotions, attachment patterns, Schwartz values |
| Boundaries | 2 | No "don't do this" section in prompt |
| Schema Alignment | 5 | All contract fields requested; output spec matches CharacterContract |
| Context Utilization | 3 | Upstream contracts injected but not referenced structurally in instructions |
| Prerequisite Gate | 4 | Checks for story; step-varied |
| Fallback Robustness | 5 | Multi-path extraction, sensible defaults for every field |
| Normalization | 5 | Best in codebase — catches construction exceptions, range constraints |
| Mapping Accuracy | 5 | All template vars provided |
| Error Messaging | 4 | Logs warnings, catches failures per field |
| Fidelity | 4 | Implements prompt faithfully; prompt requests programmatic checks Python doesn't do |
| Handoff | 4 | Writes character, links to story as subject_id |
| Constraint Propagation | 4 | FFM ranges, Plutchik validity enforced |
| Unique Value | 5 | Only agent that creates character contracts with full personality profiles |

### 2. theme_specialist — 4.3
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 5 | Clear ontology specialist voice |
| Standards | 5 | Question must end with ?, moral tensions need ≥2 values |
| Boundaries | 3 | Some negatives in prompt ("not a noun") |
| Schema Alignment | 5 | ThemeContract + GenreSelection fully specified |
| Context Utilization | 3 | Generic upstream injection |
| Prerequisite Gate | 3 | Flat `["story"]` for all steps |
| Fallback Robustness | 4 | Default ThemeContract on LLM failure |
| Normalization | 5 | `_validate_theme_contract` checks prompt-level constraints |
| Mapping Accuracy | 5 | All vars mapped |
| Error Messaging | 4 | Violations logged |
| Fidelity | 5 | Best prompt-to-code fidelity in codebase |
| Handoff | 4 | Writes theme, updates story with genre |
| Constraint Propagation | 4 | Theme quality validated before storage |
| Unique Value | 5 | Only agent for BISAC genre + theme ontology |

### 3. scene_writer — 4.2
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 4 | Clear prose writer voice |
| Standards | 4 | Scene type constraints, POV, tense rules |
| Boundaries | 5 | Best in codebase — explicit "Do NOT include" list, field-name warnings |
| Schema Alignment | 4 | Minor mismatch: prompt lists 7 scene_types, model accepts ~24 |
| Context Utilization | 4 | Medium-specific content format injection |
| Prerequisite Gate | 4 | Checks chapter, story, character, episode |
| Fallback Robustness | 4 | Static default scene on LLM failure |
| Normalization | 5 | Comprehensive remapping of common LLM errors (greimas_tracking→greimas_diagnostic) |
| Mapping Accuracy | 5 | All vars provided |
| Error Messaging | 3 | Standard base class logging |
| Fidelity | 5 | Full prompt implementation |
| Handoff | 4 | Writes scene contracts consumed by editors |
| Constraint Propagation | 4 | Validates content is non-empty, value_object_change is valid |
| Unique Value | 4 | Only prose generator; unique medium branching |

### 4. critic — 4.0
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 4 | Clear evaluator voice |
| Standards | 5 | 11 hard gate checks, 9 soft gate dimensions — most concrete in codebase |
| Boundaries | 3 | Some limits defined |
| Schema Alignment | 4 | Per-step detail, slightly loose on soft gate |
| Context Utilization | 4 | Hard gate findings chained into soft gate context |
| Prerequisite Gate | 4 | Per-step granularity |
| Fallback Robustness | 4 | Defaults all scores to mid-range (5) on LLM failure |
| Normalization | 5 | Catches non-numeric, out-of-range; detects inflation/floor effects |
| Mapping Accuracy | 4 | All vars present |
| Error Messaging | 3 | Standard logging |
| Fidelity | 5 | Prompt says "hard gate is programmatic" → Python implements exactly that |
| Handoff | 4 | Writes CritiqueContract consumed downstream |
| Constraint Propagation | 3 | Evaluates but doesn't enforce fixes |
| Unique Value | 4 | Two-gate system is unique; only agent with cliché detection |

### 5. structuralist — 3.9
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 5 | Strong Greimas + Propp theoretical identity |
| Standards | 4 | No ex nihilo causes, no backward causation |
| Boundaries | 2 | No limits defined |
| Schema Alignment | 5 | Full contract model alignment |
| Context Utilization | 3 | Generic upstream injection |
| Prerequisite Gate | 4 | Step-varied (analyze_premise needs story; build_fabula needs story+character) |
| Fallback Robustness | 3 | Generic fallback |
| Normalization | 4 | `_analyze_premise` validates contract_data, iterates known fields |
| Mapping Accuracy | 5 | All vars mapped |
| Error Messaging | 3 | Standard |
| Fidelity | 4 | `_check_constraints` is pure programmatic — matches prompt |
| Handoff | 4 | Reads story/character, writes episodes |
| Constraint Propagation | 3 | Constraints checked but not auto-fixed |
| Unique Value | 5 | Only agent doing Greimas + Propp analysis |

### 6. outline_planner — 3.8
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 4 | Clear planner voice |
| Standards | 4 | Conflict types, emotion mapping specificity |
| Boundaries | 2 | None |
| Schema Alignment | 4 | Good coverage |
| Context Utilization | 3 | Generic |
| Prerequisite Gate | 4 | Checks story+character |
| Fallback Robustness | 4 | Per-episode + full 4-phase fallback chain |
| Normalization | 5 | None→'' conversion, enum case, conflict, emotion normalization |
| Mapping Accuracy | 5 | All vars provided |
| Error Messaging | 3 | Standard |
| Fidelity | 4 | Prompt instructions implemented |
| Handoff | 4 | Writes 4 episode contracts |
| Constraint Propagation | 3 | Minimal enforcement |
| Unique Value | 4 | Only agent that segments fabula into episodes |

### 7. showrunner — 3.6
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 4 | Clear executive voice |
| Standards | 3 | Generic quality language |
| Boundaries | 2 | None |
| Schema Alignment | 4 | Core fields align |
| Context Utilization | 4 | Multistep context accumulation |
| Prerequisite Gate | 5 | Best-in-class: step-varied (approve_premise→story+character, approve_structure→adds theme) |
| Fallback Robustness | 3 | Generic fallback |
| Normalization | 2 | Most LLM steps pass through result dict with .get() defaults |
| Mapping Accuracy | 5 | All vars provided |
| Error Messaging | 3 | Standard |
| Fidelity | 4 | Uses get_registry to route narrative structure |
| Handoff | 4 | Validates premise before passing forward |
| Constraint Propagation | 3 | Minimal |
| Unique Value | 4 | Only agent that approves/rejects pipeline state |

### 8. world_researcher — 3.6
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 5 | Strong "bible keeper" identity |
| Standards | 4 | Violable rules, falsifiable claims |
| Boundaries | 2 | None |
| Schema Alignment | 4 | Good coverage |
| Context Utilization | 3 | Generic |
| Prerequisite Gate | 4 | Step-varied (assign_settings needs story+episode) |
| Fallback Robustness | 3 | Empty WorldContract as fallback |
| Normalization | 3 | Handles key-name flexibility (axes vs dimensions) |
| Mapping Accuracy | 5 | All vars provided |
| Error Messaging | 3 | Standard |
| Fidelity | 4 | Prompt instructions implemented |
| Handoff | 4 | Writes WorldContract |
| Constraint Propagation | 2 | Prompt says value range 0.0-1.0; Python doesn't enforce |
| Unique Value | 4 | Only agent managing world rules |

### 9. continuity_editor — 3.4
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 4 | Clear consistency guardian voice |
| Standards | 4 | 11 coherence checks specified |
| Boundaries | 2 | None |
| Schema Alignment | 3 | CritiqueContract stores verdict but discards rich LLM analysis |
| Context Utilization | 4 | Hybrid: engine findings injected into LLM context |
| Prerequisite Gate | 4 | Checks scene+episode |
| Fallback Robustness | 3 | Generic |
| Normalization | 2 | Minimal — CritiqueContract written with bare fields |
| Mapping Accuracy | 4 | engine_findings added as new template var |
| Error Messaging | 3 | Standard |
| Fidelity | 4 | Engine-as-gate matches prompt architecture |
| Handoff | 3 | Writes critique but analysis data is discarded |
| Constraint Propagation | 4 | Engine enforces 11 coherence rules |
| Unique Value | 4 | Only agent with programmatic pre-validation feeding LLM |

### 10. revision_agent — 3.2
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 3 | Generic editor voice |
| Standards | 3 | Generic |
| Boundaries | 3 | Some limits |
| Schema Alignment | 4 | Change items well-structured |
| Context Utilization | 3 | Generic |
| Prerequisite Gate | 2 | Missing — no gate override means it runs even without critiques |
| Fallback Robustness | 3 | Generic |
| Normalization | 3 | Validates cid, field, new_value per change item |
| Mapping Accuracy | 4 | All vars present |
| Error Messaging | 3 | Logs per-item failures |
| Fidelity | 4 | Five step methods match prompt's five apply steps |
| Handoff | 4 | Reads contracts, writes updated contracts via setattr |
| Constraint Propagation | 3 | Applies changes but doesn't re-validate |
| Unique Value | 3 | Applies critique feedback programmatically |

### 11. dialogue_specialist — 2.9
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 4 | Speech act theory voice (reveal/conceal/persuade/threaten) |
| Standards | 4 | Subtext, silence-as-speech standards |
| Boundaries | 2 | None |
| Schema Alignment | 3 | Speech acts array loosely defined |
| Context Utilization | 3 | Generic |
| Prerequisite Gate | 3 | Basic gate |
| Fallback Robustness | 2 | No fallback for empty LLM output |
| Normalization | 2 | No field validation on speech_acts array |
| Mapping Accuracy | 4 | Vars present |
| Error Messaging | 2 | Generic |
| Fidelity | 3 | Implements but doesn't enforce speech act constraints |
| Handoff | 3 | Writes scene dialogue |
| Constraint Propagation | 2 | Not leveraging medium despite medium-dependent dialogue |
| Unique Value | 4 | Only agent doing speech act annotation |

### 12. character_simulator — 2.9
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 4 | Clear simulator voice |
| Standards | 3 | Generic |
| Boundaries | 2 | None |
| Schema Alignment | 4 | Good |
| Context Utilization | 3 | Generic |
| Prerequisite Gate | 3 | Basic |
| Fallback Robustness | 2 | Returns success=True with zero simulation data on LLM failure — bug |
| Normalization | 2 | No field validation |
| Mapping Accuracy | 5 | Vars present |
| Error Messaging | 2 | Generic |
| Fidelity | 3 | LLM-dependent; no programmatic arc validation |
| Handoff | 3 | Writes critique |
| Constraint Propagation | 1 | No constraint enforcement |
| Unique Value | 4 | Only agent for per-episode character enactment |

### 13. script_editor — 2.9
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 3 | Generic |
| Standards | 3 | Generic |
| Boundaries | 2 | None |
| Schema Alignment | 3 | Medium format rules exist but Python doesn't branch on medium |
| Context Utilization | 3 | Generic |
| Prerequisite Gate | 3 | Basic |
| Fallback Robustness | 3 | Partial graceful degradation |
| Normalization | 3 | Post-LLM validation: checks content, value_object_change, characters_present |
| Mapping Accuracy | 3 | Medium metadata exists but unused in branching |
| Error Messaging | 3 | Standard |
| Fidelity | 3 | Medium-specific rules in prompt but not in Python |
| Handoff | 3 | Standard contract I/O |
| Constraint Propagation | 2 | Minimal |
| Unique Value | 3 | Overlaps with line/copy editors |

### 14. chapter_planner — 2.8
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 3 | Generic |
| Standards | 3 | Generic |
| Boundaries | 2 | None |
| Schema Alignment | 3 | Some fields missing |
| Context Utilization | 3 | Generic |
| Prerequisite Gate | 3 | Basic |
| Fallback Robustness | 3 | Generic |
| Normalization | 2 | Only normalizes conflict_type; drops narrative_programs_active |
| Mapping Accuracy | 5 | Vars present |
| Error Messaging | 3 | Standard |
| Fidelity | 2 | Drops `narrative_programs_active` from LLM output despite model having field |
| Handoff | 4 | Writes chapter contracts |
| Constraint Propagation | 3 | Minimal |
| Unique Value | 2 | Thin wrapper; overlaps with outline_planner |

### 15. line_editor — 2.8
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 3 | Generic |
| Standards | 3 | Generic |
| Boundaries | 3 | "Don't rewrite, don't fix structural" |
| Schema Alignment | 2 | Loose |
| Context Utilization | 3 | Generic |
| Prerequisite Gate | 3 | Basic |
| Fallback Robustness | 2 | No fallback if LLM yields empty contracts_data |
| Normalization | 2 | Only checks it's a list |
| Mapping Accuracy | 4 | Vars present |
| Error Messaging | 2 | Generic |
| Fidelity | 3 | Edit validation missing |
| Handoff | 3 | Standard |
| Constraint Propagation | 2 | No edit scope validation |
| Unique Value | 3 | Sentence-level polish; overlaps with proofreader |

### 16. developmental_editor — 2.8
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 4 | Clear structural editor voice |
| Standards | 4 | Specific contract references, actionable recommendations |
| Boundaries | 2 | None |
| Schema Alignment | 3 | Some gaps |
| Context Utilization | 3 | Generic |
| Prerequisite Gate | 3 | Basic |
| Fallback Robustness | 1 | No fallback — pure LLM passthrough |
| Normalization | 2 | No field validation |
| Mapping Accuracy | 5 | Vars present |
| Error Messaging | 2 | Generic |
| Fidelity | 2 | Rich prompt but Python does no programmatic analysis |
| Handoff | 3 | Standard |
| Constraint Propagation | 3 | Mentions story/character in prompt but doesn't gate on them |
| Unique Value | 2 | Overlaps with critic's soft gate |

### 17. proofreader — 2.6
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 3 | Generic |
| Standards | 3 | Generic |
| Boundaries | 2 | Only one boundary rule |
| Schema Alignment | 2 | Only extracts clearance_recommendation — ignores error_density, critical_issues |
| Context Utilization | 3 | Generic |
| Prerequisite Gate | 3 | Basic |
| Fallback Robustness | 2 | No fallback if contract_data missing |
| Normalization | 2 | No field-level validation |
| Mapping Accuracy | 4 | Vars present |
| Error Messaging | 2 | Generic |
| Fidelity | 3 | Implements partially |
| Handoff | 3 | Writes critique |
| Constraint Propagation | 2 | No enforcement |
| Unique Value | 3 | Proofreading distinct from line editing |

### 18. copy_editor — 2.3
| Dim | Score | Rationale |
|-----|-------|-----------|
| Role Identity | 3 | Generic |
| Standards | 3 | Generic |
| Boundaries | 2 | None |
| Schema Alignment | 2 | quality_score never captured |
| Context Utilization | 3 | Generic |
| Prerequisite Gate | 3 | Basic |
| Fallback Robustness | 1 | No fallback — pure LLM passthrough |
| Normalization | 2 | No validation |
| Mapping Accuracy | 2 | **Bug:** prompt says `contracts_data` (plural) but code reads `contract_data` (singular) |
| Error Messaging | 2 | Generic |
| Fidelity | 2 | Rich editorial findings (grammar_issues, timeline_issues) discarded |
| Handoff | 2 | Only bare CritiqueContract written; rich analysis lost |
| Constraint Propagation | 2 | No enforcement |
| Unique Value | 3 | Copy editing is distinct from line editing |

## Dimension Heat Map

| Dimension | 5s | 4s | 3s | 2s | 1s |
|-----------|----|----|----|----|----|
| Role Identity | 3 | 4 | 11 | 0 | 0 |
| Standards | 3 | 6 | 9 | 0 | 0 |
| Boundaries | 1 | 0 | 3 | 14 | 0 |
| Schema Alignment | 3 | 8 | 4 | 3 | 0 |
| Context Utilization | 0 | 4 | 14 | 0 | 0 |
| Prerequisite Gate | 1 | 12 | 4 | 1 | 0 |
| Fallback Robustness | 1 | 5 | 8 | 2 | 2 |
| Normalization | 5 | 0 | 4 | 9 | 0 |
| Mapping Accuracy | 12 | 3 | 2 | 1 | 0 |
| Error Messaging | 0 | 2 | 10 | 6 | 0 |
| Fidelity | 3 | 7 | 6 | 2 | 0 |
| Handoff | 0 | 11 | 6 | 1 | 0 |
| Constraint Propagation | 0 | 1 | 13 | 3 | 1 |
| Unique Value | 3 | 5 | 8 | 2 | 0 |

## Improvement Backlog (by impact)

1. **copy_editor mapping bug** — `contracts_data` vs `contract_data` mismatch (map: 2→4, pick up ~0.2 avg)
2. **character_simulator silent success** — returns success=True with zero data on LLM failure (fal: 2→3, avg +0.07)
3. **revision_agent missing gate** — add get_prerequisites returning critique contracts (prq: 2→4, avg +0.14)
4. **Boundaries across the board** — 14/18 agents scored 2; scene_writer shows it's feasible to score 5
5. **Normalization in editorial agents** — copy_editor, developmental_editor, proofreader, line_editor all at 2

## Version History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| v1 | 2026-06-09 | OpenCode | Full 14-dimension scoring of all 18 agents |
