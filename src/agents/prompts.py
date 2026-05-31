"""Prompt engine — loads role card templates and renders them with context."""

from pathlib import Path
from typing import Any

import yaml

PROMPTS_DIR = Path(__file__).parent / "prompts"

AGENT_PROMPT_FILES: dict[str, str] = {
    "showrunner": "showrunner.md",
    "structuralist": "structuralist.md",
    "character_architect": "character_architect.md",
    "outline_planner": "outline_planner.md",
    "scene_writer": "scene_writer.md",
    "critic": "critic.md",
}

_cache: dict[str, str] = {}


def load_prompt(agent_name: str) -> str:
    """Read the prompt template for the given agent name."""
    if agent_name in _cache:
        return _cache[agent_name]

    filename = AGENT_PROMPT_FILES.get(agent_name)
    if not filename:
        msg = f"No prompt template for agent: {agent_name}"
        raise ValueError(msg)

    path = PROMPTS_DIR / filename
    if not path.exists():
        msg = f"Prompt file not found: {path}"
        raise FileNotFoundError(msg)

    content = path.read_text(encoding="utf-8")
    _cache[agent_name] = content
    return content


def render_system_prompt(agent_name: str, **extra: Any) -> str:
    """Load and render the system prompt with injected context."""
    template = load_prompt(agent_name)
    return template.format(**extra)


def render_user_prompt(
    step_id: str,
    upstream_yaml: str,
    agent_name: str = "",
    medium: str = "book",
) -> str:
    """Build a step-specific user prompt with upstream contract context."""
    parts = [f"Current step: {step_id}"]
    if agent_name:
        parts.append(f"Agent: {agent_name}")
    parts.append(f"Medium: {medium}")
    if upstream_yaml:
        parts.append("\nUpstream contracts available:\n" + upstream_yaml)
    parts.append(
        '\nProduce your output as a single JSON object with the fields '
        'specified in the "Output" section of your role definition.'
    )
    return "\n\n".join(parts)


def contracts_to_yaml(contracts: list[Any], max_chars: int = 4000) -> str:
    """Serialize a list of contracts to a condensed YAML string for prompt injection."""
    items = []
    for c in contracts:
        d = c.model_dump(mode="json") if hasattr(c, "model_dump") else {}
        items.append(d)

    # Limit output size to avoid blowing context
    raw = yaml.dump(items, default_flow_style=False, sort_keys=False)
    if len(raw) > max_chars:
        raw = raw[:max_chars] + "\n# ... [truncated]"
    return raw


def parse_json_output(raw: str) -> dict[str, Any]:
    """Extract and parse JSON from LLM output (handles markdown code fences)."""
    cleaned = raw.strip()

    # Strip markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        start = 0
        for i, line in enumerate(lines):
            if line.startswith("```"):
                start = i + 1
                break
        end = len(lines)
        for i in range(len(lines) - 1, start - 1, -1):
            if lines[i].startswith("```"):
                end = i
                break
        cleaned = "\n".join(lines[start:end]).strip()

    import json
    return json.loads(cleaned)
