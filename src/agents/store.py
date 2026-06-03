"""Contract store — in-memory registry with history tracking.

All agents communicate through this shared store. The contract is the source
of truth, not agent memory.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from uuid import UUID

T = TypeVar("T")

ContractT = TypeVar("ContractT")


@dataclass
class VersionRecord:
    version: int
    timestamp: datetime
    agent: str
    action: str  # created, updated, approved, rejected
    snapshot: dict[str, Any]


@dataclass
class ContractEntry(Generic[T]):
    contract: T
    current_version: int = 1
    history: list[VersionRecord] = field(default_factory=list)
    locked: bool = False


class ContractStore:
    """Thread-safe in-memory contract store with history tracking."""

    def __init__(self) -> None:
        self._contracts: dict[tuple[str, str], ContractEntry] = {}
        self._subscribers: list[Callable[[str, str, str, str], None]] = []

    def subscribe(self, callback: Callable[[str, str, str, str], None]) -> None:
        self._subscribers.append(callback)

    def _notify(self, type_key: str, contract_id: str, action: str, agent: str) -> None:
        for cb in self._subscribers:
            cb(type_key, contract_id, action, agent)

    def put(
        self,
        type_key: str,
        contract: Any,
        agent: str = "system",
    ) -> str:
        cid = str(contract.id)
        key = (type_key, cid)

        if key in self._contracts:
            entry = self._contracts[key]
            if entry.locked:
                msg = f"Contract {type_key}/{cid} is locked"
                raise RuntimeError(msg)
            entry.current_version += 1
            entry.history.append(VersionRecord(
                version=entry.current_version,
                timestamp=datetime.now(timezone.utc),
                agent=agent,
                action="updated",
                snapshot=contract.model_dump(mode="json"),
            ))
            entry.contract = contract
        else:
            entry = ContractEntry(
                contract=contract,
                current_version=1,
                history=[
                    VersionRecord(
                        version=1,
                        timestamp=datetime.now(timezone.utc),
                        agent=agent,
                        action="created",
                        snapshot=contract.model_dump(mode="json"),
                    )
                ],
            )
            self._contracts[key] = entry

        self._notify(type_key, cid, "updated" if entry.current_version > 1 else "created", agent)
        return cid

    def get(self, type_key: str, contract_id: str | UUID) -> Any | None:
        key = (type_key, str(contract_id))
        entry = self._contracts.get(key)
        return entry.contract if entry else None

    def get_history(self, type_key: str, contract_id: str | UUID) -> list[VersionRecord]:
        key = (type_key, str(contract_id))
        entry = self._contracts.get(key)
        return list(entry.history) if entry else []

    def list_by_type(self, type_key: str) -> list[Any]:
        return [
            entry.contract
            for (tk, _), entry in self._contracts.items()
            if tk == type_key
        ]

    def list_all(self) -> dict[str, list[Any]]:
        result: dict[str, list[Any]] = {}
        for (tk, _), entry in self._contracts.items():
            result.setdefault(tk, []).append(entry.contract)
        return result

    def lock(self, type_key: str, contract_id: str | UUID) -> None:
        key = (type_key, str(contract_id))
        entry = self._contracts.get(key)
        if entry:
            entry.locked = True

    def unlock(self, type_key: str, contract_id: str | UUID) -> None:
        key = (type_key, str(contract_id))
        entry = self._contracts.get(key)
        if entry:
            entry.locked = False

    def count(self) -> int:
        return len(self._contracts)

    def delete_by_type(self, type_key: str) -> int:
        """Delete all contracts of the given type. Returns count deleted."""
        keys_to_delete = [k for k in self._contracts if k[0] == type_key]
        for k in keys_to_delete:
            del self._contracts[k]
        return len(keys_to_delete)

    def save(self, path: str) -> None:
        """Serialize the store to a JSON file."""
        import json
        from datetime import datetime

        def serialize_dt(obj: Any) -> Any:
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, UUID):
                return str(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        data: dict[str, list[dict[str, Any]]] = {}
        for (tk, cid), entry in self._contracts.items():
            data.setdefault(tk, []).append({
                "contract": entry.contract.model_dump(mode="json"),
                "current_version": entry.current_version,
                "history": [
                    {
                        "version": h.version,
                        "timestamp": h.timestamp.isoformat(),
                        "agent": h.agent,
                        "action": h.action,
                        "snapshot": h.snapshot,
                    }
                    for h in entry.history
                ],
                "locked": entry.locked,
            })

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=serialize_dt)

    def load(self, path: str) -> None:
        """Deserialize the store from a JSON file, merging into existing state."""
        import json
        from datetime import datetime

        from pydantic import BaseModel

        from src.contracts.models import (
            ChapterContract,
            CharacterContract,
            ConflictContract,
            CritiqueContract,
            DiscourseContract,
            EpisodeContract,
            ObjectOfValueContract,
            SceneContract,
            StoryContract,
            ThemeContract,
            WorldContract,
        )

        TYPE_MODEL_MAP: dict[str, type[BaseModel]] = {
            "story": StoryContract,
            "theme": ThemeContract,
            "character": CharacterContract,
            "object_of_value": ObjectOfValueContract,
            "episode": EpisodeContract,
            "chapter": ChapterContract,
            "scene": SceneContract,
            "conflict": ConflictContract,
            "discourse": DiscourseContract,
            "critique": CritiqueContract,
            "world": WorldContract,
        }

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        loaded = 0
        for type_key, entries in data.items():
            model_cls = TYPE_MODEL_MAP.get(type_key)
            if not model_cls:
                continue
            for entry_data in entries:
                contract_dict = entry_data["contract"]
                contract = model_cls(**contract_dict)
                self.put(type_key, contract, agent="system")
                loaded += 1

    def clear(self) -> None:
        self._contracts.clear()


# Singleton shared across agents
_store: ContractStore | None = None


def get_store() -> ContractStore:
    global _store
    if _store is None:
        _store = ContractStore()
    return _store


def reset_store() -> None:
    global _store
    _store = None
