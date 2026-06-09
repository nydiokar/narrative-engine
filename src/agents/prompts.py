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
    "script_editor": "script_editor.md",
    "theme_specialist": "theme_specialist.md",
    "world_researcher": "world_researcher.md",

    "chapter_planner": "chapter_planner.md",
    "character_simulator": "character_simulator.md",
    "dialogue_specialist": "dialogue_specialist.md",
    "developmental_editor": "developmental_editor.md",
    "line_editor": "line_editor.md",
    "copy_editor": "copy_editor.md",
    "proofreader": "proofreader.md",
    "revision_agent": "revision_agent.md",
    "continuity_editor": "continuity_editor.md",
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
    **extra: Any,
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
    """Extract and parse JSON from LLM output (handles real-LLM failure modes).

    Resilience chain:
    1. Strip markdown code fences (```json ... ```, etc.)
    2. Extract first JSON object/array boundary — ignores prefix/suffix text
    3. Fix trailing commas before ] or }
    4. Replace single quotes with double quotes for keys
    5. Try multiple fallback JSON decoders
    6. Never crash — return a dict with success=False on total failure
    """
    import json as _json
    import re as _re

    text = raw.strip()

    # ── Step 1: Strip markdown code fences ──────────────────────────
    if "```" in text:
        lines = text.splitlines()
        fence_starts = [i for i, line in enumerate(lines) if line.strip().startswith("```")]
        if fence_starts:
            start = fence_starts[0] + 1
            end = fence_starts[-1] if len(fence_starts) > 1 else len(lines)
            text = "\n".join(lines[start:end]).strip()

    # ── Step 2: Extract first JSON object or array ──────────────────
    def _find_json_boundary(s: str) -> str | None:
        for open_char, close_char in [("{", "}"), ("[", "]")]:
            start = s.find(open_char)
            if start == -1:
                continue
            depth = 0
            in_str = False
            escape = False
            for i in range(start, len(s)):
                ch = s[i]
                if escape:
                    escape = False
                    continue
                if ch == "\\":
                    escape = True
                    continue
                if ch == '"':
                    in_str = not in_str
                    continue
                if in_str:
                    continue
                if ch == open_char:
                    depth += 1
                elif ch == close_char:
                    depth -= 1
                    if depth == 0:
                        return s[start:i+1]
        return None

    boundary = _find_json_boundary(text)
    if boundary:
        text = boundary

    # ── Step 3: Fix trailing commas ─────────────────────────────────
    text = _re.sub(r",\s*([}\]])", r"\1", text)

    # ── Step 4: Try common JSON repairs ─────────────────────────────
    def _try_parse(s: str) -> dict | list | None:
        try:
            return _json.loads(s)
        except _json.JSONDecodeError:
            pass

        # Try replacing single quotes with double quotes (for keys)
        try:
            # Replace single-quoted keys/values with double-quoted
            fixed = _re.sub(r"'([^']*)'", r'"\1"', s)
            return _json.loads(fixed)
        except (_json.JSONDecodeError, _re.error):
            pass

        # Try basic Python literal eval for dicts/lists
        if s.startswith("{") or s.startswith("["):
            try:
                import ast
                return ast.literal_eval(s)
            except (ValueError, SyntaxError, MemoryError):
                pass

        return None

    result = _try_parse(text)
    if result is not None:
        if isinstance(result, list):
            return {"contracts_data": result, "success": True, "message": "Parsed array output", "errors": [], "artifacts": []}
        if isinstance(result, dict):
            return result

    # ── Step 5: Last resort — extract key-value pairs via regex ────
    extracted: dict[str, Any] = {}
    try:
        kv_pattern = _re.compile(r'"(\w+)":\s*"([^"]*)"')
        for match in kv_pattern.finditer(raw):
            extracted[match.group(1)] = match.group(2)
    except (_re.error, Exception):
        pass

    if extracted:
        return {
            "success": True,
            "message": "Partially parsed from LLM output (regex extraction)",
            "errors": [f"Raw output truncated: {raw[:300]}"],
            "artifacts": [],
            **extracted,
        }

    return {
        "success": False,
        "message": "No valid JSON found in LLM output",
        "errors": [f"Raw output: {raw[:500]}"],
        "artifacts": [],
    }
