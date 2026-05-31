# Emotion Model

The engine uses **Plutchik's Wheel of Emotions** as its compact, operational emotion layer. Plutchik provides eight basic emotion dimensions arranged in opposing pairs, with intensity variation and combinatorial blends.

## Eight Basic Emotions

| Dimension | Opposite | Function |
|-----------|----------|----------|
| Joy | Sadness | Connection, gain |
| Trust | Disgust | Acceptance, protection |
| Fear | Anger | Protection from threat |
| Surprise | Anticipation | Orientation, preparation |

## Intensity Levels

Each basic emotion has three intensity levels:

| Basic | Low | Medium | High |
|-------|-----|--------|------|
| Joy | Serenity | Joy | Ecstasy |
| Sadness | Pensiveness | Sadness | Grief |
| Trust | Acceptance | Trust | Admiration |
| Disgust | Boredom | Disgust | Loathing |
| Fear | Apprehension | Fear | Terror |
| Anger | Annoyance | Anger | Rage |
| Surprise | Distraction | Surprise | Amazement |
| Anticipation | Interest | Anticipation | Vigilance |

## Combinatorial Blends

Emotions combine to form more complex emotional states:

- Joy + Trust = Love
- Trust + Fear = Submission
- Fear + Surprise = Awe
- Surprise + Sadness = Disapproval
- Sadness + Disgust = Remorse
- Disgust + Anger = Contempt
- Anger + Joy = Aggressiveness
- Anticipation + Joy = Optimism

## Role in the System

Emotion is tracked at three levels:

1. **Character emotional state** — per scene, what emotion(s) is the character experiencing?
2. **Scene emotional tone** — what emotional palette does the scene project?
3. **Reader emotional arc** — what emotional journey does the story design for the reader?

## Operational Use

- **Scene-state tagging** — each scene carries an emotional state vector (primary emotion + intensity)
- **Dialogue/emotion mismatch checks** — detect when character dialogue contradicts their tracked emotional state
- **Arc tracking** — emotional progression across the fabula
- **Critic evaluation** — is the emotional arc coherent? Are emotional shifts causally motivated?
