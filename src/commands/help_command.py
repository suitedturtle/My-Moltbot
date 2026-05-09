class HelpCommand:
    HELP_TEXT = """
Clawbot Commands
================

ANALYZE MY CLAWBOT: Expected [0,25,50,75,100] mm → Actual [<values>] mm [±<n>mm]
    Analyze robot measurement accuracy and get a calibration recommendation.

SET <key> = <value> [AS <context>]
    Store a value in memory. Value can be a string, number, or JSON.
    Contexts: user_preference, system_calibration, error_log, operation_log, conversation
    Example: SET preferred_speed = 75 AS user_preference

GET <key>
    Retrieve the most recent memory entry for a key.

LIST MEMORIES [<context>]
    Show all stored memories, optionally filtered by context.

FORGET <key>
    Delete all memory entries for a key.

RECALL
    Show the last saved analysis report.

HISTORY
    Show a summary table of all past calibration runs with error trends.

HELP
    Show this message.
""".strip()

    def execute(self, command_text):
        return self.HELP_TEXT


def setup(bot):
    bot.add_command(HelpCommand())
