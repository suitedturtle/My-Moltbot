"""
THUCYDIDES [Entity A] vs [Entity B]
Power-shift analysis through Graham Allison's Thucydides Trap framework.
"""
import json
import os
from collections import Counter

JOBS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "web", "data", "jobs.json")

# Known geopolitical origins for key players
KNOWN_ORIGINS = {
    # Chinese robotics / tech
    "DJI": "China", "Unitree": "China", "UBTECH": "China",
    "Meituan": "China", "Geely": "China", "BYD": "China",
    "Huawei": "China", "Xiaomi": "China", "Horizon Robotics": "China",
    # Established industrial incumbents
    "FANUC": "Japan", "KUKA": "Germany", "ABB": "Switzerland",
    "Yaskawa": "Japan", "Rockwell Automation": "US",
    "Honeywell": "US", "Siemens": "Germany",
    # US rising challengers
    "Figure AI": "US", "Boston Dynamics": "US", "Apptronik": "US",
    "Agility Robotics": "US", "Sanctuary AI": "Canada",
    "Skydio": "US", "Nuro": "US", "Viam": "US",
    "1X Technologies": "Norway",
    # Country-level entries for macro analysis
    "United States": "US", "USA": "US", "America": "US",
    "China": "China", "PRC": "China",
    "Japan": "Japan", "Germany": "Germany",
    "Europe": "Europe", "EU": "Europe",
}

# Companies structurally classified as rising powers
RISING_POWERS = {
    "Figure AI", "Apptronik", "1X Technologies", "Agility Robotics",
    "Sanctuary AI", "Unitree", "UBTECH", "Horizon Robotics",
    "Nuro", "Skydio", "Nauticus Robotics", "Overland AI", "Viam",
}

# Pairs whose rivalry gets a geopolitical multiplier
GEOPOLITICAL_RIVALS = {frozenset({"US", "China"})}


def _load_jobs():
    try:
        with open(JOBS_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def _count_jobs(jobs, entity):
    e = entity.lower()
    return sum(1 for j in jobs if e in j.get("company", "").lower())


def _classify(entity, job_count, all_counts):
    if entity in RISING_POWERS:
        return "rising"
    if all_counts:
        top_quartile = sorted(all_counts)[-max(1, len(all_counts) // 4)]
        if job_count >= top_quartile:
            return "established"
    return "rising"


class ThucydidesCommand:
    """THUCYDIDES [A] vs [B] — Thucydides Trap power-shift analysis."""

    def execute(self, command_text):
        body = command_text.strip()
        for prefix in ("THUCYDIDES TRAP", "THUCYDIDES"):
            if body.upper().startswith(prefix):
                body = body[len(prefix):].strip()
                break

        # Parse "A vs B"
        idx = body.lower().find(" vs ")
        if idx == -1:
            return (
                "Usage: THUCYDIDES [Entity A] vs [Entity B]\n"
                "Examples:\n"
                "  THUCYDIDES Figure AI vs FANUC\n"
                "  THUCYDIDES United States vs China\n"
                "  THUCYDIDES Boston Dynamics vs KUKA"
            )

        entity_a = body[:idx].strip()
        entity_b = body[idx + 4:].strip()
        if not entity_a or not entity_b:
            return "Please name both entities: THUCYDIDES [A] vs [B]"

        jobs   = _load_jobs()
        jobs_a = _count_jobs(jobs, entity_a)
        jobs_b = _count_jobs(jobs, entity_b)

        all_counts = list(Counter(j.get("company", "") for j in jobs).values())

        role_a = _classify(entity_a, jobs_a, all_counts)
        role_b = _classify(entity_b, jobs_b, all_counts)

        if role_a == "rising" and role_b != "rising":
            rising, established = entity_a, entity_b
            rising_jobs, estab_jobs = jobs_a, jobs_b
        elif role_b == "rising" and role_a != "rising":
            rising, established = entity_b, entity_a
            rising_jobs, estab_jobs = jobs_b, jobs_a
        else:
            rising, established = entity_a, entity_b
            rising_jobs, estab_jobs = jobs_a, jobs_b

        # Momentum ratio
        ratio = min(rising_jobs / estab_jobs, 5.0) if estab_jobs > 0 else (3.0 if rising_jobs > 0 else 0.5)

        origin_a = KNOWN_ORIGINS.get(entity_a, "—")
        origin_b = KNOWN_ORIGINS.get(entity_b, "—")

        # Geopolitical multiplier
        geo_mult = 1.0
        origins = {origin_a, origin_b} - {"—"}
        if len(origins) == 2 and frozenset(origins) in GEOPOLITICAL_RIVALS:
            geo_mult = 1.8

        pressure = min(10.0, round(ratio * 3 + geo_mult * 2, 1))

        if pressure >= 7:
            risk = "HIGH   — structural conflict highly probable"
            marker = "🔴"
        elif pressure >= 4:
            risk = "MODERATE — disruption likely, conflict possible"
            marker = "🟡"
        else:
            risk = "LOW    — coexistence or gradual displacement"
            marker = "🟢"

        lines = [
            "══════════════════════════════════════════",
            "        THUCYDIDES TRAP  ANALYSIS         ",
            "══════════════════════════════════════════",
            "",
            f"  Rising Power  :  {rising}",
            f"  Established   :  {established}",
            "",
            f"  Job Presence  :  {entity_a} ({jobs_a})  ·  {entity_b} ({jobs_b})",
            f"  Origins       :  {entity_a} ({origin_a})  ·  {entity_b} ({origin_b})",
            "",
            "  ─────────────────────────────────────",
            f"  Trap Pressure :  {pressure} / 10",
            f"  Conflict Risk :  {marker}  {risk}",
            "  ─────────────────────────────────────",
            "",
            "  Allison's framework (2017):",
            f"  As {rising} accelerates into {established}'s",
            "  core domain, structural stress builds.",
            f"  {established} faces a choice: accommodate",
            "  or confront — both paths carry risk.",
            "",
        ]

        if geo_mult > 1.0:
            lines += [
                f"  ⚠  U.S.–China rivalry multiplier active ({geo_mult}×)",
                "  Historical base rate: 12 of 16 Thucydides",
                "  cases since 1500 ended in war.",
                "",
            ]

        lines.append("══════════════════════════════════════════")
        return "\n".join(lines)


def setup(bot):
    bot.add_command(ThucydidesCommand())
