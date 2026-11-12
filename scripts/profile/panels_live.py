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


def _short_date(iso):
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    try:
        y, m, d = iso.split("-")
        return f"{months[int(m) - 1]} {int(d)}"
    except (ValueError, IndexError):
        return ""


STAR_R = {1: 1.7, 2: 2.5, 3: 3.3, 4: 4.2}
STAR_FILL = {1: "#6b4e86", 2: "#9B59B6", 3: "#c9a0e0", 4: "#ffffff"}


def _sparkle(cx, cy, r, fill, cls):
    s = r * 1.9
    d = (f"M{cx},{cy - s} Q{cx},{cy} {cx + s},{cy} Q{cx},{cy} {cx},{cy + s} "
         f"Q{cx},{cy} {cx - s},{cy} Q{cx},{cy} {cx},{cy - s} Z")
    return f'<path d="{d}" fill="{fill}"{cls}/>'


def starchart(live, worlds=None):
    weeks = live.get("contrib_weeks") or []
    w, cell, top, left = WIDTH, 14, 98, 52
    h = top + 6 * cell + 74  # room for planet name tags above and below the grid
    out = [panel_bg(w, h, 12), brackets(10, 10, w - 20, h - 20, C["accent"])]
    out.append(f'<text x="28" y="40" font-size="13" font-weight="700" fill="{C["text"]}" letter-spacing="1.5">STAR CHART</text>')
    legend = "one star per day · brighter = more commits ·"
    out.append(f'<text x="150" y="40" font-size="11.5" fill="{C["dim"]}">{esc(legend)}</text>')
    lx = 150 + len(legend) * 11.5 * 0.6 + 16
    out.append(_planet(lx, 36, "shipped", scale=0.8))
    out.append(f'<text x="{lx + 13:.0f}" y="40" font-size="11.5" fill="{C["accent2"]}">= something I shipped</text>')
    total = live.get("contrib_total")
    out.append(f'<text x="{w - 28}" y="40" font-size="12" fill="{C["live"]}" text-anchor="end">{esc(_fmt(total))} this year</text>')
    if not weeks:
        out.append(f'<text x="{w / 2}" y="{top + 50}" font-size="14" fill="{C["dim"]}" text-anchor="middle">Awaiting signal. Star chart will appear after the next sensor sweep.</text>')
    shown = weeks[-53:]
    rnd = random.Random(1701)
    stars = {}  # (week, day) -> (x, y, level)
    for wi, week in enumerate(shown):
        for di, level in enumerate(week):
            cx = left + wi * cell + rnd.uniform(-2, 2)
            cy = top + di * cell + rnd.uniform(-2, 2)
            stars[(wi, di)] = (cx, cy, level)
            if level == 0:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="0.8" fill="{C["line"]}"/>')
            elif level == 4:
                cls = f' class="tw tw{(wi + di) % 3}"'
                out.append(_sparkle(round(cx, 1), round(cy, 1), STAR_R[4] * 0.6, STAR_FILL[4], cls))
            else:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{STAR_R[level]}" fill="{STAR_FILL[level]}"/>')
    placed = _worlds(worlds or [], shown, live.get("contrib_week_starts") or [], cell, top, left, w)
    out.extend(placed["svg"])
    if shown:
        out.append(_patrol(shown, stars, cell, top, left))
    peak = live.get("contrib_peak") or {}
    streak = live.get("contrib_longest_streak")
    facts = []
    if peak.get("count"):
        facts.append(f'BRIGHTEST STAR {_short_date(peak.get("date", ""))} · {peak["count"]} commits')
    if streak:
        facts.append(f"LONGEST STREAK {streak} days")
    if facts:
        out.append(f'<text x="{w / 2}" y="{h - 18}" font-size="11.5" fill="{C["accent2"]}" text-anchor="middle" letter-spacing="1" xml:space="preserve">{esc("   |   ".join(facts))}</text>')
    out.append(f'<text x="{left - 4}" y="{h - 18}" font-size="11" fill="{C["dim"]}">52 WEEKS AGO</text>')
    out.append(f'<text x="{w - 28}" y="{h - 18}" font-size="11" fill="{C["dim"]}" text-anchor="end">TODAY</text>')
    style = """
  .tw { animation: tw 3s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
  .tw1 { animation-delay: 1s; } .tw2 { animation-delay: 2s; }
  @keyframes tw { 0%,100% { opacity: 1; } 50% { opacity: .35; } }
  .engine { animation: flicker .25s steps(2) infinite; }
  @keyframes flicker { 50% { opacity: .55; } }
  @media (prefers-reduced-motion: reduce) { .ship, .ping { display: none; } }
"""
    label = (f"Star chart of GitHub contributions over the last year: {_fmt(total)} contributions, one star per day. "
             + (f"Brightest star: {_short_date(peak.get('date', ''))} with {peak.get('count')} commits. " if peak.get("count") else "")
             + (f"Longest streak: {streak} days. " if streak else "")
             + (f"Planets mark things I shipped: {', '.join(placed['names'])}. " if placed["names"] else "")
             + 
             "A small scout ship patrols the chart, and each active day flares as it passes.")
    return svg(w, h, "".join(out), label, style)


def _planet(x, y, status, scale=1.0):
    """Original ringed planet. Shipped = solid; building = dashed outline (under construction)."""
    r, rx, ry = 4.6 * scale, 9 * scale, 2.8 * scale
    if status == "building":
        body = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{C["bg"]}" stroke="{C["drydock"]}" stroke-width="1.3" stroke-dasharray="2 1.6"/>'
        ring_col, dash = C["drydock"], ' stroke-dasharray="2 1.6"'
    else:
        body = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{C["accent2"]}"/>'
        ring_col, dash = C["accent"], ""
    ring = (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="{ring_col}" '
            f'stroke-width="1.2"{dash} transform="rotate(-18 {x:.1f} {y:.1f})"/>')
    return body + ring


def _worlds(worlds, shown, week_starts, cell, top, left, w):
    """Place a planet on each shipped project's day, with a name tag in a lane above or below the grid."""
    from datetime import date, timedelta
    starts = week_starts[-len(shown):] if shown else []
    if not starts or len(starts) != len(shown):
        return {"svg": [], "names": []}
    try:
        starts = [date.fromisoformat(d) for d in starts]
    except ValueError:
        return {"svg": [], "names": []}
    spots = []
    for world in worlds:
        try:
            d = date.fromisoformat(world["date"])
        except (KeyError, ValueError):
            continue
        for wi, (st, week) in enumerate(zip(starts, shown)):
            if st <= d < st + timedelta(days=len(week)):
                spots.append((left + wi * cell, top + (d - st).days * cell, world))
                break
    spots.sort(key=lambda s: s[0])
    grid_top, grid_bot = top - 8, top + 6 * cell + 8
    lanes = [("up", top - 18), ("down", grid_bot + 14), ("up", top - 32), ("down", grid_bot + 28)]
    lane_end = [-1e9] * len(lanes)
    out, names = [], []
    for x, y, world in spots:
        name = world["name"]
        tw = len(name) * 9.5 * 0.6
        lx = min(max(x, 28 + tw / 2), w - 28 - tw / 2)
        for li, (side, ly) in enumerate(lanes):
            if lx - tw / 2 > lane_end[li] + 8:
                lane_end[li] = lx + tw / 2
                break
        else:
            continue  # no room: skip the tag rather than overlap
        anchor_y = grid_top if side == "up" else grid_bot
        tip_y = ly + 3 if side == "up" else ly - 9
        col = C["drydock"] if world.get("status") == "building" else C["accent2"]
        out.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x:.0f}" y2="{anchor_y:.0f}" stroke="{col}" stroke-opacity=".35" stroke-dasharray="1 2"/>')
        out.append(f'<line x1="{x:.0f}" y1="{anchor_y:.0f}" x2="{lx:.0f}" y2="{tip_y:.0f}" stroke="{col}" stroke-opacity=".35"/>')
        out.append(_planet(x, y, world.get("status", "shipped")))
        out.append(f'<text x="{lx:.0f}" y="{ly:.0f}" font-size="9.5" fill="{col}" text-anchor="middle" letter-spacing=".5">{esc(name)}</text>')
        names.append(name + (" (in progress)" if world.get("status") == "building" else ""))
    return {"svg": out, "names": names}


PATROL_MOVE, PATROL_CYCLE = 80.0, 86.0  # seconds flying, seconds per loop (the rest is a pause)


def _patrol(shown, stars, cell, top, left):
    """A scout ship sweeps the grid in a serpentine (down one week, up the next).
    Every active day flares as the ship passes. Pure SMIL, so it runs inside GitHub's <img>."""
    route = []
    for wi, week in enumerate(shown):
        days = range(len(week)) if wi % 2 == 0 else range(len(week) - 1, -1, -1)
        route.extend((wi, di) for di in days)
    n = len(route)
    sx, sy = left, top
    pts = [(left + wi * cell - sx, top + di * cell - sy) for wi, di in route]
    path = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    move_frac = PATROL_MOVE / PATROL_CYCLE

    pings = []
    for k, key in enumerate(route):
        x, y, level = stars[key]
        if level == 0:
            continue
        f = max(0.001, (k / max(1, n - 1)) * move_frac)
        f2, f3 = min(f + 0.004, 0.998), min(f + 0.035, 0.999)
        r = STAR_R[level] + 4
        pings.append(
            f'<circle class="ping" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="{STAR_FILL[4]}" '
            f'stroke-width="1.2" opacity="0"><animate attributeName="opacity" values="0;0;0.9;0;0" '
            f'keyTimes="0;{f:.4f};{f2:.4f};{f3:.4f};1" dur="{PATROL_CYCLE:.0f}s" repeatCount="indefinite"/></circle>'
        )
    ship = (
        f'<g class="ship" transform="translate({sx},{sy})"><g>'
        f'<animateMotion path="{path}" rotate="auto" dur="{PATROL_CYCLE:.0f}s" repeatCount="indefinite" '
        f'keyPoints="0;1;1" keyTimes="0;{move_frac:.4f};1" calcMode="linear"/>'
        f'<circle class="engine" cx="-6" cy="0" r="2.6" fill="{C["accent2"]}"/>'
        f'<path d="M10,0 L-6,-5.5 L-3,0 L-6,5.5 Z" fill="{C["text"]}"/>'
        f'<circle cx="3" cy="0" r="1.4" fill="{C["accent"]}"/>'
        f"</g></g>"
    )
    return "".join(pings) + ship


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
