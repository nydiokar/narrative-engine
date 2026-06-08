"""LLM interface — abstract provider, mock/stub for testing, and real provider.

The real provider uses the OpenAI-compatible API and can talk to any
OpenAI-compatible endpoint (OpenAI, Azure, Ollama, opencode's own LLM, etc.)

Environment variables:
    LLM_API_KEY       — API key (default: "ollama" for local use)
    LLM_BASE_URL      — Base URL (default: http://localhost:11434/v1 for Ollama)
    LLM_MODEL         — Model name (default: llama3.2)
    LLM_MAX_TOKENS    — Max tokens per call (default: 4096)
    LLM_TEMPERATURE   — Temperature (default: 0.7)
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class LLMResponse:
    content: str
    raw: dict[str, Any] | None = None
    tokens_used: int = 0


class LLMProvider(ABC):
    """Abstract LLM interface. All agents call llm.generate() — never directly."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        ...


# ── Real Provider (OpenAI-compatible) ────────────────────────────────────


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
    ) -> LLMResponse:
        temp = temperature if temperature is not None else self.temperature
        mt = max_tokens if max_tokens is not None else self.max_tokens

        self.call_log.append({
            "model": self.model,
            "system": system_prompt[:200],
            "user": user_prompt[:200],
            "temperature": temp,
            "max_tokens": mt,
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


# ── Subprocess Provider (agent-agnostic CLI harness) ────────────────────


class SubprocessLLMProvider(LLMProvider):
    """Calls any CLI command instead of an LLM API.

    The command receives prompts via temp files and produces JSON output
    via stdout or a temp file. This is agent-agnostic — swap in opencode,
    ollama, a custom agent script, etc.

    Environment variables (set LLM_SUBPROCESS_CMD to activate):
        LLM_SUBPROCESS_CMD — CLI command template with placeholders:
            {system_file}  — path to temp file with system prompt
            {user_file}    — path to temp file with user prompt
            {output_file}  — path to output file (agent writes JSON here)
        LLM_SUBPROCESS_TIMEOUT — timeout in seconds (default: 300)

    Example commands:
      opencode:  opencode run --file {user_file} --format json --dangerously-skip-permissions
                 "Read the attached file. Produce ONLY a JSON object and write it to {output_file}"
      ollama:    ollama run gemma3:12b < {user_file} > {output_file}
      custom:    python agent_script.py --system {system_file} --user {user_file} --output {output_file}
    """

    def __init__(self, cmd_template: str | None = None) -> None:
        import shutil

        self.cmd_template = (
            cmd_template
            or os.getenv("LLM_SUBPROCESS_CMD", "")
        )
        if not self.cmd_template:
            msg = "LLM_SUBPROCESS_CMD not set — provide a command template or set the env var"
            raise ValueError(msg)
        self.timeout = int(os.getenv("LLM_SUBPROCESS_TIMEOUT", "300"))
        self.call_log: list[dict[str, Any]] = []

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        import subprocess
        import tempfile
        import os

        # Write prompts to temp files
        sf = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
        sf.write(system_prompt)
        sf.close()
        uf = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
        uf.write(user_prompt)
        uf.close()
        of = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        of.close()

        cmd = self.cmd_template.format(
            system_file=sf.name,
            user_file=uf.name,
            output_file=of.name,
        )

        self.call_log.append({
            "cmd": cmd,
            "system_file": sf.name,
            "user_file": uf.name,
            "output_file": of.name,
            "temperature": temperature,
            "max_tokens": max_tokens,
        })

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            stdout_content = result.stdout or ""
            stderr_content = result.stderr or ""
        except subprocess.TimeoutExpired:
            stdout_content = ""
            stderr_content = "TIMEOUT"

        # Prefer output file, fall back to stdout
        content = ""
        if os.path.exists(of.name):
            with open(of.name, "r", encoding="utf-8") as f:
                content = f.read()
            os.unlink(of.name)
        if not content and stdout_content:
            content = stdout_content

        # Cleanup temp files
        for p in (sf.name, uf.name):
            if os.path.exists(p):
                os.unlink(p)

        if not content:
            content = json.dumps({
                "success": False,
                "message": "Subprocess produced no output",
                "errors": [stderr_content or "No output from subprocess"],
                "artifacts": [],
            })

        return LLMResponse(content=content, tokens_used=len(content))



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


# ── Singleton ────────────────────────────────────────────────────────────

_provider: LLMProvider | None = None


def get_llm() -> LLMProvider:
    global _provider
    if _provider is None:
        if os.getenv("LLM_SUBPROCESS_CMD"):
            _provider = SubprocessLLMProvider()
        elif os.getenv("LLM_BASE_URL") or os.getenv("LLM_API_KEY"):
            _provider = OpenAILLMProvider()
        else:
            _provider = MockLLMProvider(
                fallback='{"success": true, "message": "Mock response", "errors": [], "artifacts": []}'
            )
    return _provider


def set_llm(provider: LLMProvider) -> None:
    global _provider
    _provider = provider


def reset_llm() -> None:
    global _provider
    _provider = None
