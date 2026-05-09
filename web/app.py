import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request, jsonify
from main import build_bot
from src import memory

app = Flask(__name__)
bot = build_bot()


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
    )


@app.route("/command", methods=["POST"])
def run_command():
    data = request.get_json()
    command_text = (data or {}).get("command", "").strip()
    if not command_text:
        return jsonify({"error": "No command provided"}), 400
    result = bot.execute(command_text)
    return jsonify({"result": result})


@app.route("/memories")
def get_memories():
    context = request.args.get("context")
    entries = memory.recall_by_context(context) if context else memory.all_memories()
    return jsonify(entries)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
