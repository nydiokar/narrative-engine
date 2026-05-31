# System Overview

The Narrative Engine is a multi-agent architecture for generating story narratives grounded in formal narratological theory. It operates on the **complete narrative ontology stack**.

## Full Ontology Stack

```
BRIEF LAYER        — medium, audience, age band, language, target length,
                     series/standalone, content limits, market position
CONCEPT LAYER      — premise, logline, story promise, hook, comps
STRUCTURE LAYER    — Greimas actantial model, canonical schema,
                     Propp morphology, chapter architecture, scene goals
FABULA LAYER       — characters, goals, actions, outcomes, events,
                     perceptions, internal states
THEME LAYER        — LTO themes, claims, moral tensions, symbolic motifs
CHARACTER LAYER    — function (Propp/Greimas), personality (FFM),
                     values (Schwartz), social mode (RMT), attachment,
                     motivation stack (SDT + Reiss), emotion (Plutchik)
CONFLICT LAYER     — internal, interpersonal, institutional, environmental,
                     epistemic, metaphysical, systemic
WORLD LAYER        — setting, rules, causality, social order,
                     technology/magic, economy, ecology, history
DISCOURSE LAYER    — POV, focalisation, tense, temporal handling,
                     exposition strategy, suspense strategy, dialogue mode, voice
CONTROL LAYER      — continuity bible, fact map, timeline, location bible,
                     terminology sheet
EDITORIAL LAYER    — developmental, line, copy, proof
EVALUATION LAYER   — hard gate (structural soundness), soft gate (quality ranking)
```

## Pipeline

```
Human seed / premise
  → Genre + theme selection (BISAC, LTO)
    → Greimas deep narrative logic (value-objects, actants, canonical schema)
      → Propp functional skeleton (one possible morphology)
        → Fabula construction (goal → action → outcome → event)
          → Episode / chapter / scene expansion
            → Character simulation + emotional arc tracking
              → Discourse rendering (POV, tense, voice)
                → Editorial passes (developmental → line → copy → proof)
                  → Evaluation loop (hard gate → soft gate → revision)
```

## Key Design Decisions

- **Narrative ontology stack**: 12 layers from brief to evaluation, each with its own theoretical framework and contract schema.
- **Greimas above Propp**: Greimas defines structural necessity; Propp provides one possible functional morphology.
- **Layered character model**: Function + personality + values + social mode + attachment + motivation + emotion — seven distinct frameworks fused into one profile.
- **Two-gate evaluation**: Hard gate (structural soundness) rejects broken narratives; soft gate (novelty, genre fit, thematic clarity) ranks sound candidates.
- **Professional role stack**: The system simulates a production pipeline — Showrunner, Script Editor, Theme Specialist, Character Simulator, Dialogue Specialist, Development Editor, Line Editor, Copy Editor, Proofreader.
- **Contract-driven data flow**: agents communicate via typed contracts (YAML schemas).
