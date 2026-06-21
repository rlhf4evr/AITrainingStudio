"""
aitraining.studio — Automated Job Scraper
Pulls $100+/hr RLHF & AI evaluation roles from multiple platforms.
Runs via GitHub Actions on a schedule. Outputs jobs.json for the website.
"""

import json
import re
import os
import hashlib
import requests
from datetime import datetime, timezone
from typing import Optional

# ── CONFIG ─────────────────────────────────────────────────────────────────────

MIN_HOURLY_RATE = 100  # Only include roles at or above this rate

REFERRAL_LINKS = {
    "mercor":  os.getenv("MERCOR_REFERRAL_URL",  "https://work.mercor.com/refer/YOUR_CODE"),
    "micro1":  os.getenv("MICRO1_REFERRAL_URL",  "https://micro1.ai/referral/YOUR_CODE"),
    "terac":   os.getenv("TERAC_REFERRAL_URL",   "https://terac.com/refer/YOUR_CODE"),
    "default": "https://aitraining.studio",
}

HEADERS = {
    "User-Agent": "aitraining.studio job aggregator (hello@aitraining.studio)",
    "Accept": "application/json",
}

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "output", "jobs.json")

# ── HELPERS ────────────────────────────────────────────────────────────────────

def extract_hourly_rate(text: str) -> Optional[float]:
    if not text:
        return None
    text = text.replace(",", "")
    patterns = [
        r"\$(\d+(?:\.\d+)?)\s*[-–to]+\s*\$?(\d+(?:\.\d+)?)\s*(?:/\s*hr|per\s*hour|/hour)",
        r"\$(\d+(?:\.\d+)?)\s*(?:/\s*hr|per\s*hour|/hour)",
        r"(\d+(?:\.\d+)?)\s*(?:USD|usd)\s*(?:/\s*hr|per\s*hour|/hour)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = [float(g) for g in match.groups() if g]
            return max(groups)
    return None


def make_id(platform: str, title: str, url: str) -> str:
    raw = f"{platform}:{title}:{url}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def normalise_job(platform: str, title: str, description: str,
                  rate_text: str, hourly_rate: float, url: str,
                  role_type: str = "", best_for: str = "") -> dict:
    referral_url = REFERRAL_LINKS.get(platform.lower(), REFERRAL_LINKS["default"])
    if platform.lower() == "mercor" and url:
        job_slug = url.rstrip("/").split("/")[-1]
        referral_url = f"{REFERRAL_LINKS['mercor']}?job={job_slug}"

    return {
        "id":           make_id(platform, title, url),
        "platform":     platform,
        "title":        title,
        "description":  description[:300] if description else "",
        "rate_text":    rate_text,
        "hourly_rate":  hourly_rate,
        "role_type":    role_type,
        "best_for":     best_for,
        "referral_url": referral_url,
        "source_url":   url,
        "added_at":     datetime.now(timezone.utc).isoformat(),
        "active":       True,
        "manual":       False,
    }


# ── SCRAPERS ───────────────────────────────────────────────────────────────────

def scrape_mercor() -> list[dict]:
    print("  → Fetching Mercor jobs...")
    jobs = []
    try:
        url = "https://api.work.mercor.com/v2/jobs/search"
        params = {
            "limit": 100,
            "orderBy": "newest",
            "query": "RLHF OR evaluation OR AI training OR data annotation",
        }
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("jobs", []):
            title = item.get("title", "")
            desc  = item.get("description", "") or item.get("shortDescription", "")
            pay   = item.get("payRate", "") or item.get("compensation", "") or ""

            hourly = item.get("hourlyRateUSD") or item.get("minHourlyRate")
            if hourly is None:
                hourly = extract_hourly_rate(str(pay))
            else:
                hourly = float(hourly)

            if hourly is None or hourly < MIN_HOURLY_RATE:
                continue

            job_url = f"https://work.mercor.com/jobs/{item.get('id', '')}"
            jobs.append(normalise_job(
                platform    = "Mercor",
                title       = title,
                description = desc,
                rate_text   = pay or f"${int(hourly)}/hr",
                hourly_rate = hourly,
                url         = job_url,
                role_type   = item.get("category", ""),
                best_for    = item.get("requiredSkills", ""),
            ))

        print(f"     Mercor: {len(jobs)} qualifying roles found")
    except Exception as e:
        print(f"     Mercor scrape failed: {e}")
    return jobs


def scrape_micro1() -> list[dict]:
    print("  → Fetching Micro1 jobs...")
    jobs = []
    try:
        url = "https://api.micro1.ai/v1/jobs/public"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("data", data if isinstance(data, list) else []):
            title = item.get("title", item.get("jobTitle", ""))
            desc  = item.get("description", item.get("jobDescription", ""))
            pay   = str(item.get("salary", item.get("compensation", item.get("rate", ""))))

            hourly = item.get("hourlyRate") or item.get("minRate")
            if hourly is None:
                hourly = extract_hourly_rate(pay)
            else:
                hourly = float(hourly)

            if hourly is None or hourly < MIN_HOURLY_RATE:
                continue

            job_url  = item.get("applyUrl", item.get("url", "https://micro1.ai/jobs"))
            jobs.append(normalise_job(
                platform    = "Micro1",
                title       = title,
                description = desc,
                rate_text   = pay or f"${int(hourly)}/hr",
                hourly_rate = hourly,
                url         = job_url,
            ))

        print(f"     Micro1: {len(jobs)} qualifying roles found")
    except Exception as e:
        print(f"     Micro1 scrape failed: {e}")
    return jobs


def scrape_terac() -> list[dict]:
    print("  → Fetching Terac jobs...")
    jobs = []
    try:
        url = "https://terac.com/api/jobs"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for item in (data if isinstance(data, list) else data.get("jobs", [])):
            title = item.get("title", "")
            desc  = item.get("description", "")
            pay   = str(item.get("pay", item.get("rate", item.get("compensation", ""))))

            hourly = extract_hourly_rate(pay) or extract_hourly_rate(desc)

            if hourly is None or hourly < MIN_HOURLY_RATE:
                continue

            job_url = item.get("url", item.get("link", "https://terac.com"))
            jobs.append(normalise_job(
                platform    = "Terac",
                title       = title,
                description = desc,
                rate_text   = pay or f"${int(hourly)}/hr",
                hourly_rate = hourly,
                url         = job_url,
            ))

        print(f"     Terac: {len(jobs)} qualifying roles found")
    except Exception as e:
        print(f"     Terac scrape failed: {e}")
    return jobs


# ── DEDUPLICATION & MERGE ──────────────────────────────────────────────────────

def merge_with_existing(new_jobs: list[dict]) -> list[dict]:
    """
    Load existing jobs.json, preserve manual jobs, merge scraped jobs.
    Manual jobs (manual=true) are NEVER deactivated by the scraper.
    """
    existing = {}
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH) as f:
            for job in json.load(f).get("jobs", []):
                existing[job["id"]] = job

    new_ids = {j["id"] for j in new_jobs}

    # Only deactivate scraped jobs — never touch manual ones
    for job_id, job in existing.items():
        if job.get("manual"):
            continue
        if job_id not in new_ids and job.get("active"):
            job["active"] = False

    # Upsert new scraped jobs
    for job in new_jobs:
        existing[job["id"]] = job

    all_jobs = sorted(existing.values(), key=lambda j: j["hourly_rate"], reverse=True)
    return all_jobs


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    print(f"\n🤖 aitraining.studio job scraper — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Minimum rate: ${MIN_HOURLY_RATE}/hr\n")

    all_new = []
    all_new.extend(scrape_mercor())
    all_new.extend(scrape_micro1())
    all_new.extend(scrape_terac())

    print(f"\n✅ Total qualifying new roles: {len(all_new)}")

    merged = merge_with_existing(all_new)
    active = [j for j in merged if j["active"]]

    output = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_active": len(active),
        "min_hourly_rate": MIN_HOURLY_RATE,
        "jobs": merged,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"📄 Saved {len(merged)} jobs ({len(active)} active) → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
