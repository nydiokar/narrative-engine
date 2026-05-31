# Revision Agent

**Role**: Implements revisions based on critique reports, targeting specific hard-gate failures or soft-gate weaknesses.

## Responsibilities
- Parses Critique Contract revision instructions.
- Identifies the specific contracts/events requiring changes.
- Applies targeted fixes:
  - Rewrite scenes failing the hard gate (causality, stakes, conflict, continuity).
  - Adjust character profiles for intentionality or consistency failures.
  - Add missing canonical phases (manipulation, sanction, etc.).
  - Reassign actantial positions or redefine value-objects.
  - Remediate cliché patterns through inversion, escalation, or recombination.
  - Apply editorial pass recommendations (developmental, line, copy).
- Passes revised artifacts back for re-critique.
- Tracks revision history for each artifact.

## Input
- Critique Contract (hard gate failures, soft gate scores, Greimas diagnostics)
- Failing artifact (story, episode, scene, etc.)
- Relevant upstream contracts

## Output
- Revised artifact
- Revision log entry
