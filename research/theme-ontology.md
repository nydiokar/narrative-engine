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

## Constraints

- A theme must be instantiated by at least one narrative program — otherwise it is decorative.
- Conflicting themes (e.g., freedom vs security) generate productive tension.
- Theme drift across the fabula is permitted only if causally motivated.
