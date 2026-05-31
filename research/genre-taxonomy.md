# Genre Taxonomy

The engine uses **BISAC** (Book Industry Study Group) as its genre taxonomy. BISAC provides a large, up-to-date fiction subject tree maintained by industry standards — not an ad-hoc list.

## BISAC Fiction Categories (Top-Level)

| Code | Category |
|------|----------|
| FIC002000 | Action & Adventure |
| FIC004000 | Alternative History |
| FIC043000 | Coming of Age |
| FIC050000 | Crime |
| FIC028000 | Dystopian |
| FIC009000 | Fantasy (with subfamilies) |
| FIC019000 | Gothic |
| FIC014000 | Historical |
| FIC000000 | Literary |
| FIC076000 | LitRPG |
| FIC026000 | Magical Realism |
| FIC022000 | Mystery |
| FIC027000 | Romance (with subfamilies) |
| FIC028000 | Science Fiction (with subfamilies) |
| FIC031000 | Thriller |
| FIC033000 | Western |

## Role in the System

Genre constrains:
- Which Propp function sequences are available
- Which actantial configurations are typical
- Which thematic clusters are expected
- Which worldbuilding dimensions are relevant
- Audience expectations (pace, tone, resolution mode)

## BISAC as Market Map

BISAC is not a theory of genre — it is a practical, searchable market map. The engine uses it as the **primary genre classifier** for:
- Metadata generation (blurbs, keywords, BISAC codes)
- Audience promise validation
- Comparative title matching (comps)
- Genre-fit scoring in the evaluation soft gate

## Hierarchical Subfamilies

Each top-level category has subfamilies. For example:

```
FIC009000 Fantasy
  ├── FIC009010 — Action & Adventure Fantasy
  ├── FIC009020 — Dark Fantasy
  ├── FIC009030 — Epic Fantasy
  ├── FIC009050 — Historical Fantasy
  ├── FIC009060 — Romantic Fantasy
  └── FIC009100 — Urban Fantasy
```

The engine navigates this tree to select the most specific valid classification.
