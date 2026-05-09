import copy
import json
import os
from datetime import datetime, timezone

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "memory_system", "clawbot_memory.json")

VALID_CONTEXTS = {
    "user_preference",
    "system_calibration",
    "error_log",
    "operation_log",
    "conversation",
}

_EMPTY_STORE = {"next_id": 1, "memories": []}


def _load():
    path = os.path.abspath(MEMORY_FILE)
    if not os.path.exists(path):
        return copy.deepcopy(_EMPTY_STORE)
    with open(path, "r") as f:
        return json.load(f)


def _save(store):
    path = os.path.abspath(MEMORY_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(store, f, indent=2)


def remember(key, value, context="operation_log"):
    if context not in VALID_CONTEXTS:
        raise ValueError(f"Invalid context '{context}'. Must be one of: {VALID_CONTEXTS}")

    store = _load()
    entry = {
        "id": store["next_id"],
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "key": key,
        "value": value,
        "context": context,
    }
    store["memories"].append(entry)
    store["next_id"] += 1
    _save(store)
    return entry


def recall(key):
    store = _load()
    matches = [m for m in store["memories"] if m["key"] == key]
    return matches[-1] if matches else None


def recall_all(key):
    store = _load()
    return [m for m in store["memories"] if m["key"] == key]


def recall_by_context(context):
    store = _load()
    return [m for m in store["memories"] if m["context"] == context]


def forget(key):
    store = _load()
    before = len(store["memories"])
    store["memories"] = [m for m in store["memories"] if m["key"] != key]
    removed = before - len(store["memories"])
    if removed:
        _save(store)
    return removed


def all_memories():
    return _load()["memories"]
