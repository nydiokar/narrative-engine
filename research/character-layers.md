# Character Layers

There is no universally accepted exhaustive taxonomy for all character archetypes or types. The field explicitly lacks an established master classification scheme. The engine therefore separates character into **layers**, each handled by a distinct theoretical framework.

## Layer Stack

| Layer | Framework | Purpose |
|-------|-----------|---------|
| **Function** | Propp / Greimas actantial roles | What structural role does the character serve in the fabula? |
| **Personality** | Five-Factor Model (Big Five) | Broad trait dimensions: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism |
| **Values** | Schwartz Theory of Basic Values (10/19 values) | What does the character see as worth pursuing? |
| **Social Mode** | Relational Models Theory (4 elementary models) | How does the character relate to others? |
| **Attachment** | Attachment frameworks | How does the character behave under relational threat? |
| **Narratological** | GOLEM + computational character ontologies | Structured attributes, relations, setting/event links |

## Five-Factor Model (Personality)

- **Openness** — imagination, insight, willingness to try new things
- **Conscientiousness** — organisation, dependability, discipline
- **Extraversion** — sociability, assertiveness, emotional expressiveness
- **Agreeableness** — compassion, cooperativeness, trust
- **Neuroticism** — emotional instability, anxiety, moodiness

Each trait is scored 1-10. Character behaviour must be consistent with trait scores across the fabula, unless a narrative program explicitly modifies a trait (arc).

## Schwartz Values

The ten broad values:
1. Self-Direction
2. Stimulation
3. Hedonism
4. Achievement
5. Power
6. Security
7. Conformity
8. Tradition
9. Benevolence
10. Universalism

A refined set of 19 values is available for finer granularity. Character values create the value-logic that drives actantial opposition.

## Relational Models Theory

Four elementary models for social relationships:
- **Communal Sharing** — what's mine is ours
- **Authority Ranking** — hierarchies, precedence
- **Equality Matching** — turn-taking, reciprocity
- **Market Pricing** — costs, benefits, ratios

Characters can operate in different models depending on context.

## Attachment Patterns

- Secure
- Anxious-preoccupied
- Dismissive-avoidant
- Fearful-avoidant

Attachment patterns govern character behaviour under relationship conflict, loss, and intimacy.

## Integration

These layers feed into:
- Character contract (`/contracts/character-contract.yaml`)
- Character Architect agent decision-making
- Continuity Editor consistency checks (do traits stay stable unless arced?)
- Critic evaluation (are character actions consistent with their layered profile?)
