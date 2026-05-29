# System Overview

The Narrative Engine is a multi-agent architecture for generating story narratives grounded in formal narratological theory. It operates on a strict pipeline:

1. **Human Intake** — raw premise, constraints, and authorial intent are captured.
2. **Structuralization** — the premise is decomposed into a fabula (deep narrative structure) using Greimasian actantial models and Proppian functions.
3. **Expansion** — the fabula is expanded into episodes, scenes, and finally prose.
4. **Critique & Revision** — each artifact passes through automated critique; failures trigger targeted revision.

## Key Design Decisions

- **Separation of fabula and sujet**: deep structure (what happens) is kept distinct from surface presentation (how it is told).
- **Deterministic generation**: every narrative choice follows from prior constraints; no random filler.
- **Contract-driven data flow**: agents communicate via typed contracts (YAML schemas), not ad-hoc formats.
