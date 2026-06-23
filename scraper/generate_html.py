"""
aitraining.studio — Job Board HTML Generator
Converts jobs.json -> jobs.html for embedding in Squarespace via Code Block.
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
    "accounting": "🧾", "audit": "🧾",
    "consulting": "🤝", "consultant": "🤝",
    "business": "💼",
}

CATEGORY_LABELS = {
    "medical": "⚕️ Medical",
    "legal": "⚖️ Legal",
    "code": "💻 Engineering",
    "research": "🔬 Research",
    "rlhf": "🧠 RLHF",
    "finance": "📊 Finance",
    "consulting": "🤝 Consulting",
    "business": "💼 Business",
    "accounting": "🧾 Accounting",
}

def get_emoji(job):
    if job.get("emoji"):
        return job["emoji"]
    text = (job["title"] + " " + job.get("role_type", "")).lower()
    for keyword, emoji in EMOJI_MAP.items():
        if keyword in text:
            return emoji
    return "🤖"

def format_rate(job):
    rate = job.get("rate_text", "")
    hr   = job.get("hourly_rate", 0)
    if rate and "$" in rate:
        return rate
    return f"${int(hr)}/hr" if hr else "Rate upon application"

def build_card(job):
    emoji    = get_emoji(job)
    rate     = format_rate(job)
    title    = job["title"]
    desc     = job.get("description", "")[:180] + ("..." if len(job.get("description","")) > 180 else "")
    ref_url  = job["referral_url"]
    best_for = job.get("best_for", "")
    category = job.get("category", "")
    hourly   = job.get("hourly_rate", 0)
    added_at = job.get("added_at", "")

    best_for_html = f'<p class="best-for">Best for: {best_for}</p>' if best_for else ""
    cat_label = CATEGORY_LABELS.get(category, "")
    cat_badge = f'<span class="cat-badge">{cat_label}</span>' if cat_label else ""

    search_text = (title + " " + best_for + " " + desc).lower().replace('"', '').replace("'", "")

    return f"""
    <div class="job-card" data-category="{category}" data-rate="{hourly}" data-title="{title.lower().replace('"','')}" data-added="{added_at}" data-search="{search_text}">
      <div class="job-header">
        <span class="job-emoji">{emoji}</span>
        <div class="job-meta">
          <h3 class="job-title">{title}</h3>
          <span class="job-platform">Vetted AI Platform · Remote · Flexible</span>
          {cat_badge}
        </div>
        <span class="job-rate">{rate}</span>
      </div>
      {f'<p class="job-desc">{desc}</p>' if desc else ''}
      {best_for_html}
      <a class="apply-btn" href="{ref_url}" target="_blank" rel="noopener noreferrer">Apply &rarr;</a>
    </div>"""


def generate_html(jobs, last_updated, total_active):
    updated_str = datetime.fromisoformat(last_updated).strftime("%-d %B %Y, %-I:%M %p UTC")
    cards_html  = "\n".join(build_card(j) for j in jobs if j.get("active"))

    if not cards_html:
        cards_html = '<div class="no-jobs"><p>We are currently reviewing new roles. Check back soon.</p></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Training Studio - Open Roles</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: transparent; color: #1a1a1a; }}
    .board-header {{ display: flex; justify-content: space-between; align-items: center; padding: 0 0 24px 0; border-bottom: 1px solid #e5e5e5; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }}
    .board-title {{ font-size: 13px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #666; }}
    .board-meta {{ font-size: 12px; color: #999; }}
    .board-count {{ background: #1a1a1a; color: #fff; padding: 4px 12px; border-radius: 100px; font-size: 12px; font-weight: 600; }}
    .controls-bar {{ display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }}
    .search-box {{ flex: 1; min-width: 200px; padding: 9px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; font-family: inherit; outline: none; background: #fafafa; transition: border-color 0.15s; }}
    .search-box:focus {{ border-color: #1a1a1a; background: #fff; }}
    .sort-select {{ padding: 9px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 13px; font-family: inherit; outline: none; background: #fafafa; cursor: pointer; color: #444; }}
    .results-count {{ font-size: 12px; color: #999; white-space: nowrap; }}
    .filter-bar {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }}
    .filter-btn {{ background: #f3f3f3; border: none; padding: 7px 14px; border-radius: 100px; font-size: 13px; cursor: pointer; transition: all 0.15s; font-family: inherit; color: #444; }}
    .filter-btn:hover, .filter-btn.active {{ background: #1a1a1a; color: #fff; }}
    .job-grid {{ display: grid; gap: 16px; }}
    .job-card {{ background: #fff; border: 1px solid #e8e8e8; border-radius: 16px; padding: 24px; transition: box-shadow 0.2s, transform 0.15s; }}
    .job-card:hover {{ box-shadow: 0 8px 32px rgba(0,0,0,0.08); transform: translateY(-2px); }}
    .job-card.hidden {{ display: none; }}
    .job-header {{ display: flex; align-items: flex-start; gap: 16px; margin-bottom: 14px; }}
    .job-emoji {{ font-size: 28px; line-height: 1; flex-shrink: 0; }}
    .job-meta {{ flex: 1; min-width: 0; }}
    .job-title {{ font-size: 17px; font-weight: 700; color: #1a1a1a; line-height: 1.3; margin-bottom: 4px; }}
    .job-platform {{ font-size: 12px; color: #888; font-weight: 500; }}
    .cat-badge {{ display: inline-block; margin-top: 5px; font-size: 11px; color: #666; background: #f3f3f3; padding: 2px 8px; border-radius: 100px; }}
    .job-rate {{ background: #f0faf0; color: #1a7a3c; font-weight: 800; font-size: 15px; padding: 6px 14px; border-radius: 8px; white-space: nowrap; flex-shrink: 0; }}
    .job-desc {{ font-size: 14px; color: #555; line-height: 1.6; margin-bottom: 12px; }}
    .best-for {{ font-size: 12px; color: #888; margin-bottom: 16px; }}
    .best-for::before {{ content: "✓ "; color: #1a7a3c; }}
    .apply-btn {{ display: inline-block; background: #1a1a1a; color: #fff; text-decoration: none; padding: 10px 22px; border-radius: 8px; font-size: 14px; font-weight: 600; transition: background 0.15s; }}
    .apply-btn:hover {{ background: #333; }}
    .no-jobs {{ text-align: center; padding: 60px 20px; background: #f9f9f9; border-radius: 16px; color: #666; font-size: 15px; line-height: 1.6; }}
    .no-results {{ text-align: center; padding: 40px 20px; color: #999; font-size: 14px; display: none; }}
    .board-footer {{ margin-top: 32px; padding-top: 20px; border-top: 1px solid #e5e5e5; font-size: 12px; color: #aaa; text-align: center; line-height: 1.6; }}
    @media (max-width: 600px) {{ .job-header {{ flex-wrap: wrap; }} .job-rate {{ order: -1; }} .board-header {{ flex-direction: column; align-items: flex-start; }} .controls-bar {{ flex-direction: column; }} .search-box, .sort-select {{ width: 100%; }} }}
  </style>
</head>
<body>
  <div class="board-header">
    <div><div class="board-title">Current Openings</div></div>
    <div style="display:flex; gap:12px; align-items:center;">
      <span class="board-count" id="active-count">{total_active} active roles</span>
      <span class="board-meta">Updated {updated_str}</span>
    </div>
  </div>
  <div class="controls-bar">
    <input type="text" class="search-box" id="search-box" placeholder="Search by title, profession, or keyword..." oninput="applyFilters()" />
    <select class="sort-select" id="sort-select" onchange="applyFilters()">
      <option value="rate-desc">Highest Pay First</option>
      <option value="rate-asc">Lowest Pay First</option>
      <option value="newest">Newest First</option>
      <option value="oldest">Oldest First</option>
      <option value="alpha-asc">A to Z</option>
      <option value="alpha-desc">Z to A</option>
      <option value="rate-150">$150+/hr only</option>
      <option value="rate-250">$250+/hr only</option>
    </select>
    <span class="results-count" id="results-count"></span>
  </div>
  <div class="filter-bar">
    <button class="filter-btn active" onclick="setCategory('all', this)">All Roles</button>
    <button class="filter-btn" onclick="setCategory('medical', this)">⚕️ Medical</button>
    <button class="filter-btn" onclick="setCategory('legal', this)">⚖️ Legal</button>
    <button class="filter-btn" onclick="setCategory('code', this)">💻 Engineering</button>
    <button class="filter-btn" onclick="setCategory('research', this)">🔬 Research</button>
    <button class="filter-btn" onclick="setCategory('rlhf', this)">🧠 RLHF</button>
    <button class="filter-btn" onclick="setCategory('finance', this)">📊 Finance</button>
    <button class="filter-btn" onclick="setCategory('consulting', this)">🤝 Consulting</button>
    <button class="filter-btn" onclick="setCategory('business', this)">💼 Business</button>
    <button class="filter-btn" onclick="setCategory('accounting', this)">🧾 Accounting</button>
  </div>
  <div class="job-grid" id="job-grid">
    {cards_html}
  </div>
  <div class="no-results" id="no-results">No roles match your search. Try a different keyword or category.</div>
  <div class="board-footer">All roles listed pay $100/hr or above · Applying is always free · AI Training Studio is an independent curator, not affiliated with any platform listed</div>
  <script>
    let currentCategory = 'all';
    function setCategory(category, btn) {{
      currentCategory = category;
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      applyFilters();
    }}
    function applyFilters() {{
      const query = document.getElementById('search-box').value.toLowerCase().trim();
      const sort = document.getElementById('sort-select').value;
      const grid = document.getElementById('job-grid');
      const cards = Array.from(document.querySelectorAll('.job-card'));
      let visible = cards.filter(card => {{
        const catMatch = currentCategory === 'all' || card.dataset.category === currentCategory;
        const searchMatch = !query || card.dataset.search.includes(query);
        let rateMatch = true;
        if (sort === 'rate-150') rateMatch = parseInt(card.dataset.rate) >= 150;
        if (sort === 'rate-250') rateMatch = parseInt(card.dataset.rate) >= 250;
        return catMatch && searchMatch && rateMatch;
      }});
      cards.forEach(c => c.classList.add('hidden'));
      visible.sort((a, b) => {{
        const rateA = parseInt(a.dataset.rate) || 0;
        const rateB = parseInt(b.dataset.rate) || 0;
        if (sort === 'rate-desc' || sort === 'rate-150' || sort === 'rate-250') return rateB - rateA;
        if (sort === 'rate-asc') return rateA - rateB;
        if (sort === 'newest') return (b.dataset.added || '').localeCompare(a.dataset.added || '');
        if (sort === 'oldest') return (a.dataset.added || '').localeCompare(b.dataset.added || '');
        if (sort === 'alpha-asc') return (a.dataset.title || '').localeCompare(b.dataset.title || '');
        if (sort === 'alpha-desc') return (b.dataset.title || '').localeCompare(a.dataset.title || '');
        return rateB - rateA;
      }});
      visible.forEach(card => {{ card.classList.remove('hidden'); grid.appendChild(card); }});
      document.getElementById('results-count').textContent = visible.length === cards.length ? '' : visible.length + ' of ' + cards.length + ' roles';
      document.getElementById('no-results').style.display = visible.length === 0 ? 'block' : 'none';
    }}
    applyFilters();
  </script>
</body>
</html>"""


def main():
    print("\\nGenerating job board HTML...")
    with open(INPUT_PATH) as f:
        data = json.load(f)
    jobs = sorted(data.get("jobs", []), key=lambda j: j.get("hourly_rate", 0), reverse=True)
    last_updated = data.get("last_updated", datetime.now(timezone.utc).isoformat())
    total_active = data.get("total_active", sum(1 for j in jobs if j.get("active")))
    html = generate_html(jobs, last_updated, total_active)
    with open(OUTPUT_PATH, "w") as f:
        f.write(html)
    print(f"Done! {len([j for j in jobs if j.get('active')])} active jobs")

if __name__ == "__main__":
    main()
