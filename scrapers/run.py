"""
Run all scrapers and merge new jobs into web/data/jobs.json.
Existing jobs are kept; new jobs are appended (deduplicated by URL).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scrapers.base import load_jobs, save_jobs
from scrapers.usajobs import USAJobsScraper
from scrapers.adzuna import AdzunaScraper
from scrapers.calcareers import CalCareersScraper
from scrapers.company import CompanyScraper


def run_all() -> dict:
    existing = load_jobs()
    existing_urls = {j["url"] for j in existing}
    next_id = max((j["id"] for j in existing), default=0) + 1

    scrapers = [
        CompanyScraper(),       # no API key needed — runs always
        CalCareersScraper(),    # no API key needed — runs always
        USAJobsScraper(),       # needs USAJOBS_API_KEY + USAJOBS_EMAIL
        AdzunaScraper(),        # needs ADZUNA_APP_ID + ADZUNA_APP_KEY
    ]

    new_jobs = []
    scraper_results = {}

    for scraper in scrapers:
        fetched = scraper.run()
        added = 0
        for job in fetched:
            url = job.get("url", "")
            if url and url not in existing_urls:
                job["id"] = next_id
                next_id += 1
                existing_urls.add(url)
                new_jobs.append(job)
                added += 1
        scraper_results[scraper.name] = added
        print(f"[run] {scraper.name}: {added} new jobs added")

    if new_jobs:
        save_jobs(existing + new_jobs)
        print(f"[run] saved {len(existing + new_jobs)} total jobs ({len(new_jobs)} new)")
    else:
        print("[run] no new jobs found")

    return {
        "new_jobs": len(new_jobs),
        "total_jobs": len(existing) + len(new_jobs),
        "by_scraper": scraper_results,
    }


if __name__ == "__main__":
    result = run_all()
    print(result)
