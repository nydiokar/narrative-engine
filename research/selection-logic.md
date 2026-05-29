# Selection Logic

The engine uses deterministic selection rules to make narrative choices:

## Function Selection
- Given a current narrative state, the set of valid next Proppian functions is determined by the canonical sequence.
- Genre constraints further restrict the set.
- The Director selects the function that maximizes narrative tension or satisfies the required transformation.

## Actant Assignment
- Actant roles are assigned at the start of generation.
- A single character may occupy multiple actant roles across different narrative programs.
- Helper and Opponent roles may shift as the fabula progresses.

## Event Causality
- Every event must have a prior cause (no ex nihilo events).
- Events are linked by: cause → effect, or lack → acquisition.
- Temporal jumps are permitted only if a causality chain can be inferred.
