import sys

from src import memory


COMMAND_ROUTING = [
    ("ANALYZE",       "ScienceAnalysisCommand"),
    ("SET",           "SetMemoryCommand"),
    ("GET",           "GetMemoryCommand"),
    ("LIST MEMOR",    "ListMemoryCommand"),
    ("FORGET",        "ForgetMemoryCommand"),
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
                result = self._commands[command_key].execute(command_text)
                if command_key == "ScienceAnalysisCommand":
                    memory.remember(
                        key="last_analysis",
                        value={"command": command_text, "result": result},
                        context="operation_log",
                    )
                return result

        available = "ANALYZE, SET, GET, LIST MEMORIES, FORGET, RECALL"
        return f"Unknown command. Available: {available}"

    def _handle_recall(self):
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
    from src.commands.memory_commands import setup as setup_memory
    setup_science(bot)
    setup_memory(bot)

    return bot


def run_interactive(bot):
    print("Clawbot ready. Type a command or 'quit' to exit.")
    print("Commands: ANALYZE, SET, GET, LIST MEMORIES, FORGET, RECALL\n")

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
