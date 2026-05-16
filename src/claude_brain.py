import os
import urllib.request
import urllib.error
import json
from src import memory

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are Clawbot, an intelligent assistant trained by Claude. 
You help with public safety job searches, CDCR knowledge, and automation tasks.
Be concise, direct, and helpful. You remember past interactions."""

def ask_claude(question, context="conversation"):
    if not ANTHROPIC_API_KEY:
        return "Clawbot brain is offline — API key not configured."

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": question}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            answer = data["content"][0]["text"]
            memory.remember("last_claude_response", {
                "question": question,
                "answer": answer
            }, context=context)
            return answer
    except urllib.error.HTTPError as e:
        error_msg = f"Brain error: {e.code} {e.reason}"
        memory.remember("last_error", {"error": error_msg}, context="error_log")
        return error_msg
    except Exception as e:
        return f"Brain error: {str(e)}"
