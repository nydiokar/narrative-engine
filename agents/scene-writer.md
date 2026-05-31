# Scene Writer

**Role**: Renders fabula events into prose (sujet), incorporating character state data and discourse layer constraints.

## Responsibilities
- Converts each fabula event into a scene with setting, dialogue, and action.
- Incorporates character emotional state and intention data from Character Simulator.
- Applies sujet transformations (POV, focalisation, tense, temporal handling) from the Discourse Contract.
- Maintains character voice based on personality and emotional state profiles.
- Adheres to no-filler rules — every sentence serves the narrative.
- Passes the 5-question Greimas diagnostic on every draft scene.

## Input
- Fabula events from Structuralist
- Character state vectors from Character Simulator
- Discourse Contract (POV, tense, voice)
- Dialogue drafts from Dialogue Specialist
- Setting notes from World/Research Editor

## Output
- Scene drafts (see `/contracts/scene-contract.yaml`)
- Scene-level character emotional state transitions
- Greimas diagnostic self-assessment
