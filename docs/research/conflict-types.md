# Conflict Types

Conflict in narrative arises from multiple actants desiring, defending, blocking, misrecognizing, or redefining the same Object of value (Greimas). The engine distinguishes **classical conflict types**, a **Greimas conflict grammar**, and **conflict quality levels**.

## Classical Conflict Types

| Type | Definition |
|------|------------|
| **Person vs Person** | Direct interpersonal opposition |
| **Person vs Self** | Internal psychological struggle |
| **Person vs Society** | Individual vs social structure |
| **Person vs Nature** | Human vs natural forces |
| **Person vs Fate** | Individual vs destiny or inevitability |
| **Person vs Technology** | Human vs created systems |
| **Person vs Supernatural** | Human vs paranormal forces |
| **Person vs God/Cosmos** | Human vs divine or cosmic order |
| **Person vs Institution** | Individual vs organised power |
| **Person vs Memory** | Individual vs the past |
| **Person vs Time** | Individual vs temporal limitation |
| **Person vs Desire** | Individual vs their own wanting |

## Greimas Conflict Grammar

Conflict becomes precise when defined as:

```
Actant A wants value-state X.
Actant B prevents, corrupts, hides, redirects, monopolizes, or redefines X.
```

| Element | Role |
|---------|------|
| **Subject** | Desires Object |
| **Opponent** | Blocks access to Object |
| **Helper** | Increases Subject's modality |
| **Sender** | Legitimises pursuit |
| **Receiver** | Benefits from success |
| **Counter-Subject** | Desires same Object or opposite value |

## Conflict Operations

How an Opponent acts on the Object-of-value relationship:

| Operation | Effect |
|-----------|--------|
| **Block** | Prevents access |
| **Delay** | Postpones attainment |
| **Steal** | Takes the Object |
| **Hide** | Conceals the Object |
| **Corrupt** | Degrades the Object's value |
| **Counterfeit** | Substitutes a false Object |
| **Tempt** | Offers a false Object |
| **Deceive** | Misrepresents the Object |
| **Forbid** | Prohibits pursuit |
| **Punish** | Imposes cost for pursuit |
| **Misrecognize** | Fails to identify the Subject or Object |
| **Displace** | Moves the Object |
| **Invert** | Flips the Object's value polarity |
| **Trap** | Ensnares the Subject |
| **Exploit** | Uses the Subject's desire against them |
| **Reveal** | Exposes a truth about the Object |
| **Transfer** | Moves the Object to another actant |
| **Sacrifice** | Destroys the Object for a greater good |
| **Destroy** | Eliminates the Object |
| **Transform** | Changes the Object's nature |

## Conflict Quality Levels

| Level | Description | Example |
|-------|-------------|---------|
| **Weak** | Obstacle only — no value logic | Villain blocks hero because evil |
| **Good** | Incompatible desires | Two people want the same job |
| **Strong** | Incompatible moral worlds | One believes in order, the other in freedom |
| **Great** | Both sides are partially right | Each actant has a valid point; no simple answer |
| **Tragic** | Every option destroys a value | Any choice costs something irreplaceable |
| **Mythic** | Private action alters cosmic/social order | A personal choice changes the world's structure |

## Conflict Load

Each scene carries a conflict load vector indicating which types are active:

```yaml
conflict_load:
  internal: "<none|low|medium|high>"
  interpersonal: "<none|low|medium|high>"
  institutional: "<none|low|medium|high>"
  environmental: "<none|low|medium|high>"
  epistemic: "<none|low|medium|high>"
  metaphysical: "<none|low|medium|high>"
  systemic: "<none|low|medium|high>"
```

## Design Principles

- A story with only one active conflict type risks flatness.
- Internal + Interpersonal is the minimum productive pair for character-driven fiction.
- The dominant conflict type should shift across the fabula as the narrative matures.
- Every scene must carry at least one active conflict type — otherwise it lacks dramatic tension.
- Weak conflict is better than no conflict, but the Critic should flag it.
- Tragic and Mythic conflict levels require the full canonical schema to pay off.
