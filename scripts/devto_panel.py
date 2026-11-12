"""SPIKE: draw the 3 latest DEV posts into one SVG panel.

One job: fetch -> escape -> draw. No styling decisions yet; this only proves
the pipeline (fetch from the DEV public API, write SVG, commit from Actions).

STUB (later): starship console styling, reactions/comments, gem markers.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

USERNAME = "earlgreyhot1701d"
API_URL = f"https://dev.to/api/articles?username={USERNAME}&per_page=3"
OUT_PATH = Path("assets/spike-devto.svg")
MAX_TITLE = 70


def fetch_posts():
    """Return a list of {title, date} dicts, or raise on any failure."""
    req = urllib.request.Request(API_URL, headers={"User-Agent": "earlgreyhot1701D-profile-spike"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    if not isinstance(data, list):
        raise ValueError("Unexpected API response shape")
    posts = []
    for item in data[:3]:
        title = str(item.get("title", "")).strip() or "(untitled)"
        if len(title) > MAX_TITLE:
            title = title[: MAX_TITLE - 1] + "…"
        date = str(item.get("readable_publish_date", "")).strip()
        posts.append({"title": title, "date": date})
    return posts


def render(lines, status):
    """Build the SVG. Every piece of text is XML-escaped before it goes in."""
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = []
    y = 70
    for line in lines:
        rows.append(f'<text x="24" y="{y}" class="row">{escape(line)}</text>')
        y += 30
    height = y + 20
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{height}" viewBox="0 0 800 {height}" role="img" aria-label="Latest DEV posts">
<style>
  .bg {{ fill: #0d1117; }}
  .head {{ fill: #9B59B6; font: 600 18px monospace; }}
  .row {{ fill: #e6edf3; font: 15px monospace; }}
  .meta {{ fill: #8b949e; font: 12px monospace; }}
</style>
<rect class="bg" width="800" height="{height}" rx="10"/>
<text x="24" y="38" class="head">&gt; LATEST TRANSMISSIONS FROM DEV</text>
{''.join(rows)}
<text x="24" y="{height - 12}" class="meta">status: {escape(status)} · drawn {stamp}</text>
</svg>
"""


def main():
    try:
        posts = fetch_posts()
        lines = [f"{p['date']}  {p['title']}" for p in posts] or ["No posts found."]
        status = "ok"
    except Exception as exc:  # meaningful error state, never a blank panel
        print(f"Fetch failed: {exc}", file=sys.stderr)
        lines = ["Signal lost. Latest posts unavailable right now."]
        status = "fetch failed"
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render(lines, status), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({status})")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
