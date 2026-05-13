import os
import requests
from .base import BaseScraper, city_to_region, today

API_URL = "https://data.usajobs.gov/api/search"
API_KEY   = os.environ.get("USAJOBS_API_KEY", "")
API_EMAIL = os.environ.get("USAJOBS_EMAIL", "")

# (search keyword, category)
SEARCHES = [
    ("law enforcement police officer",         "Law Enforcement & Security"),
    ("border patrol agent",                    "Law Enforcement & Security"),
    ("criminal investigator special agent",    "Law Enforcement & Security"),
    ("security officer guard",                 "Law Enforcement & Security"),
    ("corrections officer",                    "Law Enforcement & Security"),
    ("robotics automation engineer",           "Robotics & Automation"),
    ("software engineer embedded systems",     "Software & Embedded"),
    ("warehouse logistics operations",         "Logistics & Warehouse"),
    ("registered nurse medical technician",    "Healthcare & Medical"),
]


class USAJobsScraper(BaseScraper):
    name = "usajobs"

    def _headers(self):
        return {
            "Host": "data.usajobs.gov",
            "User-Agent": API_EMAIL,
            "Authorization-Key": API_KEY,
        }

    def _search(self, keyword: str, category: str) -> list[dict]:
        params = {
            "Keyword": keyword,
            "LocationName": "California",
            "ResultsPerPage": 10,
            "DatePosted": 30,
        }
        try:
            r = requests.get(API_URL, headers=self._headers(), params=params, timeout=15)
            r.raise_for_status()
            items = r.json().get("SearchResult", {}).get("SearchResultItems", [])
        except Exception as e:
            print(f"[usajobs] '{keyword}' error: {e}")
            return []

        jobs = []
        for item in items:
            p = item.get("MatchedObjectDescriptor", {})
            title = p.get("PositionTitle", "").strip()
            org   = p.get("OrganizationName", "U.S. Government")
            urls  = p.get("ApplyURI", [])
            url   = urls[0] if urls else "https://www.usajobs.gov"

            locs = p.get("PositionLocation", [])
            city = locs[0].get("CityName", "Sacramento") if locs else "Sacramento"
            city = city.split(",")[0].strip()

            rem = p.get("PositionRemuneration", [{}])
            try:
                lo = int(float(rem[0].get("MinimumRange", 0)))
                hi = int(float(rem[0].get("MaximumRange", 0)))
                salary = f"${lo:,} – ${hi:,}" if lo and hi else "Competitive"
            except Exception:
                salary = "Competitive"

            desc = (
                p.get("UserArea", {})
                 .get("Details", {})
                 .get("JobSummary", "Federal government position in California.")
            )
            desc = desc[:300].strip()

            jobs.append({
                "title": title,
                "company": org,
                "city": city,
                "region": city_to_region(city),
                "type": "Full-Time",
                "category": category,
                "salary": salary,
                "posted": today(),
                "tags": ["federal", "government", keyword.split()[0]],
                "description": desc,
                "url": url,
                "source": "usajobs",
            })
        return jobs

    def fetch(self) -> list[dict]:
        all_jobs = []
        for keyword, category in SEARCHES:
            all_jobs.extend(self._search(keyword, category))
        return all_jobs
