"""LLM interface — abstract provider with a mock/stub for testing.

In production, swap MockLLMProvider for OpenAILLMProvider or similar.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


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


# ── Mock / Stub ──────────────────────────────────────────────────────────


@dataclass
class MockResponseRule:
    """If user_prompt contains `trigger`, return `response`."""

    trigger: str
    response: str


class MockLLMProvider(LLMProvider):
    """Stub LLM for testing. Returns canned responses by trigger matching."""

    def __init__(self, fallback: str = "Mock LLM response.") -> None:
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

        for rule in self.rules:
            if rule.trigger in user_prompt or rule.trigger in system_prompt:
                return LLMResponse(content=rule.response, tokens_used=len(rule.response))

        return LLMResponse(content=self.fallback, tokens_used=len(self.fallback))


# ── Singleton ────────────────────────────────────────────────────────────

_provider: LLMProvider | None = None


def get_llm() -> LLMProvider:
    global _provider
    if _provider is None:
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
