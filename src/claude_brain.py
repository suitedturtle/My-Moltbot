"""
Claude AI brain for Clawbot email commands.
Replaces rigid text-command parsing with natural language understanding.
"""
import json
import os
from anthropic import Anthropic

from src import memory
from src.knowledge.thucydides import THUCYDIDES_KNOWLEDGE

JOBS_FILE        = os.path.join(os.path.dirname(__file__), "..", "web", "data", "jobs.json")
SUBSCRIBERS_FILE = os.path.join(os.path.dirname(__file__), "..", "memory_system", "email_subscribers.json")

SYSTEM_PROMPT = """You are Clawbot, an intelligent assistant for the owner of calcojobs.com — \
a California robotics and automation job board. You respond to email commands from your owner.

You have tools to: run bot commands (RECALL, HISTORY, ANALYZE, THUCYDIDES, SET, GET, LIST MEMORIES, FORGET), \
check site stats (subscribers, jobs, last analysis), analyze market power dynamics, \
search memory, and save new memories.

You are a deep expert in the Thucydides Trap framework. When analyzing any power-shift dynamic — \
between companies, national economies, technology platforms, or market categories — apply the full \
analytical framework below. Don't just mention the trap; reason through the structural stress factors, \
identify which resolution pathway applies, and give a grounded assessment.

""" + THUCYDIDES_KNOWLEDGE + """

When the owner asks about market dynamics, geopolitics, or competitive positioning in robotics/AI, \
use this framework to give substantive, historically grounded analysis. Use the job board data tools \
to ground your analysis in real hiring signals from calcojobs.com.

Understand the owner's intent, use tools as needed, and reply conversationally. \
Be concise and direct. Always give a clear answer — don't just describe what you did."""

TOOLS = [
    {
        "name": "execute_command",
        "description": (
            "Run a Clawbot bot command. Use for: RECALL (last calibration analysis), "
            "HISTORY (calibration run history), ANALYZE (robot measurement accuracy), "
            "SET key = value [AS context], GET key, LIST MEMORIES [context], FORGET key."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bot command string, e.g. 'RECALL' or 'GET last_analysis'",
                }
            },
            "required": ["command"],
        },
    },
    {
        "name": "get_site_status",
        "description": "Get calcojobs.com stats: subscriber count, total jobs, jobs by category, last analysis.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "search_memories",
        "description": "Search Clawbot's persistent memory by key or context.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Specific memory key to look up"},
                "context": {
                    "type": "string",
                    "description": "Filter by context type",
                    "enum": [
                        "user_preference", "system_calibration",
                        "error_log", "operation_log", "conversation",
                    ],
                },
            },
        },
    },
    {
        "name": "analyze_market_power",
        "description": (
            "Analyze the calcojobs job market through the Thucydides Trap lens. "
            "Returns established incumbents vs rising challengers by job count, "
            "category dominance, and geopolitical dynamics (U.S. vs China)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Filter to a job category (optional), e.g. 'Robotics & Automation'",
                }
            },
        },
    },
    {
        "name": "save_memory",
        "description": "Save a piece of information to Clawbot's persistent memory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key":     {"type": "string", "description": "Memory key (snake_case)"},
                "value":   {"type": "string", "description": "Value to store"},
                "context": {
                    "type": "string",
                    "enum": [
                        "user_preference", "system_calibration",
                        "error_log", "operation_log", "conversation",
                    ],
                    "description": "Context category (default: operation_log)",
                },
            },
            "required": ["key", "value"],
        },
    },
]


def _run_tool(bot, name: str, inputs: dict) -> str:
    if name == "execute_command":
        return bot.execute(inputs["command"])

    if name == "get_site_status":
        result = {}
        try:
            subs = json.load(open(SUBSCRIBERS_FILE)) if os.path.exists(SUBSCRIBERS_FILE) else []
            result["subscriber_count"] = len(subs)
        except Exception:
            result["subscriber_count"] = "unknown"
        try:
            jobs = json.load(open(JOBS_FILE)) if os.path.exists(JOBS_FILE) else []
            by_cat: dict = {}
            for j in jobs:
                cat = j.get("category", "Other")
                by_cat[cat] = by_cat.get(cat, 0) + 1
            result["total_jobs"]       = len(jobs)
            result["jobs_by_category"] = by_cat
        except Exception:
            result["total_jobs"] = "unknown"
        last = memory.recall("last_analysis")
        result["last_analysis"] = (
            {"date": last["timestamp"][:10], "summary": str(last["value"].get("result", ""))[:200]}
            if last else None
        )
        return json.dumps(result, indent=2)

    if name == "search_memories":
        key     = inputs.get("key")
        context = inputs.get("context")
        if key:
            entries = memory.recall_all(key)
        elif context:
            entries = memory.recall_by_context(context)
        else:
            entries = memory.all_memories()[-20:]
        return json.dumps(entries, indent=2)

    if name == "analyze_market_power":
        from collections import Counter
        CHINESE_COMPANIES = {"DJI", "Unitree", "UBTECH", "Meituan", "Geely", "BYD",
                             "Huawei", "Xiaomi", "Horizon Robotics"}
        RISING = {"Figure AI", "Apptronik", "1X Technologies", "Agility Robotics",
                  "Sanctuary AI", "Skydio", "Nuro", "Viam", "Unitree", "UBTECH",
                  "Horizon Robotics", "Nauticus Robotics", "Overland AI"}
        try:
            jobs = json.load(open(JOBS_FILE)) if os.path.exists(JOBS_FILE) else []
            cat_filter = inputs.get("category", "").lower()
            if cat_filter:
                jobs = [j for j in jobs if cat_filter in j.get("category", "").lower()]
            company_counts = Counter(j.get("company", "Unknown") for j in jobs)
            top = company_counts.most_common(20)
            result = {
                "total_jobs_analyzed": len(jobs),
                "established_powers": [
                    {"company": c, "jobs": n} for c, n in top
                    if c not in RISING and n > 1
                ][:8],
                "rising_challengers": [
                    {"company": c, "jobs": n, "chinese": c in CHINESE_COMPANIES}
                    for c, n in top if c in RISING
                ],
                "chinese_presence": [
                    {"company": c, "jobs": n} for c, n in top if c in CHINESE_COMPANIES
                ],
                "categories": dict(Counter(j.get("category", "Other") for j in jobs)),
            }
        except Exception as e:
            result = {"error": str(e)}
        return json.dumps(result, indent=2)

    if name == "save_memory":
        entry = memory.remember(
            key=inputs["key"],
            value=inputs["value"],
            context=inputs.get("context", "operation_log"),
        )
        return f"Saved memory #{entry['id']}: {entry['key']} = {entry['value']}"

    return f"Unknown tool: {name}"


def process_email(bot, email_body: str) -> str:
    """Send the full email body to Claude, let it call tools, return the reply text."""
    client   = Anthropic()
    messages = [{"role": "user", "content": email_body.strip()}]

    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return " ".join(
                b.text for b in response.content
                if getattr(b, "type", None) == "text"
            ).strip() or "Done."

        if response.stop_reason == "tool_use":
            results = []
            for block in response.content:
                if getattr(block, "type", None) == "tool_use":
                    output = _run_tool(bot, block.name, block.input)
                    results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     output,
                    })
            messages.append({"role": "user", "content": results})
            continue

        break

    return "Something went wrong processing your request."
