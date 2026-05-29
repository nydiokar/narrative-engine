# Workflow 01: Human Intake

**Goal**: Capture the raw premise, authorial intent, and constraints from the human user.

## Steps

1. **Present Intake Form**
   - Use `templates/human-intake.yaml`
   - Collect: premise, genre, tone, target audience, constraints, reference works

2. **Validate Input**
   - Ensure premise is non-empty and coherent
   - Check genre is in the Genre Map (`research/genre-map.md`)
   - Flag contradictory constraints

3. **Produce Intake Document**
   - Store in `stories/<story-name>/intake.yaml`
   - Pass to Director agent

## Output
- Completed `intake.yaml`
- Ready for Workflow 02
