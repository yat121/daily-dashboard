#!/bin/bash
# Daily Dashboard Generator
# Run: bash skills/daily-dashboard/generate.sh

DASHBOARD_DIR="/home/yat121/.openclaw/workspace/skills/daily-dashboard"
DATA_DIR="$DASHBOARD_DIR/data"
OUTPUT="$DASHBOARD_DIR/index.html"

mkdir -p "$DATA_DIR"

echo "=== Fetching Weather ==="
curl -s "wttr.in/Hong+Kong?format=j1" -o "$DATA_DIR/weather.json"
echo "Done"

echo "=== Fetching Crypto Prices ==="
curl -s "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true" -o "$DATA_DIR/crypto.json" 2>/dev/null || echo '{}' > "$DATA_DIR/crypto.json"
echo "Done"

echo "=== Fetching News (HK + World + Tech) ==="
# Mix of HK, World, and Tech news from HackerNews
python3 << 'PYEOF'
import urllib.request, json, time

DATA_DIR = "/home/yat121/.openclaw/workspace/skills/daily-dashboard/data"

def fetch_hn(query, tags="story", hits=4):
    url = f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(query)}&tags={tags}&hitsPerPage={hits}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read()).get("hits", [])
    except:
        return []

import urllib.parse

all_news = []
seen = set()

# HK news
for h in fetch_hn("Hong Kong news", hits=4):
    oid = h.get("objectID","")
    if oid not in seen:
        seen.add(oid)
        url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('story_id','')}"
        all_news.append({"title": h.get("title",""), "url": url, "source": "HK"})

# World news
for h in fetch_hn("world news today", hits=4):
    oid = h.get("objectID","")
    if oid not in seen:
        seen.add(oid)
        url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('story_id','')}"
        all_news.append({"title": h.get("title",""), "url": url, "source": "World"})

# Tech/Crypto
for h in fetch_hn("crypto bitcoin AI", tags="story", hits=4):
    oid = h.get("objectID","")
    if oid not in seen:
        seen.add(oid)
        url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('story_id','')}"
        all_news.append({"title": h.get("title",""), "url": url, "source": "Tech"})

with open(f"{DATA_DIR}/news.json", "w") as f:
    json.dump(all_news, f, indent=2)

print(f"Fetched {len(all_news)} news items")
PYEOF
echo "Done"

echo "=== Generating HTML ==="
/usr/bin/python3 "$DASHBOARD_DIR/generate.py"
echo "Done: $OUTPUT"
