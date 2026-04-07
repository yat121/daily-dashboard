#!/usr/bin/env python3
"""Premium Daily Dashboard — generate.py"""

import json, os, re
from datetime import datetime, timezone, timedelta

DASHBOARD_DIR = "/home/yat121/.openclaw/workspace/skills/daily-dashboard"
DATA_DIR = f"{DASHBOARD_DIR}/data"
OUTPUT = f"{DASHBOARD_DIR}/index.html"

# ─── Helpers ────────────────────────────────────────────────────────────────

def hk_now():
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))

def _weather_icon(desc):
    d = (desc or "").lower()
    if 'sun' in d or 'clear' in d: return '☀️'
    if 'cloud' in d: return '☁️'
    if 'rain' in d: return '🌧️'
    if 'storm' in d or 'thunder' in d: return '⛈️'
    if 'snow' in d: return '❄️'
    if 'fog' in d or 'mist' in d: return '🌫️'
    return '🌤'

# ─── Data Fetchers ──────────────────────────────────────────────────────────

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
            items = json.load(f)
        result = []
        for it in items:
            title = re.sub(r'\s+', ' ', it.get('title', '')).strip()
            url = it.get('url', '')
            source = it.get('source', 'Tech')
            if title:
                result.append({'title': title, 'url': url, 'source': source})
        return result
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
                    for y in (data.get('yesterday') or '').split(';'):
                        y = y.strip()
                        if y: lines.append(f"   • {y}")
                    t = data.get('today', '')
                    if t: lines.append(f"   → {t}")
                    b = data.get('blockers', '')
                    if b and 'none' not in b.lower(): lines.append(f"   🔴 {b}")
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

    # ── Weather icon ──
    w_icon = weather.get('icon', '🌤')
    w_temp = weather.get('temp', '–')
    w_desc = weather.get('desc', '–')
    w_hum = weather.get('humidity', '–')
    w_wind = weather.get('wind', '–')

    # ── 3-day forecast ──
    days_cn = {'Mon':'一','Tue':'二','Wed':'三','Thu':'四','Fri':'五','Sat':'六','Sun':'日'}
    fc_html = ""
    for f in weather.get('forecast', []):
        try:
            dn = datetime.strptime(f['date'], '%Y-%m-%d').strftime('%a')
            dn_cn = days_cn.get(dn, dn)
        except:
            dn_cn = f['date'][-2:] if f.get('date') else '–'
        fc_html += f"""
        <div class="fc-day">
            <div class="fc-icon">{f.get('icon','🌤')}</div>
            <div class="fc-date">{dn_cn}</div>
            <div class="fc-temps"><span class="fc-hi">{f['max']}°</span><span class="fc-lo">{f['min']}°</span></div>
        </div>"""

    # ── Crypto ──
    def fmt_currency(v):
        if isinstance(v, (int, float)): return f"{v:,.0f}"
        return str(v)
    def fmt_change(v):
        return f"{'+' if v >= 0 else ''}{v:.2f}%"
    def cc(v):
        return "#4ade80" if v >= 0 else "#f87171"
    def cbg(v):
        return f"rgba({255 if v>=0 else 248},{113 if v>=0 else 113},{113 if v>=0 else 113},0.12)"

    btc_chg = crypto.get('btc_change', 0)
    eth_chg = crypto.get('eth_change', 0)

    # ── News (clickable) ──
    news_html = ""
    source_colors = {'HK': '#f472b6', 'World': '#38bdf8', 'Tech': '#a78bfa'}
    for it in news:
        color = source_colors.get(it.get('source', 'Tech'), '#a78bfa')
        title = it.get('title', '')
        url = it.get('url', '')
        if url and title:
            news_html += f'''<div class="news-row">
                <a href="{url}" target="_blank" rel="noopener" class="news-link">
                    <span class="news-src" style="color:{color}">● {it.get('source','Tech')}</span>
                    <span class="news-title">{title}</span>
                    <span class="news-arrow">↗</span>
                </a>
            </div>'''
        elif title:
            news_html += f'''<div class="news-row">
                <span class="news-src" style="color:{color}">● {it.get('source','Tech')}</span>
                <span class="news-title muted">{title}</span>
            </div>'''
    if not news_html:
        news_html = '<div class="empty">No news available</div>'

    # ── Standup ──
    standup_html = f'<pre class="standup-pre">{standup}</pre>' if standup else '<div class="empty">No standup yet</div>'

    # ── Schedule ──
    sched_html = f'<pre class="standup-pre">{schedule}</pre>' if schedule else '<div class="empty">Create ~/daily-schedule.txt</div>'

    # ───────────────────────────────────────────────────────────────────────
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
    --surface: #13131c;
    --card: #181824;
    --border: rgba(255,255,255,0.06);
    --accent: #6366f1;
    --accent2: #818cf8;
    --green: #4ade80;
    --red: #f87171;
    --yellow: #fbbf24;
    --text: #f1f5f9;
    --muted: #64748b;
    --muted2: #94a3b8;
    --radius: 16px;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
    font-family: 'Inter','Noto Sans HK',-apple-system,sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    line-height: 1.5;
}}

/* ── TOP STRIP (Weather + At a Glance + Crypto) ── */
.top-strip {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0;
}}

.top-grid {{
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 0;
}}

/* Weather */
.weather-section {{
    padding: 20px 28px;
    border-right: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 16px;
}}
.weather-big-icon {{ font-size: 2.8rem; line-height: 1; }}
.weather-info {{}}
.weather-temp {{
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    color: var(--text);
}}
.weather-desc {{ font-size: 0.82rem; color: var(--muted2); margin-top: 2px; }}
.weather-meta {{ font-size: 0.75rem; color: var(--muted); margin-top: 4px; display: flex; gap: 12px; }}
.weather-fc {{
    display: flex;
    gap: 8px;
    margin-left: 20px;
}}
.fc-day {{
    background: var(--card);
    border-radius: 10px;
    padding: 10px 14px;
    text-align: center;
    min-width: 56px;
}}
.fc-icon {{ font-size: 1.3rem; }}
.fc-date {{ font-size: 0.68rem; color: var(--muted); margin: 3px 0 4px; }}
.fc-temps {{ display: flex; gap: 4px; justify-content: center; font-size: 0.8rem; font-weight: 600; }}
.fc-hi {{ color: var(--yellow); }}
.fc-lo {{ color: #93c5fd; }}

/* At a Glance */
.glance-section {{
    padding: 16px 24px;
    display: flex;
    align-items: center;
    gap: 0;
    border-right: 1px solid var(--border);
}}
.glance-grid {{
    display: flex;
    gap: 0;
}}
.glance-item {{
    padding: 0 20px;
    text-align: center;
    border-right: 1px solid var(--border);
}}
.glance-item:last-child {{ border-right: none; }}
.glance-val {{
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent2);
    line-height: 1;
}}
.glance-lbl {{
    font-size: 0.65rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
    white-space: nowrap;
}}

/* Crypto */
.crypto-section {{
    padding: 16px 28px;
    display: flex;
    align-items: center;
    gap: 24px;
    justify-content: flex-end;
}}
.crypto-coin {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.crypto-icon {{ font-size: 1.4rem; }}
.crypto-name {{ font-size: 0.75rem; color: var(--muted); }}
.crypto-price {{ font-size: 1rem; font-weight: 700; }}
.crypto-chg {{
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 100px;
    margin-top: 2px;
    display: inline-block;
}}

/* ── Hero ── */
.hero {{
    background: linear-gradient(180deg, #0f0f1a 0%, var(--bg) 100%);
    padding: 36px 24px 24px;
    text-align: center;
    border-bottom: 1px solid var(--border);
}}
.hero-date {{
    font-size: 0.72rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 6px;
}}
.hero-title {{
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg,#fff 0%,#c7d2fe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}}
.hero-tagline {{
    font-size: 0.92rem;
    color: var(--muted2);
    font-style: italic;
    max-width: 480px;
    margin: 0 auto;
}}

/* ── Main Layout ── */
.main {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 28px 24px 60px;
}}

.content-grid {{
    display: grid;
    grid-template-columns: 3fr 2fr;
    gap: 20px;
    align-items: start;
}}

/* ── Cards ── */
.card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
}}
.card-header {{
    padding: 14px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.card-title {{
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 8px;
}}
.card-title::before {{
    content: '';
    width: 3px;
    height: 12px;
    background: var(--accent);
    border-radius: 2px;
}}
.card-body {{ padding: 16px 20px; }}

/* ── News ── */
.news-card {{ grid-column: 1; }}
.news-card .card-body {{ padding: 0; }}
.news-row {{
    padding: 13px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
}}
.news-row:last-child {{ border-bottom: none; }}
.news-link {{
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    color: inherit;
    width: 100%;
    transition: background 0.15s;
    padding: 0;
}}
.news-link:hover {{ background: rgba(99,102,241,0.06); }}
.news-src {{
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    min-width: 46px;
    flex-shrink: 0;
}}
.news-title {{
    font-size: 0.88rem;
    color: var(--text);
    flex: 1;
    line-height: 1.4;
}}
.news-link .news-title {{}}
.news-arrow {{
    color: var(--accent);
    font-size: 0.85rem;
    opacity: 0;
    transition: opacity 0.15s;
    flex-shrink: 0;
}}
.news-link:hover .news-arrow {{ opacity: 1; }}
.muted {{ color: var(--muted2); }}

/* ── Standup ── */
.standup-card {{ grid-column: 1; }}
.standup-pre {{
    font-family: 'Inter', monospace;
    font-size: 0.83rem;
    line-height: 1.9;
    color: var(--text);
    white-space: pre-wrap;
}}

/* ── Schedule ── */
.schedule-card {{ grid-column: 2; grid-row: 1 / 3; }}
.sched-pre {{
    font-family: 'Inter', monospace;
    font-size: 0.83rem;
    line-height: 1.9;
    color: var(--text);
    white-space: pre-wrap;
}}

/* ── Empty ── */
.empty {{
    color: var(--muted);
    font-size: 0.85rem;
    font-style: italic;
    padding: 8px 0;
}}

/* ── Footer ── */
.footer {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px 40px;
    text-align: center;
    border-top: 1px solid var(--border);
    padding-top: 28px;
    color: var(--muted);
    font-size: 0.75rem;
}}
.footer a {{ color: var(--accent2); text-decoration: none; }}

/* ── Responsive ── */
@media (max-width: 960px) {{
    .content-grid {{ grid-template-columns: 1fr; }}
    .schedule-card {{ grid-column: 1; grid-row: auto; }}
    .standup-card {{ grid-column: 1; }}
    .news-card {{ grid-column: 1; }}
}}
@media (max-width: 768px) {{
    .top-grid {{ grid-template-columns: 1fr; }}
    .weather-section {{ border-right: none; border-bottom: 1px solid var(--border); }}
    .glance-section {{ border-right: none; border-bottom: 1px solid var(--border); justify-content: center; }}
    .crypto-section {{ justify-content: center; flex-wrap: wrap; gap: 16px; }}
    .weather-fc {{ margin-left: 0; }}
}}
@media (max-width: 480px) {{
    .hero {{ padding: 24px 16px 18px; }}
    .hero-title {{ font-size: 1.4rem; }}
    .main {{ padding: 16px 12px 40px; }}
    .card-body {{ padding: 12px 14px; }}
    .news-row {{ padding: 11px 14px; }}
}}
</style>
</head>
<body>

<!-- ── TOP: Weather + At a Glance + Crypto ── -->
<div class="top-strip">
<div class="top-grid">

    <!-- Weather -->
    <div class="weather-section">
        <div class="weather-big-icon">{w_icon}</div>
        <div class="weather-info">
            <div class="weather-temp">{w_temp}°C</div>
            <div class="weather-desc">{w_desc}</div>
            <div class="weather-meta">
                <span>💧 {w_hum}%</span>
                <span>💨 {w_wind} km/h</span>
            </div>
        </div>
        <div class="weather-fc">{fc_html}</div>
    </div>

    <!-- At a Glance -->
    <div class="glance-section">
        <div class="glance-grid">
            <div class="glance-item">
                <div class="glance-val">{time_str}</div>
                <div class="glance-lbl">HKT</div>
            </div>
            <div class="glance-item">
                <div class="glance-val">{now.strftime('%A')[:3]}</div>
                <div class="glance-lbl">Day</div>
            </div>
            <div class="glance-item">
                <div class="glance-val">{now.strftime('%d')}</div>
                <div class="glance-lbl">{now.strftime('%b')}</div>
            </div>
            <div class="glance-item">
                <div class="glance-val">W{now.isocalendar()[1]}</div>
                <div class="glance-lbl">Week</div>
            </div>
        </div>
    </div>

    <!-- Crypto -->
    <div class="crypto-section">
        <div class="crypto-coin">
            <span class="crypto-icon">₿</span>
            <div>
                <div class="crypto-name">Bitcoin</div>
                <div class="crypto-price">${fmt_currency(crypto.get('btc_usd',0))}</div>
                <div class="crypto-chg" style="color:{cc(btc_chg)};background:{cbg(btc_chg)}">{fmt_change(btc_chg)}</div>
            </div>
        </div>
        <div class="crypto-coin">
            <span class="crypto-icon">Ξ</span>
            <div>
                <div class="crypto-name">Ethereum</div>
                <div class="crypto-price">${fmt_currency(crypto.get('eth_usd',0))}</div>
                <div class="crypto-chg" style="color:{cc(eth_chg)};background:{cbg(eth_chg)}">{fmt_change(eth_chg)}</div>
            </div>
        </div>
    </div>

</div>
</div>

<!-- ── Hero ── -->
<div class="hero">
    <div class="hero-date">{date_str} · Hong Kong</div>
    <h1 class="hero-title">Daily Dashboard</h1>
    <p class="hero-tagline">"{tagline}"</p>
</div>

<!-- ── Main Content ── -->
<div class="main">
<div class="content-grid">

    <!-- News -->
    <div class="card news-card">
        <div class="card-header">
            <div class="card-title">📰 科技新聞精選 Tech News</div>
        </div>
        <div class="card-body">{news_html}</div>
    </div>

    <!-- Standup -->
    <div class="card standup-card">
        <div class="card-header">
            <div class="card-title">✅ Daily Standup</div>
        </div>
        <div class="card-body">{standup_html}</div>
    </div>

    <!-- Schedule -->
    <div class="card schedule-card">
        <div class="card-header">
            <div class="card-title">📅 Schedule</div>
        </div>
        <div class="card-body">{sched_html}</div>
    </div>

</div>
</div>

<div class="footer">
    Run <code>bash skills/daily-dashboard/generate.sh</code> to refresh · Built by <a href="https://github.com/yat121">Desmond Ho</a>
</div>

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
