# Character Layers

There is no universally accepted exhaustive taxonomy for all character archetypes or types. The field explicitly lacks an established master classification scheme. The engine therefore separates character into **layers**, each handled by a distinct theoretical framework.

## Layer Stack

| Layer | Framework | Purpose |
|-------|-----------|---------|
| **Function** | Propp / Greimas actantial roles | What structural role does the character serve in the fabula? |
| **Dramatic Role** | Dramatic personae (23 roles) | What is the character's theatrical function in the narrative? |
| **Archetype** | Jungian archetypes | What symbolic/collective pattern does the character embody? |
| **Personality** | Five-Factor Model (Big Five) | Broad trait dimensions: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism |
| **Values** | Schwartz Theory of Basic Values (10/19 values) | What does the character see as worth pursuing? |
| **Social Mode** | Relational Models Theory (4 elementary models) | How does the character relate to others? |
| **Attachment** | Attachment frameworks | How does the character behave under relational threat? |
| **Enneagram** | Enneagram (fiction-use map) | Motivation/fear generator — fear + desire pair |
| **Narratological** | GOLEM + computational character ontologies | Structured attributes, relations, setting/event links |

## Dramatic Roles (Functional)

| Role | Definition |
|------|------------|
| **Protagonist** | Central character; drives the action |
| **Antagonist** | Opposes the protagonist |
| **Deuteragonist** | Second most important character |
| **Foil** | Contrasts with protagonist to highlight traits |
| **Mentor** | Guides or teaches the protagonist |
| **Ally** | Supports the protagonist |
| **Rival** | Competes with the protagonist |
| **Love Interest** | Object of romantic desire |
| **Trickster** | Undermines certainty; causes chaos |
| **Guardian** | Tests or protects the threshold |
| **Threshold Figure** | Guards the entrance to a new world/state |
| **False Ally** | Appears allied but is not |
| **False Hero** | Claims heroic status falsely |
| **Betrayer** | Switches sides |
| **Witness** | Observes; provides perspective |
| **Victim** | Suffers without agency |
| **Tempter** | Offers temptation |
| **Judge** | Evaluates or passes sentence |
| **Messenger** | Brings information or a call to action |
| **Protector** | Defends someone weaker |
| **Comic Relief** | Provides humour; reduces tension |
| **Moral Compass** | Embodies the story's ethical position |
| **Shadow Self** | Dark mirror of the protagonist |

Dramatic roles differ from actantial roles (Greimas): a Protagonist is a dramatic position; a Subject is an actantial position. One character can be both, but the layers are not equivalent.

## Propp Roles

| Role | Function |
|------|----------|
| **Hero** | The seeker or victim-hero |
| **Villain** | Causes harm or lacks |
| **Donor** | Provides magical agent or test |
| **Helper** | Aids the hero |
| **Princess / Sought-for Person** | The object of the quest |
| **Dispatcher** | Sends the hero |
| **False Hero** | Claims without deserving |

Propp's dramatis personae are role-functions, not personality types. One character can occupy several functions across the narrative.

## Greimas Actants

| Actant | Definition |
|--------|------------|
| **Subject** | Pursues the Object |
| **Object** | Value sought (abstract or concrete) |
| **Sender** | Initiates the quest / gives mandate |
| **Receiver** | Benefits from the Object |
| **Helper** | Enables the Subject |
| **Opponent** | Blocks the Subject |

**Important**: Character ≠ actant. One character can shift actantial position. One actant can be distributed across multiple characters, institutions, objects, or internal forces.

The Object can be abstract: truth, legitimacy, love, recognition, freedom, power, restoration.

## Jungian/Archetypal Fiction Roles

| Archetype | Core Drive |
|-----------|------------|
| **Hero** | Slay dragons, overcome |
| **Shadow** | Confront the repressed |
| **Mentor** | Guide the seeker |
| **Anima / Animus** | Encounter the inner other |
| **Self** | Achieve wholeness |
| **Persona** | Wear the social mask |
| **Trickster** | Break the pattern |
| **Wise Old Figure** | Dispense hard-won truth |
| **Great Mother** | Nurture or devour |
| **Child** | Innocence or new beginning |
| **Sage** | Seek knowledge |
| **Innocent** | Believe the best |
| **Explorer** | Venture into the unknown |
| **Ruler** | Take control, bring order |
| **Creator** | Build something new |
| **Caregiver** | Protect and nurture |
| **Magician** | Transform reality |
| **Outlaw** | Break the rules |
| **Lover** | Connect with others |
| **Jester** | Enjoy the moment |
| **Everyperson** | Fit in, belong |

Jungian archetypes remain influential in narrative and media analysis, but they are not empirical personality science. Use them as symbolic/story tools, not factual psychology.

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

## Enneagram (Fiction-Use Map)

Use as a motivation/fear generator, not as science.

| Type | Core Fear | Core Desire |
|------|-----------|-------------|
| 1 Reformer | Corruption | Integrity |
| 2 Helper | Being unloved | Love/worth |
| 3 Achiever | Worthlessness | Value/success |
| 4 Individualist | No identity | Uniqueness |
| 5 Investigator | Helplessness | Competence |
| 6 Loyalist | Insecurity | Safety |
| 7 Enthusiast | Deprivation | Freedom/options |
| 8 Challenger | Control/weakness | Autonomy/power |
| 9 Peacemaker | Separation | Peace/wholeness |

The Enneagram is widely used for fears/desires, but its scientific validation is disputed; treat it as a creative taxonomy.

## Integration

These layers feed into:
- Character contract (`/contracts/character-contract.yaml`)
- Character Architect agent decision-making
- Continuity Editor consistency checks (do traits stay stable unless arced?)
- Critic evaluation (are character actions consistent with their layered profile?)
