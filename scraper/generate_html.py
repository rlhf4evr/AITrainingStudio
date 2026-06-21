"""
aitraining.studio — Job Board HTML Generator
Converts jobs.json → jobs.html for embedding in Squarespace via Code Block.
"""

import json
import os
from datetime import datetime, timezone

INPUT_PATH  = os.path.join(os.path.dirname(__file__), "..", "output", "jobs.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "output", "jobs.html")

EMOJI_MAP = {
    "medical": "⚕️", "clinical": "⚕️", "health": "⚕️", "pharma": "⚕️",
    "legal": "⚖️", "law": "⚖️", "attorney": "⚖️",
    "code": "💻", "engineer": "💻", "software": "💻", "developer": "💻", "programming": "💻",
    "math": "🧮", "stem": "📐", "science": "🔬", "research": "🔬",
    "finance": "📊", "financial": "📊", "economics": "📊",
    "red team": "🔴", "safety": "🛡️", "security": "🔴",
    "writing": "✍️", "content": "✍️",
    "reasoning": "🧠", "rlhf": "🧠", "evaluation": "🧠", "training": "🧠",
}

def get_emoji(title: str, role_type: str = "") -> str:
    text = (title + " " + role_type).lower()
    for keyword, emoji in EMOJI_MAP.items():
        if keyword in text:
            return emoji
    return "🤖"


def format_rate(job: dict) -> str:
    rate = job.get("rate_text", "")
    hr   = job.get("hourly_rate", 0)
    if rate and "$" in rate:
        return rate
    return f"${int(hr)}/hr" if hr else "Rate upon application"


def build_card(job: dict) -> str:
    emoji    = get_emoji(job["title"], job.get("role_type", ""))
    rate     = format_rate(job)
    platform = job["platform"]
    title    = job["title"]
    desc     = job.get("description", "")[:180] + ("…" if len(job.get("description","")) > 180 else "")
    ref_url  = job["referral_url"]
    best_for = job.get("best_for", "")

    best_for_html = f'<p class="best-for">Best for: {best_for}</p>' if best_for else ""

    return f"""
    <div class="job-card">
      <div class="job-header">
        <span class="job-emoji">{emoji}</span>
        <div class="job-meta">
          <h3 class="job-title">{title}</h3>
          <span class="job-platform">Vetted AI Platform · Remote · Flexible</span>
        </div>
        <span class="job-rate">{rate}</span>
      </div>
      {f'<p class="job-desc">{desc}</p>' if desc else ''}
      {best_for_html}
      <a class="apply-btn" href="{ref_url}" target="_blank" rel="noopener noreferrer">
        Apply via Referral →
      </a>
    </div>"""


def generate_html(jobs: list[dict], last_updated: str, total_active: int) -> str:
    updated_str = datetime.fromisoformat(last_updated).strftime("%-d %B %Y, %-I:%M %p UTC")
    cards_html  = "\n".join(build_card(j) for j in jobs if j.get("active"))

    if not cards_html:
        cards_html = """
        <div class="no-jobs">
          <p>🔍 We're currently reviewing new roles. Check back soon — or follow us on LinkedIn for instant alerts.</p>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Training Studio — Open Roles</title>
  <style>
    /* ── Reset & base ── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: transparent;
      color: #1a1a1a;
    }}

    /* ── Header bar ── */
    .board-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 0 24px 0;
      border-bottom: 1px solid #e5e5e5;
      margin-bottom: 32px;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .board-title {{
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #666;
    }}
    .board-meta {{
      font-size: 12px;
      color: #999;
    }}
    .board-count {{
      background: #1a1a1a;
      color: #fff;
      padding: 4px 12px;
      border-radius: 100px;
      font-size: 12px;
      font-weight: 600;
    }}

    /* ── Filter tabs ── */
    .filter-bar {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 28px;
    }}
    .filter-btn {{
      background: #f3f3f3;
      border: none;
      padding: 8px 16px;
      border-radius: 100px;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.15s;
      font-family: inherit;
      color: #444;
    }}
    .filter-btn:hover, .filter-btn.active {{
      background: #1a1a1a;
      color: #fff;
    }}

    /* ── Job cards ── */
    .job-grid {{
      display: grid;
      gap: 16px;
    }}

    .job-card {{
      background: #fff;
      border: 1px solid #e8e8e8;
      border-radius: 16px;
      padding: 24px;
      transition: box-shadow 0.2s, transform 0.15s;
    }}
    .job-card:hover {{
      box-shadow: 0 8px 32px rgba(0,0,0,0.08);
      transform: translateY(-2px);
    }}

    .job-header {{
      display: flex;
      align-items: flex-start;
      gap: 16px;
      margin-bottom: 14px;
    }}
    .job-emoji {{
      font-size: 28px;
      line-height: 1;
      flex-shrink: 0;
    }}
    .job-meta {{
      flex: 1;
      min-width: 0;
    }}
    .job-title {{
      font-size: 17px;
      font-weight: 700;
      color: #1a1a1a;
      line-height: 1.3;
      margin-bottom: 4px;
    }}
    .job-platform {{
      font-size: 12px;
      color: #888;
      font-weight: 500;
    }}
    .job-rate {{
      background: #f0faf0;
      color: #1a7a3c;
      font-weight: 800;
      font-size: 15px;
      padding: 6px 14px;
      border-radius: 8px;
      white-space: nowrap;
      flex-shrink: 0;
    }}

    .job-desc {{
      font-size: 14px;
      color: #555;
      line-height: 1.6;
      margin-bottom: 12px;
    }}
    .best-for {{
      font-size: 12px;
      color: #888;
      margin-bottom: 16px;
    }}
    .best-for::before {{ content: "✓ "; color: #1a7a3c; }}

    .apply-btn {{
      display: inline-block;
      background: #1a1a1a;
      color: #fff;
      text-decoration: none;
      padding: 10px 22px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      transition: background 0.15s;
    }}
    .apply-btn:hover {{
      background: #333;
    }}

    /* ── Empty state ── */
    .no-jobs {{
      text-align: center;
      padding: 60px 20px;
      background: #f9f9f9;
      border-radius: 16px;
      color: #666;
      font-size: 15px;
      line-height: 1.6;
    }}

    /* ── Footer note ── */
    .board-footer {{
      margin-top: 32px;
      padding-top: 20px;
      border-top: 1px solid #e5e5e5;
      font-size: 12px;
      color: #aaa;
      text-align: center;
      line-height: 1.6;
    }}

    /* ── Mobile ── */
    @media (max-width: 600px) {{
      .job-header {{ flex-wrap: wrap; }}
      .job-rate {{ order: -1; }}
      .board-header {{ flex-direction: column; align-items: flex-start; }}
    }}
  </style>
</head>
<body>

  <div class="board-header">
    <div>
      <div class="board-title">Current Openings</div>
    </div>
    <div style="display:flex; gap:12px; align-items:center;">
      <span class="board-count">{total_active} active roles</span>
      <span class="board-meta">Updated {updated_str}</span>
    </div>
  </div>

  <div class="filter-bar">
    <button class="filter-btn active" onclick="filterJobs('all', this)">All Roles</button>
    <button class="filter-btn" onclick="filterJobs('medical', this)">⚕️ Medical</button>
    <button class="filter-btn" onclick="filterJobs('legal', this)">⚖️ Legal</button>
    <button class="filter-btn" onclick="filterJobs('code', this)">💻 Engineering</button>
    <button class="filter-btn" onclick="filterJobs('research', this)">🔬 Research</button>
    <button class="filter-btn" onclick="filterJobs('rlhf', this)">🧠 RLHF</button>
  </div>

  <div class="job-grid" id="job-grid">
    {cards_html}
  </div>

  <div class="board-footer">
    All roles listed pay $100/hr or above · Applying is always free · AI Training Studio is an independent curator, not affiliated with any platform listed
  </div>

  <script>
    function filterJobs(category, btn) {{
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const cards = document.querySelectorAll('.job-card');
      cards.forEach(card => {{
        if (category === 'all') {{
          card.style.display = '';
        }} else {{
          const text = card.innerText.toLowerCase();
          card.style.display = text.includes(category) ? '' : 'none';
        }}
      }});
    }}
  </script>

</body>
</html>"""


def main():
    print(f"\n🎨 Generating job board HTML...")

    with open(INPUT_PATH) as f:
        data = json.load(f)

    jobs         = data.get("jobs", [])
    last_updated = data.get("last_updated", datetime.now(timezone.utc).isoformat())
    total_active = data.get("total_active", sum(1 for j in jobs if j.get("active")))

    html = generate_html(jobs, last_updated, total_active)

    with open(OUTPUT_PATH, "w") as f:
        f.write(html)

    print(f"✅ Generated {OUTPUT_PATH} ({len([j for j in jobs if j.get('active')])} active jobs)")


if __name__ == "__main__":
    main()
