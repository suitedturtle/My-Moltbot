# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## User Preferences

- **Links:** Always provide URLs in plain copy-paste text format (e.g. https://example.com), NOT as markdown hyperlinks (e.g. never [title](url)). The user finds plain URLs much easier to copy and use.

## Project Overview

My-Moltbot (also referred to as "Clawbot" in the codebase) is a Python-based job listings and AI assistant platform. It serves California public-safety and tech job listings at https://calcojobs.com, and exposes a command-line bot interface backed by Claude for question answering. It features:
- A Flask web app with job listings, a command terminal, and email subscription
- An Anthropic Claude integration (`src/claude_brain.py`) for the `/ask` route
- An IMAP email listener that executes bot commands sent by the owner
- A set of job scrapers (USAJobs, Adzuna, CalCareers, company pages)
- A Gladius Combat Wear standalone website (`gladius/`)

## Directory Layout

```
My-Moltbot/
├── main.py                        # CLI entrypoint and command registry
├── requirements.txt               # pip dependencies
├── render.yaml                    # Render.com deployment (web + cron)
├── src/
│   ├── claude_brain.py            # Anthropic API wrapper for Claude Q&A
│   ├── email_listener.py          # IMAP listener — executes commands from owner email
│   ├── memory.py                  # JSON-based persistent memory store
│   └── commands/
│       ├── help_command.py
│       ├── history_command.py
│       ├── memory_commands.py     # SET / GET / LIST / FORGET
│       └── science_analysis.py   # ANALYZE command (numpy error stats)
├── scrapers/
│   ├── base.py                    # BaseScraper abstract class
│   ├── usajobs.py                 # USAJobs API scraper
│   ├── adzuna.py                  # Adzuna API scraper
│   ├── calcareers.py              # CalCareers HTML scraper
│   ├── company.py                 # Direct company page scrapers
│   └── run.py                     # Entrypoint — runs all scrapers, writes web/data/jobs.json
├── web/
│   ├── app.py                     # Flask app (all routes)
│   ├── data/jobs.json             # Job listings (source of truth for /jobs)
│   └── templates/
│       ├── index.html             # /dashboard — bot terminal + memory table
│       ├── jobs.html              # /jobs — listings with search/filter
│       ├── job_detail.html        # /jobs/<id> — individual job SEO page
│       ├── about.html             # /about
│       └── privacy.html          # /privacy
├── gladius/                       # Gladius CombatWear standalone website
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── assistants/
│   └── gladius/CLAUDE.md         # Scoped assistant guidance for Gladius frontend
├── memory_system/
│   └── sample_memories.json      # Reference schema for clawbot_memory.json
└── tests/
    ├── test_memory.py
    ├── test_memory_commands.py
    └── test_science_analysis.py
```

## Architecture

### Command System

Commands live under `src/commands/`. Each command is a class with an `execute(command_text)` method and is registered via a `setup(bot)` function:

```python
def setup(bot):
    bot.add_command(ScienceAnalysisCommand())
```

`main.py` builds a `ClawbotCommandRegistry`, calls each command module's `setup(bot)` to register commands, then either runs interactively or executes a single command passed as a CLI argument.

Command routing uses prefix matching on uppercased input (see `COMMAND_ROUTING` in `main.py`).

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

### Claude Brain (`src/claude_brain.py`)

Wraps the Anthropic Messages API for the `/ask` route. Uses model `claude-sonnet-4-20250514`.

```python
from src.claude_brain import ask_claude
answer = ask_claude("What jobs are available?", context="conversation")
```

- Requires `ANTHROPIC_API_KEY` env var; returns a graceful offline message if unset.
- Saves each response to memory under key `last_claude_response`.

### Email Listener (`src/email_listener.py`)

Polls Gmail via IMAP every `EMAIL_POLL_MINUTES` (default 5) minutes on a background daemon thread. Executes bot commands sent from `OWNER_EMAIL` only, and replies with HTML-formatted results via SMTP.

- Reuses the same SMTP env vars as `web/app.py`.
- Only the **first line** of the email body is treated as the command (ignores signatures).
- Started automatically by `web/app.py` at Flask startup: `start_listener(bot)`.

Required env vars: `OWNER_EMAIL`, `SMTP_USER`, `SMTP_PASSWORD`.

### Scrapers (`scrapers/`)

Each scraper extends `BaseScraper` and implements `scrape() -> list[dict]`. Run all scrapers:

```bash
python scrapers/run.py
```

Output is written to `web/data/jobs.json` (the `/jobs` page data source).

| Scraper | Source | API Key Required |
|---------|--------|-----------------|
| `usajobs.py` | USAJobs API | `USAJOBS_API_KEY`, `USAJOBS_EMAIL` |
| `adzuna.py` | Adzuna API | `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` |
| `calcareers.py` | CalCareers HTML | No |
| `company.py` | Company pages | No |

### Science Analysis Command (`src/commands/science_analysis.py`)

Analyzes robot measurement accuracy. Default expected positions: `[0, 25, 50, 75, 100]` mm. Default precision: `±0.2 mm`. Requires `numpy`.

Computes: absolute errors, z-scores, movement pattern detection, and a calibration recommendation.

### Gladius CombatWear (`gladius/`)

Standalone HTML/CSS/JS website for the Gladius combat wear brand. Completely separate from the Flask app — deployed independently or served as static files. See `assistants/gladius/CLAUDE.md` for scoped guidance.

## Running the Web Interface

```bash
pip install -r requirements.txt
python3 web/app.py        # serves on http://localhost:5000
```

**Auth:** Set `CLAWBOT_ACCESS_KEY` env var (default: `clawbot123`) and `CLAWBOT_SECRET_KEY` (Flask session secret). Non-subscribers get a read-only view; subscribers unlock full command access via a login modal backed by a session cookie.

**Email:** Set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `FROM_EMAIL`, `SITE_NAME`, `SITE_URL` env vars to enable outgoing email. Call `send_weekly_digest()` from a cron job to email all subscribers weekly.

## Web Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Redirects to `/jobs` |
| GET | `/dashboard` | Bot terminal, memory table, status panel |
| GET | `/jobs` | Job listings (search, region/type filters, AdSense) |
| GET | `/jobs/<job_id>` | Individual job detail page (SEO) |
| GET | `/about` | About page |
| GET | `/privacy` | Privacy policy |
| POST | `/command` | Run a bot command; JSON `{"command":"..."}` → `{"result":"..."}` |
| POST | `/ask` | Ask Claude a question; JSON `{"question":"..."}` → `{"answer":"..."}` |
| GET | `/status` | JSON: memory_count, last_analysis_date, last_error, subscriber_count |
| GET | `/history` | JSON array of calibration history entries |
| GET | `/memories?context=<ctx>` | JSON array of memory entries, optionally filtered |
| POST | `/subscribe` | Add email subscriber; sends welcome email |
| POST | `/unsubscribe` | Remove email subscriber |
| GET | `/sitemap.xml` | Auto-generated XML sitemap (SEO) |
| GET | `/robots.txt` | robots.txt (SEO) |
| POST | `/admin/scrape` | Trigger job scrape (requires `X-Admin-Key` header) |

## Running the Bot

```bash
pip install -r requirements.txt

# Interactive REPL
python3 main.py

# One-shot command
python3 main.py "ANALYZE MY CLAWBOT: Expected [0,25,50,75,100] mm → Actual [0.1,24.8,49.9,75.3,100.2] mm ±0.2mm"
```

**All commands** (type `HELP` in the bot for the full reference):

```
SET <key> = <value> [AS <context>]   # store a value; value can be JSON
GET <key>                            # retrieve most recent entry for key
LIST MEMORIES [context]              # list all memories, optionally filtered
FORGET <key>                         # delete all entries for key
RECALL                               # show last saved analysis
HISTORY                              # show calibration run history with trend
ANALYZE MY CLAWBOT: Expected [...] mm → Actual [...] mm ±Xmm
```

## Running Tests

```bash
python3 -m pytest tests/ -v        # all tests
python3 -m pytest tests/test_memory.py -v   # single file
```

Tests use `monkeypatch` to redirect `MEMORY_FILE` to a `tmp_path` per test — no real `clawbot_memory.json` is written during test runs.

## Deploying to Render

The repo includes `render.yaml` which configures a Render web service and a weekly cron job automatically.

**Services declared in render.yaml:**
- `calcojobs` — Flask web service (gunicorn)
- `calcojobs-weekly-scrape` — Cron job (Sundays 10:00 UTC, runs `python scrapers/run.py`)

**One-time setup steps:**
1. Go to https://render.com and sign up (free)
2. Click **New → Web Service** → connect your GitHub account → select `suitedturtle/My-Moltbot`
3. Render detects `render.yaml` automatically — click **Deploy**
4. In the Render dashboard → Environment, add these secret vars manually:
   - `SMTP_USER` — your Gmail address
   - `SMTP_PASSWORD` — your Gmail App Password (not your login password)
   - `FROM_EMAIL` — same as SMTP_USER
   - `OWNER_EMAIL` — email address allowed to send bot commands
   - `ANTHROPIC_API_KEY` — for the /ask route
   - `USAJOBS_API_KEY` + `USAJOBS_EMAIL` — for job scraper
   - `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` — for job scraper
5. Under **Settings → Custom Domains**, add `calcojobs.com` and follow Render's DNS instructions

**Start command:** `gunicorn web.app:app`

**Important note on data persistence:** Render's free tier has an ephemeral filesystem — the `memory_system/` JSON files reset on each new deploy. For now this is fine for launch. Long-term, migrate subscribers to a database (SQLite on a paid Render disk, or a free Postgres instance).

## Key Files

- `web/data/jobs.json` — Job listings (source of truth for /jobs)
- `memory_system/email_subscribers.json` — Subscriber list (gitignored, auto-created at runtime)
- `memory_system/clawbot_memory.json` — Bot memory store (gitignored, auto-created at runtime)
- `memory syte` — Design document for the memory schema (not a source file; the space in the name is intentional)

## Dependencies

Declared in `requirements.txt`:

| Package | Purpose |
|---------|---------|
| `numpy` | Science analysis command |
| `flask` | Web server |
| `gunicorn` | Production WSGI server |
| `pytest` | Tests |
| `requests` | HTTP scraping |
| `beautifulsoup4` | HTML scraping (CalCareers, company pages) |
| `lxml` | HTML parser backend |

No Anthropic SDK — `src/claude_brain.py` calls the API directly via `urllib.request`.

## AdSense

Publisher ID: `ca-pub-6496918064862756`. Auto-ads script is in both template `<head>` blocks. Individual `<ins>` slots use `data-ad-slot="auto"`. After AdSense approves the site, replace `"auto"` with real slot IDs from the AdSense console.

## SEO

- `robots.txt` route
- `sitemap.xml` route (dynamic, lists /, /jobs, and each job anchor)
- Meta description + Open Graph tags on index.html and jobs.html
- JSON-LD JobPosting structured data on jobs.html (enables Google Jobs integration)

## Development Philosophy

Always execute the next most logical step toward a solid, working foundation. Build in this order of priority:
1. Complete existing incomplete code before adding new features
2. Add a runnable entrypoint so the project can actually execute
3. Implement the memory read/write layer so state can persist
4. Add dependencies file and any scaffolding needed to run the project

When in doubt, ask "what does this project need to actually work end-to-end?" and do that next.

## GitHub Workflow

- `.github/workflows/daily-scraper.yml` — triggers `/admin/scrape` via `curl` on a daily schedule (also runs the cron on Render via `render.yaml`)
