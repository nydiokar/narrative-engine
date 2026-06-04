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
        # Type-level field locks: {type_key: {field_path, ...}}
        # Field locks apply to ALL contracts of a type, regardless of UUID.
        self._field_locks: dict[str, set[str]] = {}

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
                return cid
            field_locks = self._field_locks.get(type_key, set())
            if field_locks:
                # Use the last history snapshot as the baseline (agents may have
                # mutated the contract object in-place, so live model_dump()
                # would reflect the NEW values, not the frozen ones).
                existing_dict = self._get_latest_snapshot(entry, type_key)
                new_dict = contract.model_dump(mode="json") if hasattr(contract, "model_dump") else {}
                merged = self._deep_merge(existing_dict, new_dict, field_locks)
                model_cls = type(entry.contract)
                contract = model_cls(**merged)
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
            # New contract: apply type-level field locks if any exist
            field_locks = self._field_locks.get(type_key, set())
            if field_locks:
                existing_contracts = self.list_by_type(type_key)
                if existing_contracts:
                    latest = existing_contracts[-1]
                    existing_snapshot = latest.model_dump(mode="json") if hasattr(latest, "model_dump") else {}
                    new_dict = contract.model_dump(mode="json") if hasattr(contract, "model_dump") else {}
                    merged = self._deep_merge(existing_snapshot, new_dict, field_locks)
                    model_cls = type(latest)
                    contract = model_cls(**merged)

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

    def lock_all(self, type_key: str) -> int:
        """Lock all contracts of a given type. Returns count locked."""
        locked = 0
        for (tk, cid), entry in self._contracts.items():
            if tk == type_key and not entry.locked:
                entry.locked = True
                locked += 1
        return locked

    def unlock_all(self, type_key: str) -> int:
        """Unlock all contracts of a given type. Returns count unlocked."""
        unlocked = 0
        for (tk, _), entry in self._contracts.items():
            if tk == type_key and entry.locked:
                entry.locked = False
                unlocked += 1
        return unlocked

    def is_type_locked(self, type_key: str) -> bool:
        """Check if ALL contracts of a given type are locked.

        Returns False if no contracts exist or any is unlocked.
        """
        has_any = False
        for (tk, _), entry in self._contracts.items():
            if tk == type_key:
                has_any = True
                if not entry.locked:
                    return False
        return has_any  # True only if at least one exists and all are locked

    def count(self) -> int:
        return len(self._contracts)

    def lock_field(self, type_key: str, contract_id: str | UUID, field_path: str) -> None:
        """Lock a specific field path on all contracts of a type.

        When locked, the field value is preserved across future put() calls
        while other fields on the same contract can still be updated.
        Field locks are type-level (apply to all contracts of the type regardless of UUID).
        """
        if type_key not in self._field_locks:
            self._field_locks[type_key] = set()
        self._field_locks[type_key].add(field_path)

    def unlock_field(self, type_key: str, contract_id: str | UUID, field_path: str) -> None:
        """Unlock a specific field path on a contract type."""
        if type_key in self._field_locks:
            self._field_locks[type_key].discard(field_path)
            if not self._field_locks[type_key]:
                del self._field_locks[type_key]

    def lock_field_all(self, type_key: str, field_path: str) -> int:
        """Lock a field path on a type. Returns 1 if newly locked.
        This is a no-op if already locked (path already registered).
        """
        self.lock_field(type_key, "any", field_path)
        return 1

    def unlock_field_all(self, type_key: str, field_path: str) -> int:
        """Unlock a field path on a type. Returns 1 if unlocked."""
        self.unlock_field(type_key, "any", field_path)
        return 1

    @staticmethod
    def _deep_merge(existing: dict, new: dict, locked_fields: set[str], prefix: str = "") -> dict:
        """Deep-merge two dicts, preserving existing values at locked field paths.

        Locked field paths that don't exist in ``existing`` are not preserved;
        only fields that have already been set are frozen.

        A lock on a parent path (e.g. 'genre') also locks all sub-paths
        (e.g. 'genre.primary_bisac').
        """
        result = dict(existing)
        for key, value in new.items():
            field_path = f"{prefix}.{key}" if prefix else key
            # Check if this path or any ancestor path is locked
            path_locked = field_path in locked_fields or any(
                field_path.startswith(lp + ".") for lp in locked_fields
            )
            if path_locked and key in existing and existing[key] is not None:
                continue
            if isinstance(value, dict) and isinstance(existing.get(key), dict):
                result[key] = ContractStore._deep_merge(
                    existing[key], value, locked_fields, field_path,
                )
            else:
                result[key] = value
        return result

    def _get_latest_snapshot(self, entry: ContractEntry, type_key: str) -> dict:
        """Return the last committed snapshot for a contract entry.

        Uses the most recent history snapshot (taken by the previous put())
        rather than live model_dump(), which may reflect in-place mutations
        by agent code. Falls back to model_dump() if no history exists.
        """
        if entry.history:
            return dict(entry.history[-1].snapshot)
        if hasattr(entry.contract, "model_dump"):
            return entry.contract.model_dump(mode="json")
        return {}

    def delete_by_type(self, type_key: str) -> int:
        """Delete all contracts of the given type. Returns count deleted."""
        keys_to_delete = [k for k in self._contracts if k[0] == type_key]
        for k in keys_to_delete:
            del self._contracts[k]
        self._field_locks.pop(type_key, None)
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

        # Build field locks index: {type_key: [field_paths]}
        field_locks_index: dict[str, list[str]] = {
            tk: sorted(paths) for tk, paths in self._field_locks.items()
        }

        data: dict[str, Any] = {
            "contracts": {},
            "field_locks": field_locks_index,
        }
        for (tk, cid), entry in self._contracts.items():
            data["contracts"].setdefault(tk, []).append({
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
            raw = json.load(f)

        # Support both old format (flat dict) and new format (nested with field_locks)
        if "contracts" in raw:
            contracts_data = raw["contracts"]
            field_locks_data = raw.get("field_locks", {})
        else:
            contracts_data = raw
            field_locks_data = {}

        loaded = 0
        for type_key, entries in contracts_data.items():
            model_cls = TYPE_MODEL_MAP.get(type_key)
            if not model_cls:
                continue
            for entry_data in entries:
                contract_dict = entry_data["contract"]
                contract = model_cls(**contract_dict)
                cid = self.put(type_key, contract, agent="system")
                # Restore lock state
                if entry_data.get("locked", False):
                    self.lock(type_key, cid)
                loaded += 1

        # Restore field locks from index (new format: {type_key: [path, ...]})
        if field_locks_data and isinstance(next(iter(field_locks_data.values()), None), dict):
            # Old format: {type_key: {cid: [paths]}} — migrate to new
            for type_key, cid_map in field_locks_data.items():
                for _cid_str, paths in cid_map.items():
                    for path in paths:
                        self.lock_field(type_key, _cid_str, path)
        else:
            # New format: {type_key: [path, ...]}
            for type_key, paths in field_locks_data.items():
                for path in paths:
                    self.lock_field(type_key, "any", path)

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable snapshot of all contracts plus field locks."""
        # Build field locks index: {type_key: [field_paths]}
        field_locks_index: dict[str, list[str]] = {
            tk: sorted(paths) for tk, paths in self._field_locks.items()
        }

        data: dict[str, Any] = {
            "contracts": {},
            "field_locks": field_locks_index,
        }
        for (tk, cid), entry in self._contracts.items():
            data["contracts"].setdefault(tk, []).append({
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
        return data

    def restore(self, snapshot_data: dict[str, list[dict[str, Any]]]) -> None:
        """Restore store state from a snapshot (clears current state first)."""
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

        self._contracts.clear()
        self._field_locks.clear()

        if "contracts" in snapshot_data:
            contracts_data = snapshot_data["contracts"]
            field_locks_data = snapshot_data.get("field_locks", {})
        else:
            contracts_data = snapshot_data
            field_locks_data = {}

        for type_key, entries in contracts_data.items():
            model_cls = TYPE_MODEL_MAP.get(type_key)
            if not model_cls:
                continue
            for entry_data in entries:
                contract_dict = entry_data["contract"]
                contract = model_cls(**contract_dict)
                cid = self.put(type_key, contract, agent="system")
                if entry_data.get("locked", False):
                    self.lock(type_key, cid)

        # Restore field locks (new format: {type_key: [path, ...]})
        if field_locks_data and isinstance(next(iter(field_locks_data.values()), None), dict):
            for type_key, cid_map in field_locks_data.items():
                for _cid_str, paths in cid_map.items():
                    for path in paths:
                        self.lock_field(type_key, _cid_str, path)
        else:
            for type_key, paths in field_locks_data.items():
                for path in paths:
                    self.lock_field(type_key, "any", path)

    def clear(self) -> None:
        self._contracts.clear()
        self._field_locks.clear()


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
