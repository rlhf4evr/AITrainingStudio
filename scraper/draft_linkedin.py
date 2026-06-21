"""
aitraining.studio — LinkedIn Post Drafter
For each new $100+/hr role found, generates a ready-to-post LinkedIn update.
Saves drafts to output/linkedin_drafts.md — you review and post manually (or schedule via Buffer).
"""

import json
import os
import random
from datetime import datetime, timezone

INPUT_PATH  = os.path.join(os.path.dirname(__file__), "..", "output", "jobs.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "output", "linkedin_drafts.md")
POSTED_PATH = os.path.join(os.path.dirname(__file__), "..", "output", "posted_ids.json")

# ── TEMPLATES ──────────────────────────────────────────────────────────────────

HOOKS = [
    "Most people have no idea this type of work exists.",
    "AI companies are quietly paying $100–$250/hr for this.",
    "If you have domain expertise, this is worth 5 minutes of your time.",
    "The highest-paying remote work right now isn't in traditional tech jobs.",
    "I found another one. This one pays {rate}.",
    "Stop scrolling. If you're a {role_hint}, read this.",
    "A new high-pay AI role just dropped. Here's the breakdown.",
    "Flexible. Remote. {rate}. Let me explain what this actually involves.",
]

CLOSERS = [
    "→ Referral link in comments.\n\nFollow AI Training Studio for more — I post these as soon as they go live.",
    "→ Direct referral link below. No fees, no middleman.\n\n#RLHF #AIJobs #RemoteWork #AITraining",
    "→ Link to apply in comments. Takes under 5 minutes.\n\nRepost if you know someone this would suit 🔁",
    "→ Referral link in comments — fastest way in.\n\nFollow for weekly $100+/hr AI role drops. 📌",
]

ROLE_HINTS = {
    "medical": "doctor, nurse, or medical professional",
    "legal": "lawyer or legal professional",
    "code": "software engineer or developer",
    "research": "researcher or scientist",
    "finance": "finance professional",
    "rlhf": "domain expert",
    "reasoning": "analytical professional",
}


def get_role_hint(title: str) -> str:
    title_lower = title.lower()
    for key, hint in ROLE_HINTS.items():
        if key in title_lower:
            return hint
    return "professional with domain expertise"


def draft_post(job: dict) -> str:
    title    = job["title"]
    rate     = job.get("rate_text", f"${int(job.get('hourly_rate', 100))}/hr")
    ref_url  = job["referral_url"]
    platform = job["platform"]
    desc     = job.get("description", "")[:200]
    role_hint = get_role_hint(title)

    hook   = random.choice(HOOKS).format(rate=rate, role_hint=role_hint)
    closer = random.choice(CLOSERS)

    body_parts = [
        f"📋 Role: {title}",
        f"💰 Rate: {rate}",
        f"🌐 Type: Remote · Flexible hours · No office",
        f"🏷️ Platform: Vetted AI training network",
    ]

    if desc:
        body_parts.append(f"\nWhat the work involves:\n{desc}")

    body_parts += [
        "\nWho should apply:",
        f"✓ {role_hint.capitalize()}",
        "✓ Available 5–20 hrs/week",
        "✓ Based in the US",
        "\nNo AI experience needed. Your domain expertise is the qualification.",
    ]

    post = f"""{hook}

{chr(10).join(body_parts)}

{closer}

— — —
Referral link: {ref_url}
"""
    return post.strip()


def main():
    print(f"\n✍️  Drafting LinkedIn posts for new roles...")

    # Load jobs
    with open(INPUT_PATH) as f:
        data = json.load(f)
    jobs = [j for j in data.get("jobs", []) if j.get("active")]

    # Load already-posted IDs
    posted = set()
    if os.path.exists(POSTED_PATH):
        with open(POSTED_PATH) as f:
            posted = set(json.load(f))

    new_jobs = [j for j in jobs if j["id"] not in posted]

    if not new_jobs:
        print("   No new roles to draft posts for.")
        return

    # Generate drafts
    drafts = []
    for job in new_jobs:
        post = draft_post(job)
        drafts.append({
            "job_id":    job["id"],
            "job_title": job["title"],
            "rate":      job.get("rate_text", ""),
            "post":      post,
            "drafted_at": datetime.now(timezone.utc).isoformat(),
        })

    # Write to markdown file
    lines = [
        f"# LinkedIn Post Drafts — {datetime.now().strftime('%Y-%m-%d')}",
        f"*{len(drafts)} new draft(s) — review and schedule via Buffer or LinkedIn*",
        "",
    ]
    for i, d in enumerate(drafts, 1):
        lines += [
            f"---",
            f"## Draft {i}: {d['job_title']} · {d['rate']}",
            f"*Job ID: {d['job_id']}*",
            "",
            "```",
            d["post"],
            "```",
            "",
        ]

    with open(OUTPUT_PATH, "w") as f:
        f.write("\n".join(lines))

    # Mark as posted (they're drafted — mark them so we don't re-draft)
    new_posted = posted | {d["job_id"] for d in drafts}
    with open(POSTED_PATH, "w") as f:
        json.dump(list(new_posted), f)

    print(f"✅ {len(drafts)} LinkedIn draft(s) saved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
