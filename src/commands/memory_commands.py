import json
import re

from src import memory

VALID_CONTEXTS = sorted(memory.VALID_CONTEXTS)


class SetMemoryCommand:
    """SET key = value [as context]  — store a value in memory."""

    def execute(self, command_text):
        # SET key = value [as context]
        match = re.match(
            r'SET\s+(\w+)\s*=\s*(.+?)(?:\s+AS\s+(\w+))?\s*$',
            command_text.strip(),
            re.IGNORECASE,
        )
        if not match:
            return (
                "Usage: SET <key> = <value> [AS <context>]\n"
                f"Contexts: {', '.join(VALID_CONTEXTS)}"
            )

        key = match.group(1).lower()
        raw_value = match.group(2).strip()
        context = (match.group(3) or "user_preference").lower()

        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            value = raw_value

        try:
            entry = memory.remember(key, value, context)
        except ValueError as e:
            return f"Error: {e}"

        return f"Saved: {key} = {json.dumps(value)} (context: {context}, id: {entry['id']})"


class GetMemoryCommand:
    """GET key  — retrieve the most recent value for a key."""

    def execute(self, command_text):
        match = re.match(r'GET\s+(\w+)\s*$', command_text.strip(), re.IGNORECASE)
        if not match:
            return "Usage: GET <key>"

        key = match.group(1).lower()
        entry = memory.recall(key)

        if not entry:
            return f"No memory found for key '{key}'."

        return (
            f"[#{entry['id']} — {entry['timestamp']}]\n"
            f"Key     : {entry['key']}\n"
            f"Value   : {json.dumps(entry['value'])}\n"
            f"Context : {entry['context']}"
        )


class ListMemoryCommand:
    """LIST MEMORIES [context]  — show all stored memories, optionally filtered."""

    def execute(self, command_text):
        match = re.match(r'LIST\s+MEMORIES?(?:\s+(\w+))?\s*$', command_text.strip(), re.IGNORECASE)
        if not match:
            return "Usage: LIST MEMORIES [context]"

        context_filter = (match.group(1) or "").lower()

        if context_filter:
            entries = memory.recall_by_context(context_filter)
            header = f"Memories (context: {context_filter})"
        else:
            entries = memory.all_memories()
            header = "All memories"

        if not entries:
            return f"No memories found{' for context: ' + context_filter if context_filter else ''}."

        lines = [f"{header} — {len(entries)} entries:", ""]
        for e in entries:
            lines.append(
                f"  #{e['id']:>3}  [{e['context']}]  {e['key']} = {json.dumps(e['value'])}  ({e['timestamp']})"
            )
        return "\n".join(lines)


class ForgetMemoryCommand:
    """FORGET key  — delete all memory entries for a key."""

    def execute(self, command_text):
        match = re.match(r'FORGET\s+(\w+)\s*$', command_text.strip(), re.IGNORECASE)
        if not match:
            return "Usage: FORGET <key>"

        key = match.group(1).lower()
        removed = memory.forget(key)

        if removed == 0:
            return f"No memories found for key '{key}'."
        return f"Removed {removed} memory {'entries' if removed != 1 else 'entry'} for key '{key}'."


def setup(bot):
    bot.add_command(SetMemoryCommand())
    bot.add_command(GetMemoryCommand())
    bot.add_command(ListMemoryCommand())
    bot.add_command(ForgetMemoryCommand())
