import os
import requests
from .base import BaseScraper, city_to_region, today

BASE_URL  = "https://api.adzuna.com/v1/api/jobs/us/search/1"
APP_ID    = os.environ.get("ADZUNA_APP_ID", "")
APP_KEY   = os.environ.get("ADZUNA_APP_KEY", "")

SEARCHES = [
    ("robotics engineer",          "California", "Robotics & Automation"),
    ("automation engineer PLC",    "California", "Robotics & Automation"),
    ("embedded software engineer", "California", "Software & Embedded"),
    ("software engineer",          "Los Angeles", "Software & Embedded"),
    ("software engineer",          "San Francisco", "Software & Embedded"),
    ("warehouse operations",       "California", "Logistics & Warehouse"),
    ("logistics coordinator",      "California", "Logistics & Warehouse"),
    ("security officer",           "California", "Law Enforcement & Security"),
    ("registered nurse",           "California", "Healthcare & Medical"),
    ("medical technician",         "California", "Healthcare & Medical"),
]


class AdzunaScraper(BaseScraper):
    name = "adzuna"

    def _search(self, keyword: str, location: str, category: str) -> list[dict]:
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": 8,
            "what": keyword,
            "where": location,
            "country": "us",
            "content-type": "application/json",
        }
        try:
            r = requests.get(BASE_URL, params=params, timeout=15)
            r.raise_for_status()
            results = r.json().get("results", [])
        except Exception as e:
            print(f"[adzuna] '{keyword}' error: {e}")
            return []

        jobs = []
        for res in results:
            title   = res.get("title", "").strip()
            company = res.get("company", {}).get("display_name", "Unknown")
            url     = res.get("redirect_url", "")
            desc    = res.get("description", "")[:300].strip()

            loc_area = res.get("location", {}).get("area", [])
            city = loc_area[-1] if loc_area else location
            city = city.split(",")[0].strip()

            salary_min = res.get("salary_min")
            salary_max = res.get("salary_max")
            if salary_min and salary_max:
                salary = f"${int(salary_min):,} – ${int(salary_max):,}"
            elif salary_min:
                salary = f"${int(salary_min):,}+"
            else:
                salary = "Competitive"

            jobs.append({
                "title": title,
                "company": company,
                "city": city,
                "region": city_to_region(city),
                "type": "Full-Time",
                "category": category,
                "salary": salary,
                "posted": today(),
                "tags": keyword.lower().split()[:3],
                "description": desc,
                "url": url,
                "source": "adzuna",
            })
        return jobs

    def fetch(self) -> list[dict]:
        all_jobs = []
        for keyword, location, category in SEARCHES:
            all_jobs.extend(self._search(keyword, location, category))
        return all_jobs
