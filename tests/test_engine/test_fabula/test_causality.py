"""Tests for the causality engine."""

import pytest

from src.engine.fabula.causality import (
    CausalLink,
    CausalityGraph,
    CausalityMechanism,
    CausalityValidator,
)


class TestCausalityGraph:
    def test_simple_chain(self):
        graph = CausalityGraph()
        graph.add_event("a", 0)
        graph.add_event("b", 1)
        graph.add_event("c", 2)
        graph.add_link(CausalLink(cause_id="a", effect_id="b"))
        graph.add_link(CausalLink(cause_id="b", effect_id="c"))

        result = graph.validate()
        assert result.is_valid is True

    def test_orphan_event(self):
        graph = CausalityGraph()
        graph.add_event("a", 0)
        graph.add_event("b", 1)  # no links

        result = graph.validate()
        assert result.is_valid is False
        assert "b" in result.orphan_events

    def test_backward_causation(self):
        graph = CausalityGraph()
        graph.add_event("a", 2)  # seq 2
        graph.add_event("b", 1)  # seq 1 — but b claims a caused it
        graph.add_link(CausalLink(cause_id="a", effect_id="b"))

        result = graph.validate()
        assert result.is_valid is False
        assert len(result.backward_causes) > 0

    def test_ancestors(self):
        graph = CausalityGraph()
        graph.add_event("a", 0)
        graph.add_event("b", 1)
        graph.add_event("c", 2)
        graph.add_link(CausalLink(cause_id="a", effect_id="b"))
        graph.add_link(CausalLink(cause_id="b", effect_id="c"))

        ancestors = graph.get_ancestors("c")
        assert "a" in ancestors
        assert "b" in ancestors

    def test_descendants(self):
        graph = CausalityGraph()
        graph.add_event("a", 0)
        graph.add_event("b", 1)
        graph.add_event("c", 2)
        graph.add_link(CausalLink(cause_id="a", effect_id="b"))
        graph.add_link(CausalLink(cause_id="a", effect_id="c"))

        descendants = graph.get_descendants("a")
        assert "b" in descendants
        assert "c" in descendants


class TestCausalityValidator:
    def test_validate_events(self):
        events = [
            {"id": "a", "sequence_number": 0, "causal_predecessors": []},
            {"id": "b", "sequence_number": 1, "causal_predecessors": ["a"]},
        ]
        result = CausalityValidator.validate_events(events)
        assert result.is_valid is True

    def test_validate_events_orphan(self):
        events = [
            {"id": "a", "sequence_number": 0, "causal_predecessors": []},
            {"id": "b", "sequence_number": 1, "causal_predecessors": []},
        ]
        result = CausalityValidator.validate_events(events)
        assert result.is_valid is False

    def test_validate_event_chain_ordering(self):
        chain = [
            {"id": "a", "sequence_number": 1},  # starts at 1
            {"id": "b", "sequence_number": 0},  # out of order
        ]
        result = CausalityValidator.validate_event_chain(chain)
        assert result.is_valid is False

    def test_validate_event_chain_passes(self):
        chain = [
            {"id": "a", "sequence_number": 0, "causal_predecessors": []},
            {"id": "b", "sequence_number": 1, "causal_predecessors": ["a"]},
            {"id": "c", "sequence_number": 2, "causal_predecessors": ["b"]},
        ]
        result = CausalityValidator.validate_event_chain(chain)
        assert result.is_valid is True
