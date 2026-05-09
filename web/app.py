import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from main import build_bot
from src import memory

app = Flask(__name__)
app.secret_key = os.environ.get("CLAWBOT_SECRET_KEY", "clawbot-dev-secret-change-in-prod")

ACCESS_KEY = os.environ.get("CLAWBOT_ACCESS_KEY", "clawbot123")

bot = build_bot()


def is_subscriber():
    return session.get("subscriber") is True


@app.route("/")
def index():
    memories = memory.all_memories()
    last_analysis = memory.recall("last_analysis")
    last_error = memory.recall("last_error")
    return render_template(
        "index.html",
        memories=memories,
        last_analysis=last_analysis,
        last_error=last_error,
        subscriber=is_subscriber(),
    )


@app.route("/login", methods=["POST"])
def login():
    key = (request.get_json() or {}).get("key", "").strip()
    if key == ACCESS_KEY:
        session["subscriber"] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Invalid access key"}), 401


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("subscriber", None)
    return jsonify({"ok": True})


@app.route("/command", methods=["POST"])
def run_command():
    if not is_subscriber():
        return jsonify({"error": "Subscriber access required to run commands."}), 403
    data = request.get_json()
    command_text = (data or {}).get("command", "").strip()
    if not command_text:
        return jsonify({"error": "No command provided"}), 400
    result = bot.execute(command_text)
    return jsonify({"result": result})


@app.route("/status")
def get_status():
    all_mems = memory.all_memories()
    last_analysis = memory.recall("last_analysis")
    last_error = memory.recall("last_error")
    return jsonify({
        "memory_count": len(all_mems),
        "last_analysis_date": last_analysis["timestamp"][:10] if last_analysis else None,
        "last_analysis_result": last_analysis["value"]["result"] if last_analysis else None,
        "last_error": last_error["value"]["error"] if last_error else None,
        "subscriber": is_subscriber(),
    })


@app.route("/history")
def get_history():
    entries = memory.recall_all("calibration_history")
    return jsonify([
        {
            "timestamp": e["timestamp"],
            "date": e["timestamp"][:10],
            **e["value"],
        }
        for e in entries
    ])


@app.route("/memories")
def get_memories():
    context = request.args.get("context")
    entries = memory.recall_by_context(context) if context else memory.all_memories()
    return jsonify(entries)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
