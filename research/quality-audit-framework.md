# Quality Audit Framework — v1

A systematic rubric for evaluating the quality of narrative engine agents.
Each agent consists of three layers: a **Python logic agent** (`src/agents/*.py`), a **prompt template** (`src/agents/prompts/*.md`), and a **semantic agent config** (`.opencode/agents/*.md`).

---

## Scoring

Every dimension is scored **1–5**:

| Score | Meaning |
|-------|---------|
| 1 | Missing or broken — causes pipeline failures |
| 2 | Present but flawed — degrades output quality |
| 3 | Functional — meets baseline expectations |
| 4 | Solid — handles edge cases, clear design |
| 5 | Excellent — exemplary, sets the standard |

---

## Category I: Prompt Quality (5 dimensions)

### 1. Role Identity
Does the prompt establish a clear, distinct role identity with specific expertise?

| Score | Criteria |
|-------|----------|
| 1 | No role defined; generic "you are an AI assistant" |
| 2 | Role named but no expertise or voice |
| 3 | Clear role with domain-specific knowledge signaled |
| 4 | Role has distinctive voice, methodology, and stance |
| 5 | Role includes professional lineage, critical self-awareness, and aesthetic philosophy |

### 2. Standards & Expectations
Does the prompt set concrete quality standards (not vague "do your best")?

| Score | Criteria |
|-------|----------|
| 1 | No quality criteria mentioned |
| 2 | Vague standards — "high quality", "be thorough" |
| 3 | Specific criteria listed but not operationalized |
| 4 | Criteria include thresholds, examples, or anti-patterns |
| 5 | Criteria include calibration anchors, scoring rubrics, and known failure modes |

### 3. Boundaries
Does the prompt clearly define what the agent should NOT do, or where its limits are?

| Score | Criteria |
|-------|----------|
| 1 | No boundaries — agent could drift into any territory |
| 2 | Implicit boundaries only |
| 3 | Explicit scope: what the agent does and doesn't handle |
| 4 | Boundaries include handoff triggers — when to escalate |
| 5 | Boundaries include refusal patterns and fallback delegation |

### 4. Schema Alignment
Does the prompt's requested output structure match the actual Python contract model?

| Score | Criteria |
|-------|----------|
| 1 | Prompt asks for fields that don't exist in the contract |
| 2 | Prompt misses major fields present in the contract |
| 3 | Core fields align; some optional fields missing |
| 4 | All contract fields requested; ordering matches model |
| 5 | Prompt includes output format specification that maps 1:1 to contract, with type annotations |

### 5. Context Utilization
Does the prompt effectively use injected context (upstream contracts, metadata)?

| Score | Criteria |
|-------|----------|
| 1 | No context injected — runs blind |
| 2 | Context available but not referenced in prompt |
| 3 | Upstream contracts referenced but not structurally used |
| 4 | Context is structurally incorporated (e.g., referenced in instructions) |
| 5 | Context actively shapes agent behavior with conditional logic per input state |

---

## Category II: Python-Synergy (5 dimensions)

### 6. Prerequisite Gate
Does the Python logic agent check prerequisites before calling the LLM?

| Score | Criteria |
|-------|----------|
| 1 | No prerequisite check — crashes or hallucinates |
| 2 | Checks exist but incomplete |
| 3 | Checks for required contract types before proceeding |
| 4 | Checks include meaningful validation (e.g., at least one scene) |
| 5 | Prerequisite gate includes diagnostic messages per missing contract |

### 7. Fallback Robustness
What happens when the LLM call fails?

| Score | Criteria |
|-------|----------|
| 1 | No fallback — crash or empty result |
| 2 | Returns error but no recovery path |
| 3 | Generic fallback (static defaults) |
| 4 | Context-aware fallback (uses available data to produce reasonable output) |
| 5 | Fallback includes logging, partial recovery, and graceful degradation |

### 8. Normalization
Does the Python layer validate/normalize LLM output into contract structures?

| Score | Criteria |
|-------|----------|
| 1 | Raw LLM output passed through without validation |
| 2 | Minimal type checking only |
| 3 | Field-level validation with error handling |
| 4 | Validation includes range checks, cross-field consistency |
| 5 | Normalization includes repair strategies for malformed output |

### 9. Mapping Accuracy
Do template variables in the prompt correctly match what the Python code provides?

| Score | Criteria |
|-------|----------|
| 1 | Template variable missing from Python context — causes crash |
| 2 | Variable exists but wrong shape/type |
| 3 | Core variables mapped correctly; optional ones missing |
| 4 | All variables mapped; Python provides defaults for missing data |
| 5 | Mapping includes transformation logic, serialization, and null-safety |

### 10. Error Messaging
Are errors from the Python agent informative and actionable?

| Score | Criteria |
|-------|----------|
| 1 | Silent failure or generic exception |
| 2 | Error logged but uninformative |
| 3 | Error message identifies the step and field |
| 4 | Error includes suggested fix or remediation |
| 5 | Errors are machine-parsable and integrated with pipeline diagnostics |

---

## Category III: Cross-Cutting (4 dimensions)

### 11. Fidelity
Does the Python agent faithfully implement what the prompt specifies?

| Score | Criteria |
|-------|----------|
| 1 | Agent ignores or contradicts prompt instructions |
| 2 | Implements prompt partially |
| 3 | Core prompt instructions implemented |
| 4 | Prompt edge cases and qualifications handled |
| 5 | Agent enriches prompt with additional quality checks |

### 12. Handoff / Context Propagation
Does information flow correctly into and out of this agent?

| Score | Criteria |
|-------|----------|
| 1 | No contracts read or written |
| 2 | Contracts read but output ignored downstream |
| 3 | Reads upstream contracts; writes contracts consumed downstream |
| 4 | Explicit handoff validation (output checked before returning) |
| 5 | Handoff includes contract lineage tracking and cross-referencing |

### 13. Constraint Propagation
Are narrative constraints maintained across agent boundaries?

| Score | Criteria |
|-------|----------|
| 1 | Agent violates or ignores upstream constraints |
| 2 | Constraints mentioned but not enforced |
| 3 | Core constraints preserved |
| 4 | Constraints validated before returning |
| 5 | Agent enriches constraint propagation with cross-contract consistency checks |

### 14. Unique Value
Does this agent contribute something the pipeline would miss without it?

| Score | Criteria |
|-------|----------|
| 1 | Redundant — duplicates other agent's work |
| 2 | Partially redundant — some unique, some overlap |
| 3 | Clear unique responsibility |
| 4 | Unique value includes cross-cutting integration not possible elsewhere |
| 5 | Agent provides emergent capability impossible in other agents |

---

## Audit Protocol

For each agent, examine in order:

1. **Python logic agent** (`src/agents/<name>.py`):
   - `execute()` method: prerequisite checks, step routing
   - LLM call: what context is passed, how output is parsed
   - Fallback: what happens on LLM failure
   - Contract I/O: what contracts are read/written

2. **Prompt template** (`src/agents/prompts/<name>.md`):
   - Template variables: are they all provided by the Python code?
   - Output specification: does it match the contract model?
   - Quality standards: are they concrete?
   - Boundaries: are limits defined?

3. **Semantic agent config** (`.opencode/agents/<name>.md`):
   - Model and temperature
   - Permissions (read-only, deny bash/web)
   - System prompt body vs. attached instruction note

---

## Version History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| v1 | 2026-06-08 | OpenCode | Initial framework from pilot audit of 5 agents |
