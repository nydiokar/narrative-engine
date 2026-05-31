"""YAML contract loader — read, validate, and render narrative contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

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

CONTRACT_REGISTRY: dict[str, type] = {
    "story": StoryContract,
    "character": CharacterContract,
    "object_of_value": ObjectOfValueContract,
    "episode": EpisodeContract,
    "scene": SceneContract,
    "chapter": ChapterContract,
    "theme": ThemeContract,
    "conflict": ConflictContract,
    "discourse": DiscourseContract,
    "critique": CritiqueContract,
    "world": WorldContract,
}


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Read and parse a YAML file."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        msg = f"Expected a mapping at top level of {path}"
        raise ValueError(msg)
    return data


def detect_contract_type(data: dict[str, Any]) -> tuple[str, type]:
    """Detect the contract type from the data dict and return (type_key, model_class)."""
    for type_key in "story", "character", "episode", "scene", "chapter", "theme", "conflict", "discourse", "critique", "object_of_value", "world":
        if type_key in data:
            return type_key, CONTRACT_REGISTRY[type_key]
    msg = f"Cannot detect contract type — data keys: {list(data.keys())}"
    raise ValueError(msg)


def load_contract(path: str | Path) -> Any:
    """Load and validate a single YAML contract file.

    YAML files use a root key (e.g. story:, character:). This function
    unwraps the root key so Pydantic models receive the inner fields directly.
    """
    data = load_yaml(path)
    type_key, model_class = detect_contract_type(data)
    inner = data[type_key]
    if not isinstance(inner, dict):
        msg = f"Expected a mapping under '{type_key}' in {path}"
        raise ValueError(msg)
    return model_class.model_validate(inner)


def load_all_contracts(directory: str | Path, glob_pattern: str = "*.yaml") -> dict[str, list]:
    """Load all YAML contracts in a directory, grouped by type.

    Returns e.g. {"story": [StoryContract(...)], "character": [CharacterContract(...)], ...}
    """
    directory = Path(directory)
    result: dict[str, list] = {}
    for path in sorted(directory.glob(glob_pattern)):
        try:
            contract = load_contract(path)
            type_key, _ = detect_contract_type(load_yaml(path))
            result.setdefault(type_key, []).append(contract)
        except (ValidationError, ValueError) as exc:
            msg = f"Skipping {path}: {exc}"
            print(msg)
    return result


def render_to_yaml(contract: Any, path: str | Path) -> None:
    """Serialize a contract model to a YAML file."""
    data = contract.model_dump(mode="json", by_alias=True)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
