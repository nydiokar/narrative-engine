# Character Simulator

**Role**: Enacts the story through character agents, simulating decisions and reactions before the Scene Writer renders prose.

**Analogous to**: Character-simulation systems used in state-of-the-art story generation research.

## Responsibilities
- Loads character profiles (personality, values, motivation, emotion, attachment).
- Simulates character reactions to each event in the fabula chain.
- Generates character intentions and decisions at each story beat.
- Produces character-state vectors (emotional state, modality state, goal polarity) per scene.
- Flags character-inconsistent plot developments before drafting.
- Provides character interiority data for the Scene Writer and Dialogue Specialist.

## Input
- Fabula chain
- Character contracts (full layered profiles)
- Current narrative program state

## Output
- Per-scene character state vectors
- Character intention logs
- Consistency warnings for the Continuity Editor
- Interiority notes for prose rendering
