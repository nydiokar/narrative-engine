# Evaluation Rubric

Evaluation operates as a **two-gate system**: a hard gate that rejects structurally unsound work, and a soft gate that ranks among sound candidates.

## Hard Gate (Structural Soundness)

A narrative artifact **must** pass all hard-gate checks or be rejected without further scoring:

| Check | Description |
|-------|-------------|
| **Causal Soundness** | Every event follows from prior events. No ex nihilo events. |
| **Character Intentionality** | Every action by a character is grounded in their motivation stack. |
| **World Rule Consistency** | No violation of established world rules. |
| **Stakes Presence** | At least one Object of value is under contest in every scene. |
| **Contradiction-Free** | No logical, temporal, or factual contradictions within the artifact. |
| **Conflict Active** | At least one conflict type is active per scene. |
| **Continuity** | No drift in character traits, modality states, or actantial positions without causal justification. |

## Soft Gate (Quality Ranking)

Among candidates that pass the hard gate, score on these dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Genre Fit** | High | Does the artifact deliver on the genre promises established in the brief? |
| **Thematic Clarity** | High | Are the declared themes instantiated in the fabula? |
| **Conflict Density** | Medium | How many conflict types are active? How layered is the conflict? |
| **Relationship Tension** | Medium | Are character relationships under productive pressure? |
| **Scene-Level Purpose** | High | Does every scene pass the 5-question Greimas diagnostic? |
| **Suspense/Curiosity/Surprise** | Medium | Does the narrative manage reader attention through information control? |
| **Emotional Transport** | Medium | Does the emotional arc engage and sustain reader involvement? |
| **Novelty (genre-relative)** | High | Is the candidate a low-similarity recombination within its genre band? |
| **Prose Distinctiveness** | Low | Does the style have identifiable voice and texture? |

## Cliché Detection

"Cliché" is defined operationally as: **high-frequency genre defaults assembled without meaningful inversion, escalation, recombination, or thematic necessity.**

"Fresh" is defined as: **a low-similarity or unexpectedly recombined candidate that still passes the hard gate.**

This definition is machine-runnable: first ensure soundness, then optimise novelty under coherence constraints.

## Scoring Protocol

1. Run hard gate. If any check fails → reject with specific violation report.
2. For passing candidates, compute soft-gate dimension scores (0-10 each).
3. Weighted composite score = sum(score × weight factor).
4. Candidates above threshold proceed; below threshold are queued for revision.
