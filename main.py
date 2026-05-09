import sys
import traceback

from src import memory


COMMAND_ROUTING = [
    ("ANALYZE",    "ScienceAnalysisCommand"),
    ("HISTORY",    "HistoryCommand"),
    ("SET",        "SetMemoryCommand"),
    ("GET",        "GetMemoryCommand"),
    ("LIST MEMOR", "ListMemoryCommand"),
    ("FORGET",     "ForgetMemoryCommand"),
    ("HELP",       "HelpCommand"),
]


class ClawbotCommandRegistry:
    def __init__(self):
        self._commands = {}

    def add_command(self, command):
        self._commands[type(command).__name__] = command

    def execute(self, command_text):
        upper = command_text.strip().upper()

        if upper.startswith("RECALL"):
            return self._handle_recall()

        for prefix, command_key in COMMAND_ROUTING:
            if upper.startswith(prefix):
                if command_key not in self._commands:
                    return f"Command '{command_key}' is registered but not loaded."
                try:
                    result = self._commands[command_key].execute(command_text)
                except Exception as e:
                    return self._handle_error(command_text, e)

                if command_key == "ScienceAnalysisCommand":
                    memory.remember(
                        key="last_analysis",
                        value={"command": command_text, "result": result},
                        context="operation_log",
                    )
                    cmd_obj = self._commands[command_key]
                    try:
                        parsed = cmd_obj.parse_one_line_command(command_text)
                        errors = cmd_obj.calculate_errors(parsed["expected"], parsed["actual"])
                        memory.remember(
                            key="calibration_history",
                            value={
                                "command": command_text,
                                "max_error": round(errors["max"], 4),
                                "mean_error": round(errors["mean"], 4),
                                "rms_error": round(errors["rms"], 4),
                                "precision": parsed["precision"],
                                "n_points": len(parsed["actual"]),
                            },
                            context="system_calibration",
                        )
                    except Exception:
                        pass
                return result

        return (
            "Unknown command. Type HELP to see available commands."
        )

    def _handle_recall(self):
        mem = memory.recall("last_analysis")
        if not mem:
            return "No previous analysis found in memory."
        return (
            f"[Memory #{mem['id']} — {mem['timestamp']}]\n"
            f"Command : {mem['value']['command']}\n\n"
            f"{mem['value']['result']}"
        )

    def _handle_error(self, command_text, exc):
        error_msg = f"{type(exc).__name__}: {exc}"
        try:
            memory.remember(
                key="last_error",
                value={"command": command_text, "error": error_msg},
                context="error_log",
            )
        except Exception:
            pass
        return f"Error: {error_msg}"

    def list_commands(self):
        return list(self._commands)


def build_bot():
    bot = ClawbotCommandRegistry()

    from src.commands.science_analysis import setup as setup_science
    from src.commands.memory_commands import setup as setup_memory
    from src.commands.help_command import setup as setup_help
    from src.commands.history_command import setup as setup_history
    setup_science(bot)
    setup_memory(bot)
    setup_help(bot)
    setup_history(bot)

    return bot


def run_interactive(bot):
    print("Clawbot ready. Type HELP for available commands or 'quit' to exit.\n")

    while True:
        try:
            text = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nShutting down.")
            break

        if not text:
            continue
        if text.lower() in ("quit", "exit"):
            print("Shutting down.")
            break

        print(bot.execute(text))
        print()


if __name__ == "__main__":
    bot = build_bot()

    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        print(bot.execute(command))
    else:
        run_interactive(bot)
