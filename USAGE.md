# Narrative Engine — User Manual

## Quick Start

```bash
# Run full pipeline with mock LLM (no API key needed)
python -m src run

# Run with a real LLM
python -m src run --model qwen3-coder

# Run to a specific checkpoint, save state
python -m src run --to premise --save my_story.json
```

## Commands

### `python -m src run` — Run pipeline

```
python -m src run [--to CHECKPOINT] [--model NAME] [--medium TYPE]
                  [--premise TEXT] [--load PATH] [--save PATH]
                  [--lock TYPE[.FIELD][,TYPE[.FIELD]...]]
                  [--set TYPE.FIELD=VALUE]
```

| Flag | Default | Description |
|:-----|:--------|:------------|
| `--to` | `final` | Stop at this checkpoint |
| `--model` | (mock) | LLM model (implies real LLM) |
| `--medium` | `book` | Output medium: `book`, `animation`, `movie`, `series` |
| `--premise` | (default) | Custom premise string |
| `--load PATH` | — | Load previously saved state |
| `--save PATH` | — | Save state after run |
| `--lock TYPE[.FIELD]` | — | Lock contract types or specific fields (comma-separated) |
| `--set TYPE.FIELD=VALUE` | — | Set a contract field before running |

**Checkpoints (in order):** `brief` → `premise` → `structure` → `episodes` → `scenes` → `draft` → `editorial` → `final`

**Examples:**
```bash
# Stop after genre and theme are set
python -m src run --to brief

# Custom premise, real LLM, animation medium
python -m src run --to structure --model qwen3-coder --medium animation \
    --premise "A robot in a zombie apocalypse"

# Load saved state, lock story, continue
python -m src run --to episodes --load my_story.json --lock story

# Set a field and lock it to prevent pipeline from overwriting
python -m src run --to premise --set story.genre.primary_bisac=FIC042000 --lock story.genre
```

---

### `python -m src branch` — Create variants

```
python -m src branch --vary FIELD --values LIST [--from CP] [--to CP]
                     [--model NAME] [--medium TYPE]
                     [--tree-load PATH] [--tree-save PATH]
                     [--lock TYPE[.FIELD]]
                     [--set TYPE.FIELD=VALUE]
```

| Flag | Default | Description |
|:-----|:--------|:------------|
| `--vary` | `genre` | What to vary: `genre`, `world`, `premise`, `tone`, `character` |
| `--values` | required | Comma-separated values to try |
| `--from` | auto | Checkpoint to branch from (auto-detected from `--vary`) |
| `--to` | `final` | Run pipeline to this checkpoint for each variant |
| `--labels` | values | Human-readable labels for variants |
| `--model` | (mock) | LLM model |
| `--tree-load` | — | Load existing tree state |
| `--tree-save` | — | Save tree state after branch |
| `--lock TYPE[.FIELD]` | — | Lock contract types or specific fields in variant stores |
| `--set TYPE.FIELD=VALUE` | — | Set a contract field before branching |

**Auto-detected `--from` checkpoints by vary field:**

| Vary field | Re-runs from | Pipeline stages |
|:-----------|:-------------|:----------------|
| `genre` | `brief` | WF 00-01 (theme, premise) |
| `tone` | `brief` | WF 00-01 |
| `premise` | `premise` | WF 01-07 |
| `world` | `structure` | WF 02-07 |
| `character` | `episodes` | WF 03-07 |
| `seed` | `brief` | WF 00-07 |

**Examples:**
```bash
# Branch 3 genres from a frozen premise
python -m src branch --vary genre --values fantasy,scifi,horror \
    --tree-save tree.json

# Branch with world variant, stop at episodes to compare
python -m src branch --vary world --values "high,dark,urban" \
    --to episodes --labels "worldA,worldB,worldC" \
    --tree-save tree.json
```

---

### `python -m src compare` — Compare variants

```
python -m src compare --labels LABEL[,LABEL...] --tree-load PATH
```

Compare key contract data across siblings: genre, protagonist, world, scores.

**Example:**
```bash
python -m src compare --labels fantasy-v1,scifi-v1,horror-v1 \
    --tree-load tree.json
```

---

### `python -m src promote` — Activate a variant

```
python -m src promote LABEL --tree-load PATH [--tree-save PATH]
```

Mark a variant as the active path for continued branching.

**Example:**
```bash
python -m src promote fantasy-v1 --tree-load tree.json --tree-save tree.json
```

---

### `python -m src prune` — Delete tree nodes

```
python -m src prune LABEL --tree-load PATH [--tree-save PATH]
```

Remove a node and all its descendants from the tree. If the active node is pruned, the nearest ancestor becomes active.

**Example:**
```bash
python -m src prune fantasy-v1 --tree-load tree.json --tree-save tree.json
```

---

### `python -m src show` — Display tree as ASCII art

```
python -m src show --tree-load PATH
```

Print the tree structure with node labels, checkpoints, depths, and active markers.

**Example:**
```bash
python -m src show --tree-load tree.json
```

Output:
```
+-- (root)
    |-- (fantasy-v1) @premise d=1
    |   |-- (world-high) @structure d=2
    |   +-- (world-dark) @structure d=2 [active]
    +-- (scifi-v1) @premise d=1
```

---

### `python -m src set` — Manually set contract fields

```
python -m src set TYPE.FIELD=VALUE [TYPE.FIELD=VALUE ...] [--lock true] [--load PATH] [--save PATH]
```

Set contract fields directly and optionally lock them. Nested fields use dot notation.

**Examples:**
```bash
# Set genre on an existing story
python -m src set story.genre.primary_bisac=FIC042000 --load pipeline.json --save pipeline.json

# Set and lock in one step
python -m src set story.premise="Custom premise" --lock true --load pipeline.json

# Set multiple fields
python -m src set story.title="New Title" story.premise="New premise" --save pipeline.json
```

---

### `python -m src lock` — Freeze contracts or fields

```
python -m src lock TYPE[.FIELD] [TYPE[.FIELD] ...] [--load PATH] [--save PATH]
```

Lock contract types or specific fields so workflows skip/respect them. Dotted paths lock individual fields while plain types lock entire contracts.

**Available types:**
`story`, `theme`, `character`, `world`, `episode`, `chapter`, `scene`, `discourse`, `critique`

**How locks work:**
- **Contract-level lock** (`story`): All fields of every story contract are frozen. Any workflow whose EXISTING output types are ALL locked is skipped entirely.
- **Field-level lock** (`story.genre`): Only the specified field is frozen. Other fields on the same contract can still change. Field-level locks do NOT trigger workflow skipping.
- Locked fields that haven't been set yet are not preserved (they can still be set for the first time).
- Locking a parent path (e.g. `story.genre`) also locks all sub-fields (`story.genre.primary_bisac`).

**Examples:**
```bash
# Lock entire story and theme contracts
python -m src lock story theme --load pipeline.json --save pipeline.json

# Lock only the genre field of story contracts
python -m src lock story.genre --load pipeline.json --save pipeline.json

# Lock everything up to structure (proceed from episodes)
python -m src lock story theme character world episode --load pipeline.json

# Set and lock in one command
python -m src run --to premise --set story.genre.primary_bisac=FIC042000 --lock story.genre
```

---

### `python -m src unlock` — Unfreeze contracts or fields

```
python -m src unlock TYPE[.FIELD] [TYPE[.FIELD] ...] [--load PATH] [--save PATH]
```

**Examples:**
```bash
python -m src unlock story --load pipeline.json --save pipeline.json
python -m src unlock story.genre --load pipeline.json --save pipeline.json
```

---

## Workflows

### Linear pipeline (evaluate one path)

```bash
# Step through each checkpoint
python -m src run --to brief
python -m src run --to premise --save state.json
python -m src run --to structure --load state.json --save state.json
python -m src run --to episodes --load state.json --save state.json
# ...continue to final
```

### Tree exploration (try variants, pick best)

```bash
# 1. Run to a checkpoint and freeze
python -m src run --to premise --save trunk.json --lock story

# 2. Branch 3 genres from the premise
python -m src run --load trunk.json \
    branch --vary genre --values fantasy,scifi,horror \
    --to structure --tree-save tree.json

# 3. Compare variants
python -m src compare --labels fantasy-v1,scifi-v1,horror-v1 \
    --tree-load tree.json

# 4. Promote the best one
python -m src promote fantasy-v1 --tree-load tree.json --tree-save tree.json

# 5. Branch deeper with world variants
python -m src branch --vary world \
    --values "high-fantasy,dark-fantasy" \
    --tree-load tree.json --tree-save tree.json

# 6. Continue to final on the chosen path
python -m src compare --labels "worldA,worldB" --tree-load tree.json
python -m src promote worldA --tree-load tree.json --tree-save tree.json
```

### Lock-and-continue (freeze decisions, regenerate only what's new)

```bash
# 1. Pipeline generates premise, you review and approve
python -m src run --to premise --save story.json

# 2. Lock the story contract (genre, premise, actants are final)
python -m src lock story theme --load story.json --save story.json

# 3. Continue to structure → only WF 02 runs, WF 00-01 skip
python -m src run --to structure --load story.json

# 4. Lock structure, continue to episodes
python -m src lock world --load story.json --save story.json
python -m src run --to episodes --load story.json
```

---

## Key Concepts

### Pipeline Stages (depth levels)

| Depth | Stage | What's produced | Vary field |
|:-----:|:------|:----------------|:-----------|
| 0 | **Brief** | Genre, theme, world axes, character layers | `genre`, `tone` |
| 1 | **Premise** | Actants, protagonist, backbone grammar | `premise` |
| 2 | **Structure** | Fabula, world architecture | `world` |
| 3 | **Episodes** | Episodes, chapters, conflict arcs | `character`, `conflict` |
| 4 | **Scenes** | 24 scene sequence, Greimas diagnostics | — |
| 5 | **Draft** | Full draft assembled | — |
| 6 | **Editorial** | Line/copy/proofreading passes | — |
| 7 | **Final** | Hard gate + soft gate pass, approval | — |

### Lock Protocol

The lock system lets you freeze decisions so the pipeline respects them:

- **`lock story`** — prevents any agent from overwriting any story field; workflows whose outputs are all story are skipped
- **`lock story.genre`** — only the genre field is frozen; other story fields (premise, title) can still change
- **`lock theme`** — prevents theme regeneration
- **`lock character`** — character profiles are final
- **Skip propagation** — if all existing outputs of a workflow are locked (contract-level), the entire workflow is skipped
- **Field-level locks** do NOT trigger workflow skipping — only contract-level locks do

This means you can:
1. Run to `brief`, review the genre/theme → lock story and theme
2. Run to `premise` → WF 00 skips, WF 01 runs → new character, premise analysis
3. Review → lock character
4. Run to `structure` → WF 00-01 skip, WF 02 runs → new world architecture
5. And so on — each step only generates the *missing* pieces

**Field-level locking example:**
```bash
# Run pipeline, set a custom genre, lock just the genre field
python -m src run --to premise --set story.genre.primary_bisac=FIC042000 --lock story.genre

# The pipeline continues to structure; genre stays frozen at FIC042000
# but other story fields (premise, actants) can still be updated
python -m src run --to structure --load pipeline.json
```

### Tree Concepts

| Term | Meaning |
|:-----|:--------|
| **Node** | A frozen story state (ContractStore snapshot) |
| **Root** | The initial seed state (story contract only) |
| **Child** | A variant branched from a parent node |
| **Sibling** | Variants at the same depth (same parent) |
| **Active** | The current path for continued branching |
| **Branch** | Create N children with different variant params |
| **Promote** | Mark one child as active |
| **Compare** | View siblings side-by-side |
| **Store snapshot** | Serialized ContractStore at a point in time |

---

## Environment Variables

| Variable | Default | Description |
|:---------|:--------|:------------|
| `LLM_BASE_URL` | `http://localhost:11434/v1` | API base URL |
| `LLM_API_KEY` | `ollama` | API key |
| `LLM_MODEL` | `llama3.2` | Default model name |
| `LLM_TEMPERATURE` | `0.7` | LLM temperature |
| `LLM_MAX_TOKENS` | `4096` | Max tokens per response |

---

## File Formats

### Pipeline state (JSON)
Saved with `--save`, loaded with `--load`. Contains all contracts with their version history and lock state. Compatible across checkpoints — you can save at `premise`, load at `scenes`, etc.

### Tree state (JSON)
Saved with `--tree-save`, loaded with `--tree-load`. Contains the full tree structure: nodes, parent/child links, variant params, scores, and store snapshots per node.
