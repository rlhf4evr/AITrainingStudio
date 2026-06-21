# 🤖 aitraining.studio — Automated Job Board

Scrapes $100+/hr RLHF & AI evaluation roles from leading platforms,
generates a self-updating HTML job board, and drafts LinkedIn posts.
Runs free on GitHub Actions — no servers required.

---

## How It Works

```
GitHub Actions (2x daily)
        │
        ▼
scrape_jobs.py          ← Pulls jobs from Mercor, Micro1, Terac APIs
        │                  Filters for $100+/hr only
        ▼
output/jobs.json        ← Structured job data (active/inactive, deduped)
        │
        ├── generate_html.py  → output/jobs.html   ← Embed in Squarespace
        │
        └── draft_linkedin.py → output/linkedin_drafts.md  ← Review & post
```

---

## Setup (One Time)

### 1. Create a GitHub repo

```bash
git init aitraining-studio
cd aitraining-studio
# Copy all these files in
git add .
git commit -m "Initial setup"
git remote add origin https://github.com/YOUR_USERNAME/aitraining-studio.git
git push -u origin main
```

### 2. Add your referral URLs as GitHub Secrets

Go to your repo → **Settings → Secrets and Variables → Actions → New repository secret**

| Secret name | Value |
|-------------|-------|
| `MERCOR_REFERRAL_URL` | Your Mercor referral link (from work.mercor.com/refer) |
| `MICRO1_REFERRAL_URL` | Your Micro1 referral link (from micro1.ai/referral-program) |
| `TERAC_REFERRAL_URL`  | Your Terac referral link |

### 3. Enable GitHub Actions

Go to your repo → **Actions** → Click "Enable workflows"

The job will now run automatically every day at 8am and 6pm UTC.
You can also trigger it manually from the Actions tab anytime.

### 4. Enable GitHub Pages (to host jobs.html)

Go to your repo → **Settings → Pages**
- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/output`

Your job board will be live at:
`https://YOUR_USERNAME.github.io/aitraining-studio/jobs.html`

### 5. Embed in Squarespace

1. In Squarespace, go to your **Opportunities** page
2. Add a **Code Block**
3. Paste this iframe (replace the URL with your GitHub Pages URL):

```html
<iframe
  src="https://YOUR_USERNAME.github.io/aitraining-studio/jobs.html"
  width="100%"
  height="900px"
  frameborder="0"
  scrolling="auto"
  style="border:none; border-radius:12px;">
</iframe>
```

The board updates automatically — you never touch Squarespace again.

---

## Adding New Platforms

Open `scraper/scrape_jobs.py` and add a new function:

```python
def scrape_newplatform() -> list[dict]:
    jobs = []
    # ... fetch and filter
    return jobs

# Then add to main():
all_new.extend(scrape_newplatform())
```

Also add the referral URL to `REFERRAL_LINKS` at the top of the file.

---

## LinkedIn Posts

After each run, check `output/linkedin_drafts.md` for ready-to-post drafts.
Each new role gets its own post. Review, tweak tone if needed, then:

**Option A — Manual:** Copy/paste into LinkedIn directly.
**Option B — Buffer:** Connect Buffer to your LinkedIn and schedule posts.
**Option C — Zapier:** Trigger a Zap on file commit to auto-post (advanced).

---

## Files

| File | Purpose |
|------|---------|
| `scraper/scrape_jobs.py` | Pulls and filters jobs from all platforms |
| `scraper/generate_html.py` | Builds the embeddable job board HTML |
| `scraper/draft_linkedin.py` | Drafts LinkedIn posts for new roles |
| `output/jobs.json` | Live job data (auto-updated) |
| `output/jobs.html` | Embeddable job board (auto-updated) |
| `output/linkedin_drafts.md` | Ready-to-post LinkedIn copy |
| `output/posted_ids.json` | Tracks which jobs have been drafted |
| `.github/workflows/update_jobs.yml` | GitHub Actions schedule |

---

## Cost

**$0/month.** GitHub Actions free tier gives 2,000 minutes/month.
This workflow uses ~2 minutes per run × 60 runs/month = ~120 minutes. Well within limits.
