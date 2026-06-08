"""Atomic commit + referential validation for agent output artifacts.

Flow:
  1. Agent writes output JSON to runs/.../step_N/output/
  2. Python reads output, validates with Pydantic
  3. Python checks referential integrity
  4. Python writes committed file atomically (.tmp → .json)
  5. Python appends to commit log (JSONL)
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ValidationError

from src.agents.store import ContractStore


def validate_output(
    raw_data: dict[str, Any] | list[dict[str, Any]],
    model: type[BaseModel],
    many: bool = False,
) -> list[BaseModel]:
    """Validate agent output against a Pydantic model.

    Args:
        raw_data: Parsed JSON output from the agent.
        model: The Pydantic model to validate against.
        many: If True, raw_data is expected to be a list.

    Returns:
        List of validated model instances.

    Raises:
        ValidationError: If validation fails.
    """
    if many:
        if not isinstance(raw_data, list):
            raise ValidationError.from_exception_data(
                "Expected list for many=True",
                line_errors=[{"type": "type_error", "loc": ("root",), "msg": "Expected a list", "input": raw_data}],
            )
        return [model.model_validate(item) for item in raw_data]

    if isinstance(raw_data, list):
        return [model.model_validate(raw_data[0])]
    return [model.model_validate(raw_data)]


def validate_array_output(
    raw_data: list[dict[str, Any]],
    model: type[BaseModel],
) -> list[BaseModel]:
    """Validate a list of items against a Pydantic model."""
    return validate_output(raw_data, model, many=True)


def check_referential_integrity(
    store: ContractStore,
    contracts: list[BaseModel],
    type_key: str,
) -> list[str]:
    """Run referential integrity checks on contracts being committed.

    Checks:
      - episodes: every chapter.episode_id must exist
      - chapters: every scene.chapter_id must exist
      - scenes: episode_id and chapter_id must resolve
      - characters: episode.character_ids / scene character references must exist
      - critiques: target_id must resolve to an existing contract

    Returns list of violation messages (empty = all clean).
    """
    violations: list[str] = []

    episode_ids = {str(c.id) for c in store.list_by_type("episode")}
    chapter_ids = {str(c.id) for c in store.list_by_type("chapter")}
    scene_ids = {str(c.id) for c in store.list_by_type("scene")}
    character_ids = {str(c.id) for c in store.list_by_type("character")}
    critique_target_ids = episode_ids | chapter_ids | scene_ids

    for c in contracts:
        cid = str(getattr(c, "id", "?"))
        type_label = f"{type_key}[{cid[:8]}]"

        if type_key == "chapter":
            eid = str(getattr(c, "episode_id", ""))
            if eid and eid not in episode_ids:
                violations.append(f"{type_label}: episode_id {eid[:8]} not found in store")

        elif type_key == "scene":
            eid = str(getattr(c, "episode_id", ""))
            if eid and eid not in episode_ids:
                violations.append(f"{type_label}: episode_id {eid[:8]} not found in store")
            chid = str(getattr(c, "chapter_id", ""))
            if chid and chid not in chapter_ids:
                violations.append(f"{type_label}: chapter_id {chid[:8]} not found in store")

            chars_present = getattr(c, "characters_present", []) or []
            for char_ref in chars_present:
                if isinstance(char_ref, dict):
                    ref_id = char_ref.get("id", "")
                elif hasattr(char_ref, "id"):
                    ref_id = str(char_ref.id)
                else:
                    ref_id = ""
                if ref_id and ref_id not in character_ids:
                    violations.append(f"{type_label}: character {ref_id[:8]} referenced in characters_present not in store")

        elif type_key == "critique":
            tid = str(getattr(c, "target_id", ""))
            if tid and tid not in critique_target_ids:
                violations.append(f"{type_label}: target_id {tid[:8]} not found in any contract type")

        elif type_key == "episode":
            if hasattr(c, "chapters"):
                ch_list = getattr(c, "chapters", []) or []
                for ch_id in ch_list:
                    sid = str(ch_id) if isinstance(ch_id, UUID) else str(ch_id)
                    if sid and sid not in chapter_ids:
                        violations.append(f"{type_label}: chapter ref {sid[:8]} not found in store")

    return violations


def commit_artifact(
    source_path: Path,
    committed_dir: Path,
    type_key: str,
    artifact_id: str,
) -> Path:
    """Atomically commit an artifact from runs/ to store/committed/.

    Creates the committed directory structure:
      store/committed/{type_key}/{artifact_id}.json

    Writes atomically via .tmp → .replace() to avoid partial writes.
    """
    target_dir = committed_dir / type_key
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{artifact_id}.json"
    tmp_path = target_path.with_suffix(".json.tmp")

    if source_path.exists():
        tmp_path.write_bytes(source_path.read_bytes())
        tmp_path.replace(target_path)
    else:
        # Write an empty artifact marker
        marker = json.dumps({"id": artifact_id, "type": type_key, "committed_at": datetime.now(timezone.utc).isoformat()})
        tmp_path.write_text(marker, encoding="utf-8")
        tmp_path.replace(target_path)

    return target_path


def append_commit_log(
    log_path: Path,
    entry: dict[str, Any],
) -> None:
    """Append a commit entry to the JSONL commit log.

    Creates the log file if it doesn't exist.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry["timestamp"] = entry.get("timestamp", datetime.now(timezone.utc).isoformat())
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def commit_agent_output(
    store: ContractStore,
    type_key: str,
    raw_data: dict[str, Any] | list[dict[str, Any]],
    model: type[BaseModel],
    run_dir: Path,
    agent_role: str = "",
    step_id: str = "",
    many: bool = False,
) -> list[str]:
    """Full flow: validate → check integrity → commit → log.

    Args:
        store: The contract store to write to.
        type_key: Contract type key (e.g. "scene", "episode").
        raw_data: Parsed JSON output from the agent.
        model: Pydantic model class for validation.
        run_dir: The run directory path (runs/{run_id}/step_{step_id}/).
        agent_role: Agent role name for logging.
        step_id: Step identifier for logging.
        many: If True, raw_data is a list of items.

    Returns:
        List of committed contract IDs.

    Raises:
        ValidationError: If validation fails.
        RuntimeError: If referential integrity checks fail.
    """
    # 1. Validate
    validated = validate_output(raw_data, model, many=many)

    # 2. Referential integrity
    violations = check_referential_integrity(store, validated, type_key)
    if violations:
        raise RuntimeError(f"Referential integrity violations for {type_key}:\n" + "\n".join(violations))

    # 3. Commit each contract to store
    committed_ids: list[str] = []
    for contract in validated:
        cid = store.put(type_key, contract, agent=agent_role or "commit")
        committed_ids.append(cid)

        # Atomically write to committed directory
        committed_dir = run_dir.parent.parent / "store" / "committed"
        commit_artifact(
            source_path=run_dir / "output" / f"{type_key}.json",
            committed_dir=committed_dir,
            type_key=type_key,
            artifact_id=cid,
        )

    # 4. Append commit log
    log_path = run_dir.parent.parent / "store" / "commits" / "commit.log.jsonl"
    append_commit_log(log_path, {
        "step_id": step_id,
        "agent": agent_role,
        "type_key": type_key,
        "committed_ids": committed_ids,
        "count": len(validated),
    })

    return committed_ids
