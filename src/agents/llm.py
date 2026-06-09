"""LLM interface — abstract provider, mock/stub for testing, and real providers.

Architecture:
  Python Agent (logic) → LLMProvider (abstraction) → Backend (concrete)

Three providers:
  - OpenAILLMProvider   — OpenAI-compatible HTTP API (Ollama, OpenAI, etc.)
  - SubprocessLLMProvider — CLI subprocess (opencode run, custom scripts)
  - MockLLMProvider     — canned responses for testing

Environment variables:
  LLM_API_KEY            — API key (default: "ollama" for local use)
  LLM_BASE_URL           — Base URL (default: http://localhost:11434/v1 for Ollama)
  LLM_MODEL              — Model name (default: llama3.2)
  LLM_MAX_TOKENS         — Max tokens per call (default: 4096)
  LLM_TEMPERATURE        — Temperature (default: 0.7)
  LLM_SUBPROCESS_CMD     — CLI command template for SubprocessLLMProvider
  LLM_SUBPROCESS_TIMEOUT — Timeout in seconds (default: 300)
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


# ── Role name mapping: Python snake_case → OpenCode kebab-case ──────

_ROLE_TO_SEMANTIC_AGENT: dict[str, str] = {
    "showrunner": "showrunner",
    "structuralist": "structuralist",
    "character_architect": "character-architect",
    "character_simulator": "character-simulator",
    "theme_specialist": "theme-specialist",
    "world_researcher": "world-researcher",
    "outline_planner": "outline-planner",
    "chapter_planner": "chapter-planner",
    "scene_writer": "scene-writer",
    "continuity_editor": "continuity-editor",
    "copy_editor": "copy-editor",
    "developmental_editor": "developmental-editor",
    "line_editor": "line-editor",
    "proofreader": "proofreader",
    "revision_agent": "revision-agent",
    "script_editor": "script-editor",
    "dialogue_specialist": "dialogue-specialist",
    "critic": "critic",
}


def role_to_semantic_agent(role: str) -> str:
    """Map Python agent role name to OpenCode semantic agent filename (kebab-case)."""
    return _ROLE_TO_SEMANTIC_AGENT.get(role, role.replace("_", "-"))


# ── Data classes ─────────────────────────────────────────────────────


@dataclass
class LLMResponse:
    content: str
    raw: dict[str, Any] | None = None
    tokens_used: int = 0


@dataclass
class GenerationContext:
    """Context passed from the logic agent to the LLM provider.

    The provider uses this to select the correct backend agent config,
    create run directories, and log execution metadata.
    """

    agent_role: str = ""
    step_id: str = ""
    workflow_id: str = ""
    medium: str = "book"


# ── Abstract provider ────────────────────────────────────────────────


class LLMProvider(ABC):
    """Abstract LLM interface. All agents call llm.generate() — never directly."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        context: GenerationContext | None = None,
        timeout: int | None = None,
    ) -> LLMResponse:
        ...


# ── OpenAI-compatible provider ───────────────────────────────────────


class OpenAILLMProvider(LLMProvider):
    """OpenAI-compatible LLM provider.

    Works with OpenAI, Azure OpenAI, Ollama, any OpenAI-compatible API.
    Configured via environment variables (see module docstring).
    """

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> None:
        from openai import OpenAI

        self.model = model or os.getenv("LLM_MODEL", "llama3.2")
        api_key = api_key or os.getenv("LLM_API_KEY", "ollama")
        base_url = base_url or os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        self.max_tokens = max_tokens or int(os.getenv("LLM_MAX_TOKENS", "4096"))
        self.temperature = temperature or float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.call_log: list[dict[str, Any]] = []

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
        context: GenerationContext | None = None,
        timeout: int | None = None,
    ) -> LLMResponse:
        temp = temperature if temperature is not None else self.temperature
        mt = max_tokens if max_tokens is not None else self.max_tokens

        self.call_log.append({
            "model": self.model,
            "system": system_prompt[:200],
            "user": user_prompt[:200],
            "temperature": temp,
            "max_tokens": mt,
            "context": {
                "role": context.agent_role if context else None,
                "step": context.step_id if context else None,
            },
        })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temp,
            max_tokens=mt,
        )

        content = response.choices[0].message.content or ""
        raw = response.model_dump() if hasattr(response, "model_dump") else {}
        return LLMResponse(
            content=content,
            raw=raw,
            tokens_used=response.usage.total_tokens if response.usage else 0,
        )


# ── Subprocess provider (OpenCode / CLI backend) ────────────────────


class SubprocessLLMProvider(LLMProvider):
    """Calls a CLI command instead of an LLM API, with run directory isolation.

    Each call creates an isolated run directory:
      runs/{run_id}/step_{step_id}/
        task.md              — instruction for the agent
        input/
          system_prompt.md   — system prompt
          context.json       — upstream contract context
          schema.json        — expected output schema
        output/
          result.json        — agent writes its output here
        logs/
          stdout.txt         — captured stdout
          stderr.txt         — captured stderr
          metadata.json      — call metadata

    The command template supports these placeholders:
      {system_file}  — path to system prompt file
      {user_file}    — path to user prompt / task file
      {output_file}  — path where agent should write JSON output
      {run_dir}      — path to the run step directory

    Default command (set LLM_SUBPROCESS_CMD to override):
      opencode run --dir {run_dir} --agent {agent} --file {user_file} --format json
        "Execute the task in task.md. Write JSON output to {output_file}."
    """

    _run_counter: int = 0

    def __init__(self, cmd_template: str | None = None) -> None:
        self.cmd_template = (
            cmd_template
            or os.getenv("LLM_SUBPROCESS_CMD", "")
        )
        if not self.cmd_template:
            self.cmd_template = (
                "opencode run --dir {run_dir} --agent {agent} "
                "--file {system_file} --file {user_file} --format json "
                '"Read the system prompt in {system_file} for your role. '
                'Execute the task in {user_file}. '
                'Write ONLY valid JSON to {output_file}."'
            )
        self.timeout = int(os.getenv("LLM_SUBPROCESS_TIMEOUT", "300"))
        self.runs_root = Path(os.getenv("LLM_RUNS_DIR", "runs"))
        self.call_log: list[dict[str, Any]] = []

    @classmethod
    def _next_run_id(cls) -> str:
        cls._run_counter += 1
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"run_{now}_{cls._run_counter:03d}"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        context: GenerationContext | None = None,
        timeout: int | None = None,
    ) -> LLMResponse:
        import subprocess as _subprocess

        agent_role = context.agent_role if context else "unknown"
        semantic_agent = role_to_semantic_agent(agent_role)
        step_id = context.step_id if context else "unknown"
        workflow_id = context.workflow_id if context else "unknown"
        medium = context.medium if context else "book"

        # Create run step directory
        run_id = self._next_run_id()
        run_dir = self.runs_root / run_id / f"step_{step_id}"
        input_dir = run_dir / "input"
        output_dir = run_dir / "output"
        logs_dir = run_dir / "logs"

        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Write task.md (user prompt is the instruction)
        task_path = run_dir / "task.md"
        task_path.write_text(user_prompt, encoding="utf-8")

        # Write system prompt
        sys_path = input_dir / "system_prompt.md"
        sys_path.write_text(system_prompt, encoding="utf-8")

        # Write metadata about the call
        meta = {
            "timestamp": datetime.now().isoformat(),
            "agent_role": agent_role,
            "semantic_agent": semantic_agent,
            "workflow_id": workflow_id,
            "step_id": step_id,
            "medium": medium,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        (input_dir / "call_metadata.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )

        # Output file
        output_path = output_dir / "result.json"

        # Build command
        placeholders = {
            "system_file": str(sys_path),
            "user_file": str(task_path),
            "output_file": str(output_path),
            "run_dir": str(run_dir),
            "agent": semantic_agent,
        }
        cmd = self.cmd_template.format(**placeholders)

        effective_timeout = timeout if timeout is not None else self.timeout

        self.call_log.append({
            "cmd": cmd,
            "run_dir": str(run_dir),
            "agent": semantic_agent,
            "step_id": step_id,
            "timeout": effective_timeout,
            "temperature": temperature,
            "max_tokens": max_tokens,
        })

        # Execute
        try:
            result = _subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=effective_timeout,
            )
            stdout_content = result.stdout or ""
            stderr_content = result.stderr or ""
        except _subprocess.TimeoutExpired:
            stdout_content = ""
            stderr_content = f"TIMEOUT after {effective_timeout}s"
        except OSError as _os_err:
            stdout_content = ""
            stderr_content = f"OS error: {_os_err}"

        # Save logs
        (logs_dir / "stdout.txt").write_text(stdout_content, encoding="utf-8")
        (logs_dir / "stderr.txt").write_text(stderr_content, encoding="utf-8")
        (logs_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        # Read output: prefer output/result.json, fall back to stdout
        content = ""
        if output_path.exists():
            content = output_path.read_text(encoding="utf-8")
        if not content and stdout_content:
            content = stdout_content

        if not content:
            content = json.dumps({
                "success": False,
                "message": "Subprocess produced no output",
                "errors": [stderr_content or "No output from subprocess"],
                "artifacts": [],
            })

        return LLMResponse(content=content, tokens_used=len(content))


# ── Mock provider (testing) ──────────────────────────────────────────


@dataclass
class MockResponseRule:
    """If user_prompt contains `trigger`, return `response`."""

    trigger: str
    response: str


class MockLLMProvider(LLMProvider):
    """Stub LLM for testing. Returns canned responses by trigger matching."""

    def __init__(self, fallback: str = '{"success": true, "message": "Mock response", "errors": [], "artifacts": []}') -> None:
        self.rules: list[MockResponseRule] = []
        self.call_log: list[dict[str, Any]] = []
        self.fallback = fallback

    def add_rule(self, trigger: str, response: str) -> None:
        self.rules.append(MockResponseRule(trigger=trigger, response=response))

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        context: GenerationContext | None = None,
        timeout: int | None = None,
    ) -> LLMResponse:
        self.call_log.append({
            "system": system_prompt,
            "user": user_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        })

        combined = user_prompt + "\n" + system_prompt
        for rule in self.rules:
            if rule.trigger in combined:
                return LLMResponse(content=rule.response, tokens_used=len(rule.response))

            # Also try matching agent.step against Current step / Agent lines
            if "." in rule.trigger:
                agent_part, step_part = rule.trigger.split(".", 1)
                if f"Agent: {agent_part}" in user_prompt and f"step: {step_part}" in user_prompt:
                    return LLMResponse(content=rule.response, tokens_used=len(rule.response))

        return LLMResponse(content=self.fallback, tokens_used=len(self.fallback))


# ── Singleton ────────────────────────────────────────────────────────

_PROVIDER_TYPE: str | None = None
_provider: LLMProvider | None = None


def get_llm() -> LLMProvider:
    global _provider
    if _provider is None:
        provider_type = _PROVIDER_TYPE or os.getenv("LLM_PROVIDER", "auto")
        if provider_type == "opencode":
            _provider = SubprocessLLMProvider()
        elif provider_type == "openai":
            _provider = OpenAILLMProvider()
        elif provider_type == "mock":
            _provider = MockLLMProvider(
                fallback='{"success": true, "message": "Mock response", "errors": [], "artifacts": []}'
            )
        elif provider_type == "auto":
            if os.getenv("LLM_SUBPROCESS_CMD") or os.getenv("LLM_PROVIDER") == "opencode":
                _provider = SubprocessLLMProvider()
            elif os.getenv("LLM_BASE_URL") or os.getenv("LLM_API_KEY"):
                _provider = OpenAILLMProvider()
            else:
                _provider = MockLLMProvider(
                    fallback='{"success": true, "message": "Mock response", "errors": [], "artifacts": []}'
                )
        else:
            msg = f"Unknown provider type: {provider_type}. Use 'opencode', 'openai', or 'mock'."
            raise ValueError(msg)
    return _provider


def set_llm(provider: LLMProvider, provider_type: str | None = None) -> None:
    global _provider, _PROVIDER_TYPE
    _provider = provider
    if provider_type:
        _PROVIDER_TYPE = provider_type


def set_provider_type(provider_type: str) -> None:
    """Set the provider type for the next get_llm() call.

    Args:
        provider_type: One of "opencode", "openai", "mock", "auto".
    """
    global _PROVIDER_TYPE, _provider
    _PROVIDER_TYPE = provider_type
    _provider = None  # Force re-creation on next get_llm()


def reset_llm() -> None:
    global _provider, _PROVIDER_TYPE
    _provider = None
    _PROVIDER_TYPE = None
