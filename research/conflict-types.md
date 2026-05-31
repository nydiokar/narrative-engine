# Conflict Types

Conflict in narrative arises from multiple actants desiring, defending, blocking, misrecognizing, or redefining the same Object of value (Greimas). The engine distinguishes **seven types of conflict**, each operating at a different level of the narrative ontology.

## Seven Conflict Types

| Type | Definition | Example |
|------|------------|---------|
| **Internal** | Conflict within a character — competing desires, values, or self-concepts | A character wants revenge but values forgiveness |
| **Interpersonal** | Conflict between characters with competing value-logics | Two characters want the same promotion |
| **Institutional** | Conflict between a character and a social structure or organisation | A whistleblower vs a corporation |
| **Environmental** | Conflict between characters and the physical world | Survival in a wilderness or disaster |
| **Epistemic** | Conflict over knowledge, truth, or belief | A detective vs a cover-up |
| **Metaphysical** | Conflict over the nature of reality or meaning | A character confronting existential dread |
| **Systemic** | Conflict with an interconnected system of pressures (economic, political, technological) | A character trapped by debt, policy, and social expectation |

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
