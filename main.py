import json
import os
import sys


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
        else:
            return f"Unknown command. Available: {', '.join(self._commands)}"

        if key not in self._commands:
            return f"Command '{key}' is registered but not loaded."

        return self._commands[key].execute(command_text)

    def list_commands(self):
        return list(self._commands.keys())


def build_bot():
    bot = ClawbotCommandRegistry()

    from src.commands.science_analysis import setup as setup_science
    setup_science(bot)

    return bot


def run_interactive(bot):
    print("Clawbot ready. Type a command or 'quit' to exit.")
    print(f"Loaded commands: {bot.list_commands()}\n")

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

        result = bot.execute(text)
        print(result)
        print()


if __name__ == "__main__":
    bot = build_bot()

    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        print(bot.execute(command))
    else:
        run_interactive(bot)
