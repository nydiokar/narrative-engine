# Selection Logic

The engine uses deterministic selection rules to make narrative choices. The Greimas layer constrains and validates Propp selections. The selection order and rejection rules prevent weak or incoherent combinations.

## Selection Order

The recommended order for populating the narrative ontology from a human seed:

1. **Human seed** — capture the raw premise.
2. **Desired emotional effect** — what should the reader feel?
3. **Object of Value** — what value-state is under contest?
4. **Core moral question** — what thematic tension animates the story?
5. **Protagonist wound/desire** — what drives the Subject?
6. **Antagonistic force** — who/what blocks and why?
7. **Genre promise** — what does the reader expect?
8. **World pressure** — how does the setting force choices?
9. **Plot morphology** — which structural grammar fits?
10. **Tone/style** — how is the story told?
11. **Ending type** — what final junction sanctions the journey?
12. **Scene engine** — build the scene chain.

## Do Not Choose Genre First

Genre should be inferred from the seed, not chosen first unless the user already knows it. Use the selection heuristics in `/research/genre-taxonomy.md`:

| Seed Focus | Lead Selection |
|------------|----------------|
| Symbolic | Choose Object of Value first |
| Action-based | Choose conflict first |
| Setting-based | Choose world first |
| Psychological | Choose character wound first |
| Market/audience-based | Choose genre first |

## Greimas Layer — Structural Necessity Selection

- Given a current actantial configuration, the system identifies which canonical phase is required next (Manipulation → Competence → Performance → Sanction).
- The Object of value determines what kinds of transformations are meaningful.
- Conflict opportunities are identified by detecting which actants desire, defend, or block the same value-object.
- The Showrunner selects the narrative program that maximizes structural necessity and genre congruence.

## Propp Layer — Functional Sequence Selection

- Given a Greimas-validated narrative program, the set of valid next Proppian functions is determined by the canonical sequence.
- Genre constraints further restrict the set.
- A Propp function is only selected if it serves an active Greimasian narrative program.

## Actant Assignment

- Actant roles are assigned at the start of generation based on the value-object analysis.
- A single character may occupy multiple actant roles across different narrative programs.
- Actantial positions shift as the Object of value is redefined or as new narrative programs begin.
- Helper and Opponent roles must have their own value-logic — not merely "aid" or "oppose."

## Rejection Rules

Reject a narrative option if:

- It does not pressure the protagonist.
- It does not clarify the Object of Value.
- It does not create scene conflict.
- It contradicts genre promise without purpose.
- It makes the ending obvious too early.
- It solves the story too easily.
- It adds lore without action-state consequences.

## Matrix Compatibility

The core compatibility chain: **Seed → Object of Value → Theme → Genre → World → Character Wound → Conflict → Ending**

### Good-Fit Patterns

| Pattern | Why It Works |
|---------|--------------|
| Revenge + shame wound + tragedy | The wound justifies the drive; tragedy pays the cost |
| Freedom theme + prison world + control antagonist | The world and antagonist embody the thematic obstacle |
| Love theme + forbidden relationship + social order | Social order provides the obstacle that tests love |
| Truth theme + mystery structure + deceptive world | Every layer reinforces the epistemic struggle |
| Power theme + ambitious protagonist + corrupting object | The protagonist's desire meets an escalator |

### Productive Clashes

| Clash | Effect |
|-------|--------|
| Soft character in brutal world | Character must harden or break |
| Comic tone over tragic structure | Ironic distance heightens tragedy |
| Sacred theme in profane world | Faith is tested by reality |
| Romance inside political collapse | Intimacy against impossibility |
| Innocent protagonist in corrupt system | Naivety exposed to complexity |
| Mystery inside fantasy world | Epistemic + magical uncertainty |
| Horror inside domestic realism | The familiar becomes terrifying |
| Epic stakes through intimate POV | Scale felt through personal cost |

### Destructive Clashes

| Clash | Why It Fails |
|-------|--------------|
| Theme says freedom, plot rewards obedience without irony | Contradiction between stated theme and actual payoff |
| Protagonist wants nothing, but story demands quest | No Subject desire = no narrative program |
| World rules forbid solution, but ending ignores rules | Deus ex machina violates contract |
| Villain blocks nothing specific | Opposition without value-object is noise |
| Scenes happen but no state changes | Filler — no action/state transformation |
| Tone promises realism, plot depends on coincidence | Genre promise broken |
| Romance promised, intimacy never tested | No obstacle = no drama |
| Mystery promised, clues are withheld unfairly | Reader contract violated |
