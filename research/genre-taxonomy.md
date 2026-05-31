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

## Major Genre Map

| Genre | Core Experience | Common Stakes |
|-------|-----------------|---------------|
| **Fantasy** | Wonder, power, myth, transformation | World restoration, power, identity |
| **Science Fiction** | Possibility, consequence, systems, future shock | Survival, truth, freedom |
| **Horror** | Dread, violation, survival, forbidden knowledge | Life/death, soul/damnation, sanity |
| **Thriller** | Threat, speed, pursuit, reversals | Life/death, freedom/captivity, truth |
| **Mystery** | Curiosity, clues, revelation, hidden truth | Truth/ignorance, justice/corruption |
| **Crime** | Transgression, law, corruption, moral compromise | Justice/corruption, power/subjugation |
| **Romance** | Desire, intimacy, obstacle, union/separation | Love/loss, belonging/exile |
| **Historical** | Immersion, continuity, period conflict | Legacy, justice, freedom |
| **Literary** | Interiority, language, ambiguity, meaning | Identity, memory, meaning |
| **Adventure** | Movement, danger, discovery, resourcefulness | Survival, freedom, discovery |
| **War** | Sacrifice, loyalty, trauma, survival | Life/death, honour/shame, legacy |
| **Satire** | Exposure, ridicule, social critique | Truth/comfort, justice/corruption |
| **Comedy** | Disorder, misrecognition, release, renewal | Belonging, love, identity |
| **Tragedy** | Flaw, inevitability, loss, recognition | Power, honour, identity |

## Genre Promises (Reader Contract)

Each genre carries an implicit promise to the reader:

| Genre | Promise |
|-------|---------|
| **Fantasy** | Wonder, power, myth, transformation |
| **Science Fiction** | Possibility, consequence, systems, future shock |
| **Horror** | Dread, violation, survival, forbidden knowledge |
| **Thriller** | Threat, speed, pursuit, reversals |
| **Mystery** | Curiosity, clues, revelation, hidden truth |
| **Crime** | Transgression, law, corruption, moral compromise |
| **Romance** | Desire, intimacy, obstacle, union/separation |
| **Historical** | Immersion, continuity, period conflict |
| **Literary** | Interiority, language, ambiguity, meaning |
| **Adventure** | Movement, danger, discovery, resourcefulness |
| **War** | Sacrifice, loyalty, trauma, survival |
| **Satire** | Exposure, ridicule, social critique |
| **Comedy** | Disorder, misrecognition, release, renewal |
| **Tragedy** | Flaw, inevitability, loss, recognition |

## Genre Selection Logic

Genre should be inferred from the seed, not chosen first. Selection heuristics:

| Seed Characteristic | Likely Genre(s) |
|--------------------|-----------------|
| Forbidden knowledge | Mystery, horror, dark academia, sci-fi |
| Lost order | Fantasy, dystopian, historical, epic |
| Desire blocked by society | Romance, literary, historical |
| System corruption | Crime, thriller, dystopia, satire |
| Identity formation | Coming-of-age, literary, fantasy |
| Power and cost | Fantasy, political thriller, tragedy |
| Survival under pressure | Thriller, horror, war, adventure |
