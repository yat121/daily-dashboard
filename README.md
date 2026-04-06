# Daily Dashboard

A personal command-center dashboard for tracking daily standups, weather, crypto prices, tech news, and your schedule — all in one place.

**Live Demo:** https://yat121.github.io/daily-dashboard/

---

## Features

- **Daily standup tracking** — check-in and track status for VV and Caca agents
- **Hong Kong weather** — current conditions and forecast via wttr.in
- **Crypto prices** — live BTC/ETH prices from CoinGecko
- **Top 5 Hacker News headlines** — latest tech news via HN RSS feed
- **Live HK clock** — always shows Hong Kong time
- **Daily schedule** — reads your personal schedule from `~/daily-schedule.txt`
- **Auto-refresh via cron** — keeps the dashboard data fresh throughout the day

---

## How to Use

### Run locally

```bash
# Generate the dashboard HTML
./generate.sh

# Or run the Python script directly
python3 generate_dashboard.py

# Serve locally (any static server works)
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

### Update schedule

Edit `~/daily-schedule.txt` on the machine running the cron job. The format is free-form text — each line is displayed as a schedule item.

Example `~/daily-schedule.txt`:
```
09:00 Standup
12:00 Lunch
14:00 Deep work
18:00 Wrap up
```

### Auto-refresh with cron

The dashboard refreshes automatically via a cron job that regenerates the HTML file:

```bash
# Edit crontab
crontab -e

# Add this line to regenerate every 30 minutes:
*/30 * * * * /path/to/generate.sh >> /path/to/dashboard.log 2>&1
```

---

## Tech Stack

- **Python** — data fetching and HTML generation
- **Shell script** — orchestration / cron entrypoint
- **Single HTML output** — static file, no server required
- [wttr.in](https://wttr.in/) — Hong Kong weather API
- [CoinGecko API](https://www.coingecko.com/en/api) — BTC/ETH prices
- [Hacker News RSS](https://hn.algolia.com/API) — top 5 headlines

---

## Project Structure

| File | Description |
|------|-------------|
| `generate_dashboard.py` | Fetches weather, crypto, HN headlines, and schedule → generates `index.html` |
| `generate.sh` | Shell wrapper — runs the Python script (used by cron) |
| `index.html` | The generated dashboard — served via GitHub Pages |

---

## Cron Setup

```bash
# Regenerate dashboard every 30 minutes
*/30 * * * * /home/yat121/.openclaw/workspace/projects/daily-dashboard/generate.sh >> /home/yat121/.openclaw/workspace/projects/daily-dashboard/dashboard.log 2>&1

# Or regenerate every hour on the hour
0 * * * * /home/yat121/.openclaw/workspace/projects/daily-dashboard/generate.sh >> /home/yat121/.openclaw/workspace/projects/daily-dashboard/dashboard.log 2>&1
```

The generated `index.html` is what gets published to GitHub Pages.
