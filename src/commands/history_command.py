from src import memory


class HistoryCommand:
    """HISTORY  — show a summary table of all past calibration runs."""

    def execute(self, command_text):
        entries = memory.recall_all("calibration_history")
        if not entries:
            return "No calibration history found. Run an ANALYZE command to start tracking."

        lines = [
            f"Calibration History — {len(entries)} run(s)",
            "",
            f"{'#':<4} {'Date':<12} {'Max Err':>8} {'Mean Err':>9} {'RMS Err':>8} {'Pts':>4}  Precision",
            "-" * 62,
        ]
        for i, e in enumerate(entries, 1):
            v = e["value"]
            date = e["timestamp"][:10]
            lines.append(
                f"{i:<4} {date:<12} {v['max_error']:>8.3f} {v['mean_error']:>9.3f} "
                f"{v['rms_error']:>8.3f} {v['n_points']:>4}  ±{v['precision']} mm"
            )

        # Simple trend note
        if len(entries) >= 2:
            first = entries[0]["value"]["mean_error"]
            last  = entries[-1]["value"]["mean_error"]
            delta = last - first
            direction = "▲ worsening" if delta > 0.01 else "▼ improving" if delta < -0.01 else "→ stable"
            lines += ["", f"Trend: {direction}  (mean error {first:.3f} → {last:.3f} mm)"]

        return "\n".join(lines)


def setup(bot):
    bot.add_command(HistoryCommand())
