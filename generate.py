#!/usr/bin/env python3
"""Generate the daily dashboard — premium UI."""

import json, os, re
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

DASHBOARD_DIR = "/home/yat121/.openclaw/workspace/skills/daily-dashboard"
DATA_DIR = f"{DASHBOARD_DIR}/data"
OUTPUT = f"{DASHBOARD_DIR}/index.html"

# ─── Helpers ────────────────────────────────────────────────────────────────

def hk_now():
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))

def parse_weather():
    try:
        with open(f"{DATA_DIR}/weather.json") as f:
            d = json.load(f)
        c = d.get('current_condition', [{}])[0]
        fc = []
        for day in d.get('weather', [])[:3]:
            fc.append({
                'date': day.get('date', ''),
                'max': day.get('maxtempC', 'N/A'),
                'min': day.get('mintempC', 'N/A'),
                'desc': (day.get('hourly', [{}])[0].get('weatherDesc', [{}]) or [{}])[0].get('value', ''),
                'icon': _weather_icon((day.get('hourly', [{}])[0].get('weatherDesc', [{}]) or [{}])[0].get('value', ''))
            })
        return {
            'temp': c.get('temp_C', 'N/A'),
            'desc': c.get('weatherDesc', [{}])[0].get('value', 'N/A'),
            'humidity': c.get('humidity', 'N/A'),
            'wind': c.get('windspeedKmph', 'N/A'),
            'forecast': fc,
            'icon': _weather_icon(c.get('weatherDesc', [{}])[0].get('value', ''))
        }
    except:
        return {'temp': 'N/A', 'desc': 'N/A', 'humidity': 'N/A', 'wind': 'N/A', 'forecast': [], 'icon': '🌤'}

def _weather_icon(desc):
    d = desc.lower()
    if 'sun' in d or 'clear' in d: return '☀️'
    if 'cloud' in d: return '☁️'
    if 'rain' in d: return '🌧️'
    if 'storm' in d or 'thunder' in d: return '⛈️'
    if 'snow' in d: return '❄️'
    if 'fog' in d or 'mist' in d: return '🌫️'
    return '🌤'

def parse_crypto():
    try:
        with open(f"{DATA_DIR}/crypto.json") as f:
            d = json.load(f)
        btc = d.get('bitcoin', {})
        eth = d.get('ethereum', {})
        return {
            'btc_usd': btc.get('usd', 0),
            'btc_change': btc.get('usd_24h_change', 0),
            'eth_usd': eth.get('usd', 0),
            'eth_change': eth.get('usd_24h_change', 0),
        }
    except:
        return {'btc_usd': 0, 'btc_change': 0, 'eth_usd': 0, 'eth_change': 0}

def parse_news():
    try:
        with open(f"{DATA_DIR}/news.json") as f:
            d = json.load(f)
        return [re.sub(r'\s+', ' ', h.get('title', '')).strip()
                for h in d.get('hits', [])[:8] if h.get('title')]
    except:
        return []

def read_schedule():
    p = os.path.expanduser("~/daily-schedule.txt")
    return open(p).read().strip() if os.path.exists(p) else None

def read_standup():
    agents_dir = "/home/yat121/.openclaw/workspace/skills/daily-standup/agents"
    today = hk_now().strftime("%Y-%m-%d")
    names = {'vv': ('🤖', 'VV'), 'caca': ('🍫', 'Caca'), 'rasp': ('🔍', 'Rasp'),
             'mimi': ('🎯', 'Mimi'), 'potato': ('🥔', 'Potato')}
    lines = []
    for fn, (emoji, name) in names.items():
        fp = os.path.join(agents_dir, f"{fn}-standup.json")
        if os.path.exists(fp):
            try:
                data = json.load(open(fp)).get(today, {})
                if data.get('yesterday') or data.get('today') or data.get('blockers'):
                    lines.append(f"{emoji} {name}")
                    y = data.get('yesterday', '')
                    t = data.get('today', '')
                    b = data.get('blockers', '')
                    if y: lines.append(f"   Yesterday: {y}")
                    if t: lines.append(f"   Today: {t}")
                    if b: lines.append(f"   🔴 {b}")
            except: pass
    return '\n'.join(lines) if lines else None

# ─── Taglines ───────────────────────────────────────────────────────────────

TAGLINES = [
    "Build in public. Ship fast. Learn louder.",
    "The best time to plant a tree was yesterday. The second best is today.",
    "Focus on what matters. Ignore the rest.",
    "Stay curious, keep coding, embrace failure.",
    "Progress over perfection, every single day.",
    "Consistency beats intensity.",
    "Your future self will thank you for today's effort."
]

def get_tagline():
    return TAGLINES[hk_now().weekday()]

# ─── Build HTML ─────────────────────────────────────────────────────────────

def build_html(weather, crypto, news, schedule, standup, tagline):
    now = hk_now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    # Crypto helpers
    def fmt(v):
        if isinstance(v, float): return f"{v:,.2f}"
        return str(v)
    def fmtd(v):
        sign = "+" if v >= 0 else ""
        return f"{sign}{v:.2f}%"
    def crypto_color(v):
        return "#4ade80" if v >= 0 else "#f87171"

    # Forecast HTML
    fc_rows = ""
    days_map = {'Mon':'一','Tue':'二','Wed':'三','Thu':'四','Fri':'五','Sat':'六','Sun':'日'}
    for f in weather.get('forecast', []):
        try:
            dn = datetime.strptime(f['date'], '%Y-%m-%d').strftime('%a')
            dn_cn = days_map.get(dn, dn)
        except:
            dn_cn = f['date'][-2:]
        fc_rows += f"""
        <div class="fc-day">
            <div class="fc-emoji">{f.get('icon','🌤')}</div>
            <div class="fc-date">{dn_cn}</div>
            <div class="fc-temps"><span class="fc-high">{f['max']}°</span><span class="fc-low">{f['min']}°</span></div>
        </div>"""

    # News HTML
    news_html = ""
    for i, h in enumerate(news, 1):
        news_html += f'<div class="news-item"><span class="news-num">{i}</span><span class="news-title">{h}</span></div>'
    if not news_html:
        news_html = '<div class="empty-state">No news available</div>'

    # Standup HTML
    standup_html = f'<pre class="standup-pre">{standup}</pre>' if standup else '<div class="empty-state">No standup yet</div>'

    # Schedule HTML
    sched_html = f'<pre class="sched-pre">{schedule}</pre>' if schedule else '<div class="empty-state">Create ~/daily-schedule.txt to show your schedule</div>'

    # ── Full HTML ──────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Dashboard — {date_str}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+HK:wght@400;500;700&display=swap');

  :root {{
    --bg: #0a0a0f;
    --surface: #12121a;
    --card: #1a1a24;
    --card-hover: #1f1f2b;
    --border: rgba(255,255,255,0.06);
    --accent: #6366f1;
    --accent2: #818cf8;
    --accent-glow: rgba(99,102,241,0.15);
    --green: #4ade80;
    --red: #f87171;
    --yellow: #fbbf24;
    --text: #f1f5f9;
    --muted: #64748b;
    --muted2: #94a3b8;
    --radius: 16px;
    --radius-sm: 10px;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Inter', 'Noto Sans HK', -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    line-height: 1.5;
  }}

  /* ── Header ── */
  .hero {{
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%);
    border-bottom: 1px solid var(--border);
    padding: 48px 24px 40px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }}
  .hero::before {{
    content: '';
    position: absolute;
    top: -50%;
    left: 50%;
    transform: translateX(-50%);
    width: 600px;
    height: 300px;
    background: radial-gradient(ellipse, var(--accent-glow) 0%, transparent 70%);
    pointer-events: none;
  }}
  .hero-date {{
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 8px;
  }}
  .hero-title {{
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #fff 0%, #c7d2fe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
  }}
  .hero-tagline {{
    font-size: 1rem;
    color: var(--muted2);
    font-style: italic;
    max-width: 500px;
    margin: 0 auto 20px;
  }}
  .hero-time {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: 6px 16px;
    font-size: 0.85rem;
    color: var(--muted);
  }}
  .hero-time span {{
    color: var(--accent2);
    font-weight: 600;
    font-size: 1.1rem;
  }}

  /* ── Container ── */
  .container {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 32px 20px 60px;
  }}

  /* ── Grid ── */
  .main-grid {{
    display: grid;
    grid-template-columns: 1fr 380px;
    grid-template-rows: auto;
    gap: 20px;
  }}
  .content-col {{ display: flex; flex-direction: column; gap: 20px; }}
  .sidebar {{ display: flex; flex-direction: column; gap: 20px; }}

  /* ── Cards ── */
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    transition: border-color 0.2s;
  }}
  .card:hover {{ border-color: rgba(255,255,255,0.1); }}
  .card-title {{
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--muted);
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .card-title::before {{
    content: '';
    width: 3px;
    height: 14px;
    background: var(--accent);
    border-radius: 2px;
  }}

  /* ── News ── */
  .news-card {{ grid-column: 1; }}
  .news-item {{
    display: flex;
    gap: 14px;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
    align-items: flex-start;
  }}
  .news-item:last-child {{ border-bottom: none; }}
  .news-num {{
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--accent);
    min-width: 20px;
    padding-top: 2px;
  }}
  .news-title {{
    font-size: 0.92rem;
    color: var(--text);
    line-height: 1.5;
    cursor: default;
  }}

  /* ── Standup ── */
  .standup-card {{ grid-column: 1; }}
  .standup-pre {{
    font-family: 'Inter', monospace;
    font-size: 0.85rem;
    line-height: 1.8;
    color: var(--text);
    white-space: pre-wrap;
  }}

  /* ── Schedule ── */
  .sched-card {{ grid-column: 1; }}
  .sched-pre {{
    font-family: 'Inter', monospace;
    font-size: 0.85rem;
    line-height: 1.8;
    color: var(--text);
    white-space: pre-wrap;
  }}

  /* ── Sidebar: Weather ── */
  .weather-card {{ }}
  .weather-main {{
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
  }}
  .weather-icon {{ font-size: 3.5rem; line-height: 1; }}
  .weather-temp {{
    font-size: 3rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
  }}
  .weather-desc {{
    font-size: 0.9rem;
    color: var(--muted2);
    margin-top: 4px;
  }}
  .weather-meta {{
    display: flex;
    gap: 16px;
    font-size: 0.82rem;
    color: var(--muted);
    margin-bottom: 20px;
  }}
  .weather-meta span {{ display: flex; align-items: center; gap: 4px; }}
  .fc-row {{
    display: flex;
    gap: 8px;
    justify-content: space-between;
  }}
  .fc-day {{
    flex: 1;
    background: var(--surface);
    border-radius: var(--radius-sm);
    padding: 12px 8px;
    text-align: center;
  }}
  .fc-emoji {{ font-size: 1.4rem; margin-bottom: 4px; }}
  .fc-date {{ font-size: 0.72rem; color: var(--muted); margin-bottom: 6px; }}
  .fc-temps {{ display: flex; justify-content: center; gap: 6px; font-size: 0.82rem; font-weight: 600; }}
  .fc-high {{ color: var(--yellow); }}
  .fc-low {{ color: #93c5fd; }}

  /* ── Sidebar: Crypto ── */
  .crypto-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
  }}
  .crypto-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
  .crypto-left {{ display: flex; align-items: center; gap: 10px; }}
  .crypto-coin {{ font-size: 1.6rem; }}
  .crypto-name {{ font-size: 0.85rem; font-weight: 600; }}
  .crypto-price {{ font-size: 1rem; font-weight: 700; margin-top: 2px; }}
  .crypto-right {{ text-align: right; }}
  .crypto-change {{ font-size: 0.8rem; font-weight: 600; padding: 3px 8px; border-radius: 100px; }}

  /* ── Quick Stats ── */
  .stats-row {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }}
  .stat-box {{
    background: var(--surface);
    border-radius: var(--radius-sm);
    padding: 14px;
    text-align: center;
  }}
  .stat-val {{
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--accent2);
    line-height: 1;
    margin-bottom: 4px;
  }}
  .stat-lbl {{
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
  }}

  /* ── Empty state ── */
  .empty-state {{
    color: var(--muted);
    font-size: 0.88rem;
    font-style: italic;
    padding: 8px 0;
  }}

  /* ── Footer ── */
  .footer {{
    text-align: center;
    margin-top: 48px;
    padding-top: 24px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.78rem;
  }}
  .footer a {{ color: var(--accent2); text-decoration: none; }}

  /* ── Responsive ── */
  @media (max-width: 900px) {{
    .main-grid {{ grid-template-columns: 1fr; }}
    .sidebar {{ flex-direction: row; flex-wrap: wrap; }}
    .sidebar .card {{ flex: 1 1 280px; }}
  }}
  @media (max-width: 600px) {{
    .hero {{ padding: 32px 16px 28px; }}
    .hero-title {{ font-size: 1.5rem; }}
    .container {{ padding: 20px 16px 40px; }}
    .card {{ padding: 18px; }}
    .stats-row {{ grid-template-columns: 1fr 1fr; }}
  }}
</style>
</head>
<body>

<!-- ── Hero ── -->
<div class="hero">
  <div class="hero-date">{date_str} · Hong Kong</div>
  <h1 class="hero-title">Daily Dashboard</h1>
  <p class="hero-tagline">"{tagline}"</p>
  <div class="hero-time">🕐 <span>{time_str}</span> HKT</div>
</div>

<!-- ── Main Content ── -->
<div class="container">
<div class="main-grid">

  <!-- News ── -->
  <div class="card news-card">
    <div class="card-title">📰 科技新聞精選 Tech News</div>
    {news_html}
  </div>

  <!-- Standup ── -->
  <div class="card standup-card">
    <div class="card-title">✅ Daily Standup</div>
    {standup_html}
  </div>

  <!-- Schedule ── -->
  <div class="card sched-card">
    <div class="card-title">📅 Today's Schedule</div>
    {sched_html}
  </div>

  <!-- Sidebar ── -->
  <div class="sidebar">

    <!-- Weather ── -->
    <div class="card weather-card">
      <div class="card-title">🌤 Weather</div>
      <div class="weather-main">
        <div class="weather-icon">{weather.get('icon','☀️')}</div>
        <div>
          <div class="weather-temp">{weather.get('temp','N/A')}°</div>
          <div class="weather-desc">{weather.get('desc','N/A')}</div>
        </div>
      </div>
      <div class="weather-meta">
        <span>💧 {weather.get('humidity','N/A')}%</span>
        <span>💨 {weather.get('wind','N/A')} km/h</span>
      </div>
      <div class="fc-row">{fc_rows}</div>
    </div>

    <!-- Crypto ── -->
    <div class="card">
      <div class="card-title">💹 Crypto</div>
      <div class="crypto-item">
        <div class="crypto-left">
          <span class="crypto-coin">₿</span>
          <div>
            <div class="crypto-name">Bitcoin</div>
            <div class="crypto-price">${fmt(crypto.get('btc_usd',0))}</div>
          </div>
        </div>
        <div class="crypto-right">
          <div class="crypto-change" style="color:{crypto_color(crypto.get('btc_change',0))};background:rgba({255 if crypto.get('btc_change',0)>=0 else 248},{(113 if crypto.get('btc_change',0)>=0 else 113)},{(128 if crypto.get('btc_change',0)>=0 else 113)},0.12)">{fmtd(crypto.get('btc_change',0))}</div>
        </div>
      </div>
      <div class="crypto-item">
        <div class="crypto-left">
          <span class="crypto-coin">Ξ</span>
          <div>
            <div class="crypto-name">Ethereum</div>
            <div class="crypto-price">${fmt(crypto.get('eth_usd',0))}</div>
          </div>
        </div>
        <div class="crypto-right">
          <div class="crypto-change" style="color:{crypto_color(crypto.get('eth_change',0))};background:rgba({255 if crypto.get('eth_change',0)>=0 else 248},{(113 if crypto.get('eth_change',0)>=0 else 113)},{(128 if crypto.get('eth_change',0)>=0 else 113)},0.12)">{fmtd(crypto.get('eth_change',0))}</div>
        </div>
      </div>
    </div>

    <!-- Quick Stats ── -->
    <div class="card">
      <div class="card-title">⚡ At a Glance</div>
      <div class="stats-row">
        <div class="stat-box">
          <div class="stat-val">{now.strftime('%H:%M')}</div>
          <div class="stat-lbl">Time (HKT)</div>
        </div>
        <div class="stat-box">
          <div class="stat-val">{now.strftime('%A')[:3]}</div>
          <div class="stat-lbl">Day</div>
        </div>
        <div class="stat-box">
          <div class="stat-val">{now.strftime('%d')}</div>
          <div class="stat-lbl">Date</div>
        </div>
        <div class="stat-box">
          <div class="stat-val">W{now.isocalendar()[1]}</div>
          <div class="stat-lbl">Week</div>
        </div>
      </div>
    </div>

  </div><!-- /sidebar -->
</div><!-- /main-grid -->

<div class="footer">
  Run <code>bash skills/daily-dashboard/generate.sh</code> to refresh · Built by <a href="https://github.com/yat121">Desmond Ho</a>
</div>
</div><!-- /container -->
</body>
</html>"""
    return html


if __name__ == "__main__":
    weather = parse_weather()
    crypto = parse_crypto()
    news = parse_news()
    schedule = read_schedule()
    standup = read_standup()
    tagline = get_tagline()

    html = build_html(weather, crypto, news, schedule, standup, tagline)
    with open(OUTPUT, "w") as f:
        f.write(html)
    print(f"✅ Dashboard written to: {OUTPUT}")
