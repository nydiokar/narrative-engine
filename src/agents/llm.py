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


# ── Mock / Stub ──────────────────────────────────────────────────────────


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
        if os.getenv("LLM_BASE_URL") or os.getenv("LLM_API_KEY"):
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
