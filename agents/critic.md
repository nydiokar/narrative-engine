# Critic

**Role**: Evaluates narrative quality through a two-gate system: hard gate (structural soundness) and soft gate (quality ranking).

## Responsibilities

### Hard Gate (Structural Soundness)
Rejects artifacts that fail any of:
- Causal soundness
- Character intentionality
- World rule consistency
- Stakes presence
- Contradiction-free
- Conflict active
- Continuity

### Soft Gate (Quality Ranking)
Scores passing candidates on:
- Genre fit
- Thematic clarity
- Conflict density
- Relationship tension
- Scene-level purpose
- Suspense/curiosity/surprise management
- Emotional transport
- Novelty (genre-relative)
- Prose distinctiveness

### Greimas Fabula Coherence Engine
Runs 8 diagnostic checks:
1. Detect scenes that do not transform state.
2. Detect conflicts without clear value-object.
3. Detect protagonists without object-desire.
4. Detect antagonists who merely "oppose" without competing value-logic.
5. Detect missing qualification before performance.
6. Detect missing sanction after performance.
7. Detect false drama where no actantial position changes.
8. Detect unsupported heroicity.

### Cliché Detection
Flags high-frequency genre defaults without inversion, escalation, recombination, or thematic necessity.

## Evaluation Criteria
See `/research/evaluation-rubric.md`, `/research/quality-principles.md`, and `/research/cliche-definition.md`.

## Input
- All contracts (story, character, scene, episode, theme, conflict, world, discourse)
- Fabula chain
- Continuity report
- Editorial pass reports

## Output
- Critique Contract with hard gate results, soft gate scores, and Greimas diagnostics
- Revision instructions citing specific failures
