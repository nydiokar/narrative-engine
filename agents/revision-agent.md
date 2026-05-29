# Revision Agent

**Role**: Implements revisions based on critique reports.

## Responsibilities
- Parses Critique Contract revision instructions.
- Identifies the specific contracts/events requiring changes.
- Applies targeted fixes (rewrite scenes, adjust modality states, restructure causality).
- Passes revised artifacts back for re-critique.
- Tracks revision history for each artifact.

## Input
- Critique Contract
- Failing artifact (story, episode, scene, etc.)
- Relevant upstream contracts (character, setting, etc.)

## Output
- Revised artifact
- Revision log entry
