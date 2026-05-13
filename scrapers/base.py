import json
import os
from datetime import datetime, timezone

JOBS_FILE = os.path.join(os.path.dirname(__file__), "..", "web", "data", "jobs.json")

# Map city names to our four CA regions
CITY_REGION = {
    # Bay Area
    "san francisco": "Bay Area", "oakland": "Bay Area", "san jose": "Bay Area",
    "berkeley": "Bay Area", "fremont": "Bay Area", "sunnyvale": "Bay Area",
    "santa clara": "Bay Area", "mountain view": "Bay Area", "palo alto": "Bay Area",
    "san mateo": "Bay Area", "hayward": "Bay Area", "richmond": "Bay Area",
    "concord": "Bay Area", "walnut creek": "Bay Area", "livermore": "Bay Area",
    "pleasanton": "Bay Area", "san ramon": "Bay Area", "milpitas": "Bay Area",
    # Los Angeles
    "los angeles": "Los Angeles", "long beach": "Los Angeles", "burbank": "Los Angeles",
    "pasadena": "Los Angeles", "glendale": "Los Angeles", "santa monica": "Los Angeles",
    "torrance": "Los Angeles", "compton": "Los Angeles", "inglewood": "Los Angeles",
    "pomona": "Los Angeles", "ontario": "Los Angeles", "anaheim": "Los Angeles",
    "santa ana": "Los Angeles", "irvine": "Los Angeles", "riverside": "Los Angeles",
    "san bernardino": "Los Angeles", "rancho cucamonga": "Los Angeles",
    "oxnard": "Los Angeles", "thousand oaks": "Los Angeles", "ventura": "Los Angeles",
    # San Diego
    "san diego": "San Diego", "chula vista": "San Diego", "oceanside": "San Diego",
    "el cajon": "San Diego", "escondido": "San Diego", "san marcos": "San Diego",
    "vista": "San Diego", "carlsbad": "San Diego", "el centro": "San Diego",
    # Central Valley
    "sacramento": "Central Valley", "fresno": "Central Valley", "stockton": "Central Valley",
    "modesto": "Central Valley", "bakersfield": "Central Valley", "visalia": "Central Valley",
    "merced": "Central Valley", "redding": "Central Valley", "chico": "Central Valley",
    "turlock": "Central Valley", "roseville": "Central Valley", "elk grove": "Central Valley",
}


def city_to_region(city: str) -> str:
    return CITY_REGION.get(city.lower().strip(), "Los Angeles")


def load_jobs() -> list:
    with open(JOBS_FILE) as f:
        return json.load(f)


def save_jobs(jobs: list):
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class BaseScraper:
    name = "base"

    def fetch(self) -> list[dict]:
        raise NotImplementedError

    def run(self) -> list[dict]:
        try:
            jobs = self.fetch()
            print(f"[{self.name}] fetched {len(jobs)} jobs")
            return jobs
        except Exception as e:
            print(f"[{self.name}] error: {e}")
            return []
