# Narrative Engine

Theory-first narrative generation engine with formal narratological validation (Greimas, Propp, Todorov, Modality).

## Quick Start

```bash
python -m src run --to premise
python -m src run --save trunk.json
python -m src branch --vary genre --values fantasy,scifi --tree-load trunk.json --tree-save tree.json
python -m src compare --labels fantasy,scifi --tree-load tree.json
```

## Architecture

The pipeline runs **8 workflows** through **18 agent roles**, communicating through a typed contract store:

| Workflow | Purpose |
|----------|---------|
| 00 — Brief & Taxonomy | Theme, genre, world axes, character layers |
| 01 — Seed to Premise | Premise analysis, actantial model, protagonist |
| 02 — Premise to Structure | Fabula construction, constraints, thematic fit |
| 03 — Structure to Episodes | Episode/chapter segmentation, arcs, settings |
| 04 — Episodes to Scenes | Scene rendering, Greimas diagnostics, continuity |
| 05 — Scenes to Draft | Finalization, assembly |
| 06 — Editorial Passes | Developmental → line → copy → proof |
| 07 — Critique & Revision | Hard Gate → Soft Gate → Revision → Approval |

See [System Overview](system-overview.md), [Pipeline Map](pipeline-map.md), and [Workflows](workflows/index.md).

## Key Concepts

- **Theory-first**: Narrative is a product of deep structural constraints, not stochastic LLM text
- **Deterministic**: Every story beat follows from logical necessity
- **Two-gate evaluation**: Hard Gate (structural soundness) → Soft Gate (novelty, genre fit)
- **Contract-driven**: Agents communicate through a typed contract store (no agent memory)
- **Medium-agnostic**: Same structure engine, different rendering per medium (book, animation, movie, series)

## Documentation

- [Usage Guide](usage.md)
- [Agents Overview](agents-overview.md)
- [API Reference](api/contracts.md)
- [Theory Notes](theory-notes.md)
- [Glossary](glossary.md)
- [Roadmap](roadmap.md)
