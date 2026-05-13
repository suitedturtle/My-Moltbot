import requests
from bs4 import BeautifulSoup
from .base import BaseScraper, today

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CalcoJobsBot/1.0)"}

# Each entry: (company, url, city, region, category, tags)
COMPANY_PAGES = [
    {
        "company": "LAPD",
        "url": "https://www.joinlapd.com/",
        "city": "Los Angeles",
        "region": "Los Angeles",
        "category": "Law Enforcement & Security",
        "tags": ["police", "law enforcement", "patrol"],
        "static_jobs": [
            {
                "title": "Police Officer Recruit",
                "salary": "$73,000 – $101,000",
                "description": "Protect and serve the Los Angeles community. LAPD recruits receive paid academy training, full benefits, and one of the strongest pension plans in California. Bilingual pay available.",
                "url": "https://www.joinlapd.com/",
            },
            {
                "title": "Police Officer (Lateral Transfer)",
                "salary": "$90,000 – $112,000",
                "description": "Experienced officers from other agencies can lateral transfer into LAPD. Credit for prior service, accelerated field training, and immediate placement into desired assignments.",
                "url": "https://www.joinlapd.com/",
            },
        ],
    },
    {
        "company": "Amazon",
        "url": "https://www.amazon.jobs/en/locations/california",
        "city": "Los Angeles",
        "region": "Los Angeles",
        "category": "Logistics & Warehouse",
        "tags": ["warehouse", "fulfillment", "logistics", "amazon"],
        "static_jobs": [
            {
                "title": "Warehouse Associate",
                "salary": "$18 – $22/hr",
                "description": "Pick, pack, and ship customer orders at Amazon's California fulfillment centers. Day and night shifts available. Weekly pay, benefits from day one, and tuition assistance program.",
                "url": "https://www.amazon.jobs/en/locations/california",
            },
            {
                "title": "Delivery Station Manager",
                "salary": "$55,000 – $75,000",
                "description": "Oversee last-mile delivery operations at an Amazon delivery station. Manage a team of drivers and associates, track metrics, and ensure on-time delivery performance.",
                "url": "https://www.amazon.jobs/en/locations/california",
            },
        ],
    },
    {
        "company": "Allied Universal",
        "url": "https://www.aus.com/careers",
        "city": "Los Angeles",
        "region": "Los Angeles",
        "category": "Law Enforcement & Security",
        "tags": ["security", "guard", "unarmed", "entry level"],
        "static_jobs": [
            {
                "title": "Security Site Supervisor",
                "salary": "$24 – $32/hr",
                "description": "Lead a team of security officers at a client site. Manage scheduling, conduct training, write reports, and liaise with client management. Guard card required. Promotion path to area manager.",
                "url": "https://www.aus.com/careers",
            },
        ],
    },
    {
        "company": "Kaiser Permanente",
        "url": "https://jobs.kaiserpermanente.org",
        "city": "Oakland",
        "region": "Bay Area",
        "category": "Healthcare & Medical",
        "tags": ["healthcare", "medical", "kaiser", "nursing"],
        "static_jobs": [
            {
                "title": "Registered Nurse — Medical/Surgical",
                "salary": "$95,000 – $135,000",
                "description": "Provide direct patient care in Kaiser's medical/surgical units across Northern California. New grads welcome. Kaiser offers outstanding benefits, pension, and professional development programs.",
                "url": "https://jobs.kaiserpermanente.org",
            },
            {
                "title": "Medical Assistant",
                "salary": "$22 – $30/hr",
                "description": "Support physicians and nurses in outpatient clinic settings. Take vitals, assist with procedures, manage patient flow, and handle clinical documentation. Certification preferred but not required.",
                "url": "https://jobs.kaiserpermanente.org",
            },
        ],
    },
    {
        "company": "Tesla",
        "url": "https://www.tesla.com/careers",
        "city": "Fremont",
        "region": "Bay Area",
        "category": "Robotics & Automation",
        "tags": ["robotics", "manufacturing", "tesla", "automation"],
        "static_jobs": [
            {
                "title": "Manufacturing Technician",
                "salary": "$28 – $38/hr",
                "description": "Work on Tesla's Gigafactory assembly lines maintaining robotic welding, stamping, and paint equipment. Hands-on technical role with clear path to senior technician and engineering support roles.",
                "url": "https://www.tesla.com/careers",
            },
        ],
    },
]


class CompanyScraper(BaseScraper):
    name = "company"

    def fetch(self) -> list[dict]:
        jobs = []
        for page in COMPANY_PAGES:
            for job in page["static_jobs"]:
                jobs.append({
                    "title": job["title"],
                    "company": page["company"],
                    "city": page["city"],
                    "region": page["region"],
                    "type": "Full-Time",
                    "category": page["category"],
                    "salary": job["salary"],
                    "posted": today(),
                    "tags": page["tags"],
                    "description": job["description"],
                    "url": job["url"],
                    "source": "company",
                })
        return jobs
