# Discourse Layer (Sujet)

The discourse layer governs *how* the fabula is presented to the reader — the sujet-level decisions that shape reader experience. This is distinct from the fabula (what happens).

## Discourse Dimensions

| Dimension | Options | Narrative Effect |
|-----------|---------|------------------|
| **Point of View** | First-person, Second-person, Third-limited, Third-omniscient, Third-objective | Information access, intimacy, reliability |
| **Focalisation** | Internal (through character), External (behavioural), Zero (omniscient) | What the reader knows and when |
| **Tense** | Past, Present, Future (rare) | Temporal distance, immediacy |
| **Temporal Handling** | Chronological, Analepsis (flashback), Prolepsis (flash-forward), Ellipsis (gap), Pause (description), Summary, Scene, Stretch | Pacing, information reveal |
| **Exposition Strategy** | Integrated (shown), Block (told), Delayed, Withheld | Information economy |
| **Suspense Strategy** | Mystery (past-oriented), Suspense (future-oriented), Surprise (present-oriented) | Reader engagement mode |
| **Dialogue Mode** | Direct, Indirect, Free indirect, Narratised | Character voice vs narrator voice |
| **Voice** | Register, diction, sentence rhythm, metaphor density | Prose identity |

## Discourse Contract

The discourse configuration is declared in a `discourse_contract` (see `/contracts/discourse-contract.yaml`) per story. Changes within a story (e.g., POV switch between chapters) are tracked as discourse events.

## Constraints

- Discourse choices must be consistent within a scene (no unmotivated POV shifts).
- Focalisation determines what information is available to the reader — the fabula chain must respect these constraints.
- Temporal handling choices must not produce causal contradictions in the reader's inferred fabula.
- Voice should be consistent within a narrative program unless a discourse event explicitly changes it.
