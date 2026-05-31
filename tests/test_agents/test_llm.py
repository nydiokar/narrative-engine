"""Tests for the LLM provider interface and mock."""

import pytest

from src.agents.llm import (
    LLMResponse,
    MockLLMProvider,
    get_llm,
    reset_llm,
    set_llm,
)


class TestMockLLMProvider:
    def setup_method(self):
        reset_llm()

    def test_canned_response(self):
        llm = MockLLMProvider()
        llm.add_rule("analyze", "Analysis result")
        response = llm.generate("System", "Please analyze this premise")
        assert response.content == "Analysis result"

    def test_fallback_response(self):
        llm = MockLLMProvider(fallback="Default response")
        response = llm.generate("System", "Something unknown")
        assert response.content == "Default response"

    def test_call_logging(self):
        llm = MockLLMProvider()
        llm.generate("Sys prompt", "User prompt")
        assert len(llm.call_log) == 1
        assert llm.call_log[0]["system"] == "Sys prompt"
        assert llm.call_log[0]["user"] == "User prompt"

    def test_multiple_rules(self):
        llm = MockLLMProvider()
        llm.add_rule("first", "First match")
        llm.add_rule("second", "Second match")
        resp = llm.generate("System", "What about second?")
        assert resp.content == "Second match"

    def test_get_and_set_provider(self):
        reset_llm()
        provider = MockLLMProvider(fallback="Custom")
        set_llm(provider)
        assert get_llm() is provider

    def test_default_mock_provider(self):
        reset_llm()
        provider = get_llm()
        assert isinstance(provider, MockLLMProvider)
