"""
Clawbot memory system schema knowledge for Claude's brain.
Describes the persistent memory structure Clawbot reads and writes.
"""

MEMORY_SCHEMA_KNOWLEDGE = """
════════════════════════════════════════════════════════════════
CLAWBOT MEMORY SYSTEM — SCHEMA AND USAGE REFERENCE
════════════════════════════════════════════════════════════════

OVERVIEW
────────
Clawbot has a persistent JSON memory at memory_system/clawbot_memory.json.
Every memory entry follows a fixed schema. The brain can read, write, search,
and forget entries via the search_memories and save_memory tools, or by
calling SET/GET/FORGET/LIST MEMORIES commands via execute_command.

SCHEMA — EVERY ENTRY HAS THESE FIELDS
───────────────────────────────────────

  id        — Auto-incrementing integer (1, 2, 3...). Assigned on write.
               Never reused even after forget(). Identifies the entry.

  timestamp — ISO 8601 UTC string. Set automatically on write.
               Format: "2024-02-08T14:30:45Z"
               Use the date portion ([:10]) for human-readable display.

  key       — Descriptive snake_case string. The lookup identifier.
               Examples: user_favorite_color, last_analysis, last_error,
               calibration_history, owner_email_preference
               Multiple entries can share a key. recall(key) returns
               the most recent; recall_all(key) returns all of them.

  value     — Any JSON-compatible type: string, number, list, dict.
               Examples:
                 "blue"
                 42
                 ["list", "of", "things"]
                 {"command": "ANALYZE ...", "result": "..."}

  context   — Category string. Must be one of the five valid contexts:

               user_preference    — owner settings, preferences, config
               system_calibration — robot measurement / calibration data
               error_log          — errors caught during command execution
               operation_log      — general bot operations, analysis runs
               conversation       — notes from conversations with owner

EXAMPLE ENTRY
─────────────
  {
    "id": 1,
    "timestamp": "2024-02-08T10:00:00Z",
    "key": "user_name",
    "value": "Alex",
    "context": "user_preference"
  }

WELL-KNOWN KEYS (written automatically by the bot)
───────────────────────────────────────────────────
  last_analysis       — Saved after every ANALYZE run.
                        value: {"command": "...", "result": "..."}
                        context: operation_log

  calibration_history — Saved after every ANALYZE run with parsed metrics.
                        value: {"command": "...", "max_error": 0.3,
                                "mean_error": 0.12, "rms_error": 0.19,
                                "precision": 0.2, "n_points": 5}
                        context: system_calibration

  last_error          — Saved whenever a command throws an exception.
                        value: {"command": "...", "error": "TypeError: ..."}
                        context: error_log

PYTHON API (src/memory.py)
──────────────────────────
  memory.remember(key, value, context="operation_log")  → writes entry
  memory.recall(key)                → most recent entry for key, or None
  memory.recall_all(key)            → list of all entries for key
  memory.recall_by_context(context) → all entries for a context
  memory.forget(key)                → delete all entries for key
  memory.all_memories()             → full list, ordered by id

EMAIL COMMANDS (what the owner types)
──────────────────────────────────────
  SET key = value [AS context]   — store a value; value can be JSON
  GET key                        — retrieve most recent entry for key
  LIST MEMORIES [context]        — list all memories, optionally filtered
  FORGET key                     — delete all entries for key
  RECALL                         — show last saved analysis

IMPORTANT RULES
───────────────
- Keys are snake_case strings. Do not use spaces in keys.
- Timestamps are set automatically — never pass a timestamp on write.
- context must be exactly one of the five valid strings above.
  Default context when none is specified: operation_log.
- The file memory_system/clawbot_memory.json is gitignored on production
  (Render ephemeral filesystem resets it on deploy). For persistence,
  the plan is to migrate to SQLite or Postgres.
- memory_system/sample_memories.json is a static reference example,
  not the live store. Do not read it for live queries.

════════════════════════════════════════════════════════════════
"""
