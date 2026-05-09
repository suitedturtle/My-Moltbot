import os
import sys

from src import memory


class ClawbotCommandRegistry:
    def __init__(self):
        self._commands = {}

    def add_command(self, command):
        name = type(command).__name__
        self._commands[name] = command

    def execute(self, command_text):
        upper = command_text.strip().upper()
        if upper.startswith("ANALYZE"):
            key = "ScienceAnalysisCommand"
        elif upper.startswith("RECALL"):
            return self._handle_recall(command_text)
        else:
            return f"Unknown command. Available: {', '.join(self._commands)}"

        if key not in self._commands:
            return f"Command '{key}' is registered but not loaded."

        result = self._commands[key].execute(command_text)

        memory.remember(
            key="last_analysis",
            value={"command": command_text, "result": result},
            context="operation_log",
        )

        return result

    def _handle_recall(self, command_text):
        mem = memory.recall("last_analysis")
        if not mem:
            return "No previous analysis found in memory."
        return (
            f"[Memory #{mem['id']} — {mem['timestamp']}]\n"
            f"Command : {mem['value']['command']}\n\n"
            f"{mem['value']['result']}"
        )

    def list_commands(self):
        return list(self._commands)


def build_bot():
    bot = ClawbotCommandRegistry()

    from src.commands.science_analysis import setup as setup_science
    setup_science(bot)

    return bot


def run_interactive(bot):
    print("Clawbot ready. Type a command or 'quit' to exit.")
    print(f"Loaded commands: {bot.list_commands()}")
    print("Special: RECALL — show last saved analysis\n")

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
