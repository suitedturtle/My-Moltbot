import pytest
import src.memory as mem
from src.commands.memory_commands import (
    SetMemoryCommand, GetMemoryCommand, ListMemoryCommand, ForgetMemoryCommand
)


@pytest.fixture(autouse=True)
def isolated_memory(tmp_path, monkeypatch):
    monkeypatch.setattr(mem, "MEMORY_FILE", str(tmp_path / "clawbot_memory.json"))


class TestSetMemoryCommand:
    cmd = SetMemoryCommand()

    def test_basic_set(self):
        result = self.cmd.execute("SET speed = 75 AS user_preference")
        assert "Saved" in result
        assert "speed" in result

    def test_set_default_context(self):
        self.cmd.execute("SET speed = 75")
        entry = mem.recall("speed")
        assert entry["context"] == "user_preference"

    def test_set_json_value(self):
        self.cmd.execute("SET offsets = [1,2,3] AS system_calibration")
        entry = mem.recall("offsets")
        assert entry["value"] == [1, 2, 3]

    def test_set_invalid_context(self):
        result = self.cmd.execute("SET key = val AS badcontext")
        assert "Error" in result

    def test_set_bad_syntax(self):
        result = self.cmd.execute("SET")
        assert "Usage" in result


class TestGetMemoryCommand:
    cmd = GetMemoryCommand()

    def test_get_existing(self):
        mem.remember("color", "blue", "user_preference")
        result = self.cmd.execute("GET color")
        assert "color" in result
        assert "blue" in result

    def test_get_missing(self):
        result = self.cmd.execute("GET nothing")
        assert "No memory found" in result

    def test_get_bad_syntax(self):
        result = self.cmd.execute("GET")
        assert "Usage" in result


class TestListMemoryCommand:
    cmd = ListMemoryCommand()

    def test_list_all(self):
        mem.remember("a", 1, "operation_log")
        mem.remember("b", 2, "user_preference")
        result = self.cmd.execute("LIST MEMORIES")
        assert "2 entries" in result
        assert "operation_log" in result
        assert "user_preference" in result

    def test_list_filtered(self):
        mem.remember("a", 1, "operation_log")
        mem.remember("b", 2, "user_preference")
        result = self.cmd.execute("LIST MEMORIES user_preference")
        assert "1 entries" in result
        assert "operation_log" not in result

    def test_list_empty(self):
        result = self.cmd.execute("LIST MEMORIES")
        assert "No memories found" in result


class TestForgetMemoryCommand:
    cmd = ForgetMemoryCommand()

    def test_forget_existing(self):
        mem.remember("temp", 1, "operation_log")
        result = self.cmd.execute("FORGET temp")
        assert "Removed 1" in result
        assert mem.recall("temp") is None

    def test_forget_missing(self):
        result = self.cmd.execute("FORGET ghost")
        assert "No memories found" in result

    def test_forget_bad_syntax(self):
        result = self.cmd.execute("FORGET")
        assert "Usage" in result
