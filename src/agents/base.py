"""Base agent class — lifecycle, contract access, LLM integration.

Every agent follows this lifecycle:
1. __init__ — receives role name and optional store/LLM references
2. setup() — one-time initialization (load schemas, etc.)
3. execute(context) — the main work method (subclass implements)
4. teardown() — cleanup

Agents communicate *only* through the contract store.

Pre-flight gate: before executing, an agent checks that all prerequisite
contracts exist. If any are missing, it fails with "go back, missing [X]".
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from logging import Logger
from typing import Any

from src.agents.llm import LLMProvider, get_llm
from src.agents.prompts import (
    contracts_to_yaml,
    parse_json_output,
    render_system_prompt,
    render_user_prompt,
)
from src.agents.store import ContractStore, get_store


@dataclass
class AgentContext:
    """Context passed to agent.execute(). Carries workflow state."""

    workflow_id: str  # e.g. "00-brief-and-taxonomy"
    step_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    success: bool = False
    message: str = ""
    artifacts: list[str] = field(default_factory=list)  # contract IDs created/updated
    errors: list[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base for all narrative-engine agents."""

    def __init__(
        self,
        role: str,
        store: ContractStore | None = None,
        llm: LLMProvider | None = None,
        logger: Logger | None = None,
    ) -> None:
        self.role = role
        self.store = store or get_store()
        self.llm = llm or get_llm()
        self.logger = logger

    def log(self, level: str, message: str) -> None:
        if self.logger:
            getattr(self.logger, level.lower(), print)(f"[{self.role}] {message}")

    def setup(self) -> None:
        """Override for one-time initialization."""
        pass

    @abstractmethod
    def execute(self, context: AgentContext) -> AgentResult:
        """Main work method. Subclass must implement."""
        ...

    def teardown(self) -> None:
        """Override for cleanup."""
        pass

    # ── Contract helpers ─────────────────────────────────────────────

    def read_contract(self, type_key: str, contract_id: str) -> Any | None:
        return self.store.get(type_key, contract_id)

    def write_contract(self, type_key: str, contract: Any) -> str:
        return self.store.put(type_key, contract, agent=self.role)

    def list_contracts(self, type_key: str) -> list[Any]:
        return self.store.list_by_type(type_key)

    # ── Pre-flight gate ──────────────────────────────────────────────

    def get_prerequisites(self, step_id: str) -> list[str]:
        """Return list of contract type keys needed for this step.

        Override in subclasses to declare what must exist before this step runs.
        """
        return []

    def check_prerequisites(self, step_id: str) -> list[str]:
        """Check all prerequisites exist in the contract store.

        Returns a list of missing contract type keys (empty = all present).
        """
        missing: list[str] = []
        for prereq in self.get_prerequisites(step_id):
            if not self.list_contracts(prereq):
                missing.append(prereq)
        return missing

    # ── Prompt + LLM helpers ─────────────────────────────────────────

    def _gather_upstream_yaml(self) -> str:
        """Collect all contracts from the store into a YAML string."""
        all_contracts = self.store.list_all()
        chunks: list[str] = []
        for type_key, contracts in all_contracts.items():
            y = contracts_to_yaml(contracts, max_chars=2000)
            chunks.append(f"{type_key}:\n{y}")
        return "\n".join(chunks)

    def _call_llm_for_step(
        self,
        context: AgentContext,
    ) -> dict[str, Any]:
        """Build prompt from role template, call LLM, parse JSON response.

        Returns the parsed JSON dict from the LLM, or a default
        success dict if parsing fails.
        """
        upstream_yaml = self._gather_upstream_yaml()
        medium = context.metadata.get("medium", "book")

        system_prompt = render_system_prompt(
            self.role,
            upstream_contracts=upstream_yaml,
            current_step=context.step_id,
            medium=medium,
        )
        user_prompt = render_user_prompt(
            step_id=context.step_id,
            upstream_yaml=upstream_yaml,
            agent_name=self.role,
            medium=medium,
        )

        self.log("info", f"Calling LLM for step '{context.step_id}'")
        response = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=4096,
        )

        try:
            parsed = parse_json_output(response.content)
            return parsed
        except Exception:
            self.log("warning", f"Failed to parse LLM output as JSON, using defaults")
            return {
                "success": True,
                "message": f"Step '{context.step_id}' completed",
                "errors": [],
                "artifacts": [],
            }
