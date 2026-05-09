import json
import os
import tempfile
import pytest

import src.memory as mem


@pytest.fixture(autouse=True)
def isolated_memory(tmp_path, monkeypatch):
    """Redirect memory file to a temp path for each test."""
    fake_file = tmp_path / "clawbot_memory.json"
    monkeypatch.setattr(mem, "MEMORY_FILE", str(fake_file))


def test_remember_creates_entry():
    entry = mem.remember("robot_name", "Clawbot", "user_preference")
    assert entry["id"] == 1
    assert entry["key"] == "robot_name"
    assert entry["value"] == "Clawbot"
    assert entry["context"] == "user_preference"
    assert "T" in entry["timestamp"]


def test_remember_increments_id():
    mem.remember("a", 1, "operation_log")
    mem.remember("b", 2, "operation_log")
    entries = mem.all_memories()
    assert entries[0]["id"] == 1
    assert entries[1]["id"] == 2


def test_remember_invalid_context_raises():
    with pytest.raises(ValueError, match="Invalid context"):
        mem.remember("key", "value", "bad_context")


def test_recall_returns_latest():
    mem.remember("speed", 50, "user_preference")
    mem.remember("speed", 75, "user_preference")
    entry = mem.recall("speed")
    assert entry["value"] == 75


def test_recall_missing_key_returns_none():
    assert mem.recall("nonexistent") is None


def test_recall_all():
    mem.remember("x", 1, "operation_log")
    mem.remember("x", 2, "operation_log")
    mem.remember("y", 3, "operation_log")
    results = mem.recall_all("x")
    assert len(results) == 2
    assert all(r["key"] == "x" for r in results)


def test_recall_by_context():
    mem.remember("pref", "blue", "user_preference")
    mem.remember("err", "oops", "error_log")
    results = mem.recall_by_context("user_preference")
    assert len(results) == 1
    assert results[0]["key"] == "pref"


def test_forget_removes_entries():
    mem.remember("temp", 1, "operation_log")
    mem.remember("temp", 2, "operation_log")
    removed = mem.forget("temp")
    assert removed == 2
    assert mem.recall("temp") is None


def test_forget_nonexistent_returns_zero():
    assert mem.forget("ghost") == 0


def test_all_memories_empty():
    assert mem.all_memories() == []


def test_remember_json_compatible_types():
    mem.remember("list_val", [1, 2, 3], "system_calibration")
    mem.remember("dict_val", {"a": 1}, "system_calibration")
    mem.remember("bool_val", True, "operation_log")
    entries = mem.all_memories()
    assert entries[0]["value"] == [1, 2, 3]
    assert entries[1]["value"] == {"a": 1}
    assert entries[2]["value"] is True
