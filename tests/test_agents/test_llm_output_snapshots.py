import json
from pathlib import Path

import pytest

from src.agents.prompts import parse_json_output

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"
STDOUT_DIR = Path(__file__).parent / "stdout_snapshots"


def _collect_snapshots():
    if not SNAPSHOTS_DIR.exists():
        return []
    return sorted(SNAPSHOTS_DIR.glob("*.json"))


def _collect_stdout_snapshots():
    if not STDOUT_DIR.exists():
        return []
    return sorted(STDOUT_DIR.glob("*.json"))


class TestResultJsonSnapshots:
    @pytest.mark.parametrize(
        "snapshot_path",
        _collect_snapshots(),
        ids=lambda p: p.stem,
    )
    def test_snapshot_parses(self, snapshot_path: Path):
        raw = snapshot_path.read_text(encoding="utf-8")
        parsed = parse_json_output(raw)
        assert "success" in parsed, f"{snapshot_path.name}: missing 'success'"
        assert "message" in parsed, f"{snapshot_path.name}: missing 'message'"
        contracts = parsed.get("contracts_data", [])
        assert isinstance(contracts, list), f"{snapshot_path.name}: contracts_data not a list"

    @pytest.mark.parametrize(
        "snapshot_path",
        _collect_snapshots(),
        ids=lambda p: p.stem,
    )
    def test_snapshot_contracts_have_required_fields(self, snapshot_path: Path):
        raw = snapshot_path.read_text(encoding="utf-8")
        parsed = parse_json_output(raw)
        contracts = parsed.get("contracts_data", [])
        for i, c in enumerate(contracts):
            has_fields = bool(
                c.keys() & {"contract", "id", "scene_type", "scene_id", "speech_acts"}
            )
            assert has_fields, (
                f"{snapshot_path.name}: contract[{i}] has no identifiable fields"
            )

    @pytest.mark.parametrize(
        "snapshot_path",
        _collect_snapshots(),
        ids=lambda p: p.stem,
    )
    def test_snapshot_message_not_empty(self, snapshot_path: Path):
        raw = snapshot_path.read_text(encoding="utf-8")
        parsed = parse_json_output(raw)
        msg = parsed.get("message", "")
        assert msg, f"{snapshot_path.name}: empty message"


class TestStdoutSnapshots:
    @pytest.mark.parametrize(
        "snapshot_path",
        _collect_stdout_snapshots(),
        ids=lambda p: p.stem,
    )
    def test_stdout_has_text_event(self, snapshot_path: Path):
        raw = snapshot_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        assert lines, f"{snapshot_path.name}: empty stdout"

        text_events = []
        for line in lines:
            try:
                obj = json.loads(line)
                if obj.get("type") == "text":
                    text_events.append(obj["part"]["text"])
            except (json.JSONDecodeError, KeyError):
                continue

        assert text_events, f"{snapshot_path.name}: no text events found"
        combined = " ".join(text_events)
        parsed = parse_json_output(combined)
        assert "success" in parsed, f"{snapshot_path.name}: parsed output missing 'success'"

    @pytest.mark.parametrize(
        "snapshot_path",
        _collect_stdout_snapshots(),
        ids=lambda p: p.stem,
    )
    def test_stdout_has_step_finish(self, snapshot_path: Path):
        raw = snapshot_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        has_finish = any(
            json.loads(line).get("type") == "step_finish"
            for line in lines
            if line
        )
        assert has_finish, f"{snapshot_path.name}: no step_finish event"
