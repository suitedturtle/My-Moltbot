# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

My-Moltbot (also referred to as "Clawbot" in the codebase) is a Python-based bot for controlling and monitoring a physical clawbot/robot. It features a command system and a JSON-based persistent memory system.

## Architecture

### Command System

Commands live under `src/commands/`. Each command is a class with an `execute(command_text)` method and is registered via a `setup(bot)` function:

```python
def setup(bot):
    bot.add_command(ScienceAnalysisCommand())
```

One-line text commands are parsed from natural-language-style strings (e.g., `ANALYZE MY CLAWBOT: Expected [0,25,50,75,100] mm → Actual [0.1,24.8,...] mm`).

### Memory System

`src/memory.py` is the read/write layer. Persistent state is stored in `memory_system/clawbot_memory.json` (auto-created at runtime; `memory_system/sample_memories.json` is the reference example).

**Public API:**

```python
from src import memory

memory.remember(key, value, context="operation_log")  # write
memory.recall(key)           # most recent entry for key
memory.recall_all(key)       # all entries for key
memory.recall_by_context(context)  # all entries for a context
memory.forget(key)           # delete all entries for key
memory.all_memories()        # full list
```

- `key`: snake_case identifier
- `value`: any JSON-compatible type
- `timestamp`: ISO 8601, UTC (set automatically)
- `context`: one of `user_preference`, `system_calibration`, `error_log`, `operation_log`, `conversation`

Each ANALYZE run automatically saves to memory under key `last_analysis`. Errors are caught, displayed gracefully, and logged to memory under key `last_error` with context `error_log`. Type `RECALL` in the bot to retrieve the last analysis.

**All commands** (type `HELP` in the bot for the full reference):

```
SET <key> = <value> [AS <context>]   # store a value; value can be JSON
GET <key>                            # retrieve most recent entry for key
LIST MEMORIES [context]              # list all memories, optionally filtered
FORGET <key>                         # delete all entries for key
RECALL                               # show last saved analysis
HISTORY                              # show calibration run history with trend
```

### Science Analysis Command (`src/commands/science_analysis.py`)

Analyzes robot measurement accuracy. Default expected positions: `[0, 25, 50, 75, 100]` mm. Default precision: `±0.2 mm`. Requires `numpy`.

Computes: absolute errors, z-scores (normalized by precision), movement pattern detection, and a calibration recommendation.

## Running the Web Interface

```bash
pip install -r requirements.txt
python3 web/app.py        # serves on http://localhost:5000
```

The dashboard (`web/app.py` + `web/templates/index.html`) provides:
- A command terminal (all CLI commands work via the browser)
- Quick-command buttons for common operations
- A live memory table with context filtering
- A status panel showing memory count, last analysis date, and last error

**Auth:** Set `CLAWBOT_ACCESS_KEY` env var (default: `clawbot123`) and `CLAWBOT_SECRET_KEY` (Flask session secret). Non-subscribers get a read-only view; subscribers unlock full command access via a login modal backed by a session cookie.

Routes: `GET /` (dashboard), `POST /login`, `POST /logout`, `POST /command` (JSON `{"command": "..."}` → `{"result": "..."}`), `GET /memories?context=<ctx>` (JSON array), `GET /status` (JSON with memory_count, last_analysis_date, last_error), `GET /history` (JSON array of calibration runs).

## Running Tests

```bash
python3 -m pytest tests/ -v        # all tests
python3 -m pytest tests/test_memory.py -v   # single file
```

Tests use `monkeypatch` to redirect `MEMORY_FILE` to a `tmp_path` per test — no real `clawbot_memory.json` is written during test runs.

## Running the Bot

```bash
pip install -r requirements.txt

# Interactive REPL
python3 main.py

# One-shot command
python3 main.py "ANALYZE MY CLAWBOT: Expected [0,25,50,75,100] mm → Actual [0.1,24.8,49.9,75.3,100.2] mm ±0.2mm"
```

`main.py` builds a `ClawbotCommandRegistry`, calls each command module's `setup(bot)` to register commands, then either runs interactively or executes a single command passed as a CLI argument.

## Development Philosophy

Always execute the next most logical step toward a solid, working foundation. Build in this order of priority:
1. Complete existing incomplete code before adding new features
2. Add a runnable entrypoint so the project can actually execute
3. Implement the memory read/write layer so state can persist
4. Add dependencies file and any scaffolding needed to run the project

When in doubt, ask "what does this project need to actually work end-to-end?" and do that next.

## Development Notes

- Dependencies: `numpy` (analysis), `flask` (web), `pytest` (tests) — declared in `requirements.txt`.
- The file named `memory syte` (with a space, in the project root) is a design document for the memory schema, not a source file.
