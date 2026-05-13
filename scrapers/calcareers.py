import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, city_to_region, today

SEARCH_URL = "https://www.calcareers.ca.gov/CalHRPublic/Search/JobSearchResults.aspx"

# Keywords to search on CalCareers
SEARCHES = [
    ("correctional officer",    "Law Enforcement & Security"),
    ("peace officer",           "Law Enforcement & Security"),
    ("highway patrol",          "Law Enforcement & Security"),
    ("park ranger",             "Law Enforcement & Security"),
    ("social worker",           "Healthcare & Medical"),
    ("registered nurse",        "Healthcare & Medical"),
    ("engineer",                "Robotics & Automation"),
    ("warehouse",               "Logistics & Warehouse"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CalcoJobsBot/1.0)"
}


class CalCareersScraper(BaseScraper):
    name = "calcareers"

    def _search(self, keyword: str, category: str) -> list[dict]:
        params = {
            "Keywords": keyword,
            "Location": "California",
        }
        try:
            r = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")
        except Exception as e:
            print(f"[calcareers] '{keyword}' error: {e}")
            return []

        jobs = []
        # CalCareers job rows are in a table with class "SearchResultsTable"
        rows = soup.select("table.SearchResultsTable tr")[1:11]  # skip header, max 10
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            try:
                title_cell = cells[0]
                title = title_cell.get_text(strip=True)
                link  = title_cell.find("a")
                url   = ("https://www.calcareers.ca.gov" + link["href"]) if link else SEARCH_URL

                dept   = cells[1].get_text(strip=True) if len(cells) > 1 else "State of California"
                location_text = cells[2].get_text(strip=True) if len(cells) > 2 else "Sacramento"
                city   = location_text.split(",")[0].strip()
                salary = cells[3].get_text(strip=True) if len(cells) > 3 else "State Pay Scale"

                jobs.append({
                    "title": title,
                    "company": dept,
                    "city": city,
                    "region": city_to_region(city),
                    "type": "Full-Time",
                    "category": category,
                    "salary": salary,
                    "posted": today(),
                    "tags": ["state", "california", keyword.split()[0].lower()],
                    "description": f"California state government position: {title} with {dept}. Visit the link to view full job description and requirements.",
                    "url": url,
                    "source": "calcareers",
                })
            except Exception:
                continue
        return jobs

    def fetch(self) -> list[dict]:
        all_jobs = []
        for keyword, category in SEARCHES:
            all_jobs.extend(self._search(keyword, category))
        return all_jobs
