"""Tests for the base agent class."""

import pytest

from src.agents.base import AgentContext, AgentResult, BaseAgent
from src.agents.store import ContractStore, reset_store
from src.contracts.models import StoryContract


class ConcreteAgent(BaseAgent):
    """Minimal concrete agent for testing."""

    def __init__(self, name: str = "test_agent", **kwargs):
        super().__init__(role=name, **kwargs)
        self.setup_called = False
        self.teardown_called = False

    def setup(self):
        self.setup_called = True

    def execute(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, message=f"Executed {context.step_id}")

    def teardown(self):
        self.teardown_called = True


class TestBaseAgent:
    def setup_method(self):
        reset_store()

    def test_agent_role(self):
        agent = ConcreteAgent("hero_builder")
        assert agent.role == "hero_builder"

    def test_execute_returns_result(self):
        agent = ConcreteAgent()
        context = AgentContext(workflow_id="test", step_id="test_step")
        result = agent.execute(context)
        assert result.success is True
        assert "test_step" in result.message

    def test_write_and_read_contract(self):
        agent = ConcreteAgent()
        story = StoryContract(title="Test", premise="Premise")
        cid = agent.write_contract("story", story)
        retrieved = agent.read_contract("story", cid)
        assert retrieved is not None
        assert retrieved.title == "Test"

    def test_list_contracts(self):
        agent = ConcreteAgent()
        agent.write_contract("story", StoryContract(title="A", premise="P1"))
        agent.write_contract("story", StoryContract(title="B", premise="P2"))
        stories = agent.list_contracts("story")
        assert len(stories) == 2

    def test_lifecycle(self):
        agent = ConcreteAgent()
        assert agent.setup_called is False
        agent.setup()
        assert agent.setup_called is True
        agent.teardown()
        assert agent.teardown_called is True

    def test_default_store_is_isolated(self):
        agent1 = ConcreteAgent()
        agent2 = ConcreteAgent()
        assert agent1.store is not agent2.store

    def test_explicit_store_is_shared(self):
        store = ContractStore()
        agent1 = ConcreteAgent(store=store)
        agent2 = ConcreteAgent(store=store)
        assert agent1.store is agent2.store
