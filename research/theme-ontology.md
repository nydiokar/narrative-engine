# Theme Ontology

The engine uses the **Literary Theme Ontology (LTO)** as its theme layer. LTO exposes ~2,990 defined literary themes in a hierarchy with annotated stories, providing a searchable map for theme selection, matching, and evaluation.

## Role in the System

Themes sit at the **concept layer** of the narrative ontology, above structure and below character. They define what the story is *about* in the abstract sense — the claims, moral tensions, and symbolic motifs that give the fabula meaning.

## Theme Hierarchy Approach

Themes are organised as a directed hierarchy:

```
Root Theme
  ├── Sub-theme A
  │     ├── Specific theme A1
  │     └── Specific theme A2
  └── Sub-theme B
        └── Specific theme B1
```

The engine uses this hierarchy for:
- **Selection** — choose themes that match the premise and genre
- **Matching** — detect which themes a given fabula instantiates
- **Evaluation** — assess whether the narrative delivers on its declared themes

## Theme Contract Integration

Every story carries a `theme_contract` (see `/contracts/theme-contract.yaml`) that declares:
- Primary themes (1-3)
- Secondary themes (0-5)
- Moral tensions between conflicting themes
- Symbolic motifs that embody themes at the scene level

## Theme Families (Core Tensions)

| Family | Pole A | Pole B |
|--------|--------|--------|
| Freedom vs Security | Liberty, autonomy | Safety, protection |
| Love vs Duty | Personal desire | Obligation, honour |
| Truth vs Comfort | Honesty, reality | Peace, denial |
| Justice vs Mercy | Fairness, punishment | Compassion, forgiveness |
| Power vs Sacrifice | Control, influence | Cost, loss |
| Identity vs Belonging | Individual self | Group acceptance |
| Order vs Vitality | Structure, stability | Chaos, life |
| Tradition vs Change | Continuity, heritage | Progress, renewal |
| Innocence vs Experience | Purity, naivety | Knowledge, worldliness |
| Ambition vs Integrity | Drive, success | Principles, honesty |
| Memory vs Forgetting | Holding on | Letting go |
| Faith vs Doubt | Belief, trust | Skepticism, uncertainty |
| Revenge vs Forgiveness | Retribution | Release |
| Individual vs Collective | Self-interest | Common good |
| Nature vs Civilisation | Wild, natural | Constructed, ordered |
| Control vs Surrender | Mastery, will | Acceptance, release |
| Desire vs Responsibility | Wanting | Duty |
| Survival vs Humanity | Persistence | Moral integrity |
| Recognition vs Humility | Being seen | Being modest |
| Destiny vs Choice | Fate | Free will |

## Moral Question Forms

The theme family generates a specific moral question that the narrative must answer through action:

| Theme Family | Moral Question Form |
|-------------|---------------------|
| Freedom vs Security | What must be sacrificed to gain freedom? |
| Truth vs Comfort | Is truth worth destroying peace? |
| Justice vs Mercy | Can justice exist without mercy? |
| Love vs Duty | When does love become possession? |
| Power vs Sacrifice | Can power remain innocent? |
| Identity vs Belonging | Is belonging worth self-betrayal? |
| Revenge vs Forgiveness | Is revenge ever restoration? |
| Survival vs Humanity | When does survival become corruption? |
| Memory vs Forgetting | Can a lie protect something true? |
| Faith vs Doubt | Can a broken person become trustworthy? |
| Individual vs Collective | When is obedience moral cowardice? |
| Order vs Vitality | When does order become oppression? |

General forms:
- What must be sacrificed to gain X?
- Is X worth destroying Y?
- Can X exist without Y?
- When does X become Y?
- Can a broken person become trustworthy?
- Is belonging worth self-betrayal?
- When is obedience moral cowardice?
- When does survival become corruption?
- Can a lie protect something true?
- Is forgiveness possible without recognition?

## Theme Expression Channels

Themes are expressed through:

| Channel | How |
|---------|-----|
| **Protagonist Arc** | The protagonist's choices embody the theme |
| **Antagonist Worldview** | The antagonist's values counter the theme |
| **Object of Value** | What is sought defines the theme's stakes |
| **World Rules** | The setting's structure pressures the theme |
| **Central Relationship** | The key relationship dramatises the tension |
| **Repeated Choice** | The protagonist faces the same dilemma with escalating cost |
| **Symbolic Object** | An object instantiates the theme (see `/research/symbolism-motifs.md`) |
| **Ending** | The final junction answers the moral question |
| **Sanction/Judgment** | How the world evaluates the protagonist's choice |
| **Cost of Victory** | What was lost in attaining the Object |

## Constraints

- A theme must be instantiated by at least one narrative program — otherwise it is decorative.
- Conflicting themes (e.g., freedom vs security) generate productive tension.
- Theme drift across the fabula is permitted only if causally motivated.
- The ending must answer the moral question posed by the theme — even if the answer is "there is no answer."
