"""Panels drawn from live data (DEV + GitHub). Each handles missing data with a visible state."""

import random

from theme import C, WIDTH, brackets, esc, panel_bg, svg, text_lines, wrap


def _fmt(n):
    return f"{n:,}" if isinstance(n, int) else "--"


def stats(live):
    w, h = WIDTH, 112
    cells = [
        ("PUBLIC REPOS", live.get("public_repos"), C["accent2"]),
        ("DEV POSTS", live.get("dev_posts"), C["docked"]),
        ("DEV REACTIONS", live.get("dev_reactions"), C["accent"]),
        ("CONTRIBUTIONS / YR", live.get("contrib_total"), C["live"]),
    ]
    cw = w / 4
    out = [panel_bg(w, h, 12)]
    for i, (label, val, col) in enumerate(cells):
        x = i * cw
        if i:
            out.append(f'<line x1="{x:.0f}" y1="22" x2="{x:.0f}" y2="{h - 22}" stroke="{C["line"]}"/>')
        out.append(f'<text x="{x + cw / 2:.0f}" y="58" font-size="30" font-weight="700" fill="{col}" text-anchor="middle">{esc(_fmt(val))}</text>')
        out.append(f'<text x="{x + cw / 2:.0f}" y="84" font-size="11" letter-spacing="2" fill="{C["dim"]}" text-anchor="middle">{esc(label)}</text>')
    when = live.get("fetched_at", "")
    label = "Ship's sensors: " + ", ".join(f"{l.lower()} {_fmt(v)}" for l, v, _ in cells) + (f" (as of {when})" if when else "")
    return svg(w, h, "".join(out), label)


STAR_R = {1: 1.7, 2: 2.5, 3: 3.3, 4: 4.2}
STAR_FILL = {1: "#6b4e86", 2: "#9B59B6", 3: "#c9a0e0", 4: "#ffffff"}


def _sparkle(cx, cy, r, fill, cls):
    s = r * 1.9
    d = (f"M{cx},{cy - s} Q{cx},{cy} {cx + s},{cy} Q{cx},{cy} {cx},{cy + s} "
         f"Q{cx},{cy} {cx - s},{cy} Q{cx},{cy} {cx},{cy - s} Z")
    return f'<path d="{d}" fill="{fill}"{cls}/>'


def starchart(live):
    weeks = live.get("contrib_weeks") or []
    w, cell, top, left = WIDTH, 14, 62, 52
    h = top + 7 * cell + 46
    out = [panel_bg(w, h, 12), brackets(10, 10, w - 20, h - 20, C["accent"])]
    out.append(f'<text x="28" y="40" font-size="13" font-weight="700" fill="{C["text"]}" letter-spacing="1.5">STAR CHART</text>')
    out.append(f'<text x="150" y="40" font-size="11.5" fill="{C["dim"]}">one star per day · brighter = more commits</text>')
    total = live.get("contrib_total")
    out.append(f'<text x="{w - 28}" y="40" font-size="12" fill="{C["live"]}" text-anchor="end">{esc(_fmt(total))} this year</text>')
    if not weeks:
        out.append(f'<text x="{w / 2}" y="{top + 50}" font-size="14" fill="{C["dim"]}" text-anchor="middle">Awaiting signal. Star chart will appear after the next sensor sweep.</text>')
    rnd = random.Random(1701)
    for wi, week in enumerate(weeks[-53:]):
        for di, level in enumerate(week):
            cx = left + wi * cell + rnd.uniform(-2, 2)
            cy = top + di * cell + rnd.uniform(-2, 2)
            if level == 0:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="0.8" fill="{C["line"]}"/>')
            elif level == 4:
                cls = f' class="tw tw{(wi + di) % 3}"'
                out.append(_sparkle(round(cx, 1), round(cy, 1), STAR_R[4] * 0.6, STAR_FILL[4], cls))
            else:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{STAR_R[level]}" fill="{STAR_FILL[level]}"/>')
    out.append(f'<text x="{left - 4}" y="{h - 18}" font-size="11" fill="{C["dim"]}">52 WEEKS AGO</text>')
    out.append(f'<text x="{w - 28}" y="{h - 18}" font-size="11" fill="{C["dim"]}" text-anchor="end">TODAY</text>')
    style = """
  .tw { animation: tw 3s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
  .tw1 { animation-delay: 1s; } .tw2 { animation-delay: 2s; }
  @keyframes tw { 0%,100% { opacity: 1; } 50% { opacity: .35; } }
"""
    label = f"Star chart of GitHub contributions over the last year: {_fmt(total)} contributions, one star per day."
    return svg(w, h, "".join(out), label, style)


def transmission(post, is_gem):
    w, pad = WIDTH, 30
    lines = wrap(post["title"], w - pad * 2, 17, max_lines=2)
    h = 84 + len(lines) * 25
    meta = f'{post["date"]}  ·  {post["reactions"]} reactions  ·  {post["comments"]} comments'
    out = [
        panel_bg(w, h, 10),
        f'<rect x="0" y="0" width="5" height="{h}" rx="2" fill="{C["accent"] if is_gem else C["docked"]}"/>',
        f'<text x="{pad}" y="34" font-size="11" letter-spacing="2" fill="{C["dim"]}">INCOMING TRANSMISSION</text>',
    ]
    if is_gem:
        out.append(f'<path d="M{w - pad - 140},28 l6,-7 h10 l6,7 l-11,12 Z" fill="{C["accent"]}"/>')
        out.append(f'<text x="{w - pad}" y="34" font-size="11" letter-spacing="1.5" fill="{C["accent"]}" text-anchor="end" font-weight="700">COMMUNITY GEM</text>')
    out.append(text_lines(lines, pad, 64, 17, C["text"], gap=1.45, weight=700))
    out.append(f'<text x="{pad}" y="{h - 20}" font-size="12" fill="{C["accent2"]}">{esc(meta)}</text>')
    label = f'DEV post: {post["title"]}. {meta}.' + (" Picked as a Community Gem." if is_gem else "")
    return svg(w, h, "".join(out), label)


def transmission_empty():
    w, h = WIDTH, 90
    body = panel_bg(w, h, 10) + f'<text x="{w / 2}" y="52" font-size="14" fill="{C["dim"]}" text-anchor="middle">Signal lost. Latest posts are on dev.to/earlgreyhot1701d.</text>'
    return svg(w, h, body, "Latest DEV posts unavailable right now.")
