"""Panels drawn from data/profile.json only. No network here."""

import random

from theme import (C, STATUS_LABEL, WIDTH, brackets, esc, panel_bg, status_dot, svg,
                   text_lines, wrap)


def header(profile, stats, stardate):
    w, h = WIDTH, 270
    rnd = random.Random(1701)  # fixed seed: same sky every run, no noisy diffs
    stars = []
    for i in range(80):
        x, y, r = rnd.uniform(8, w - 8), rnd.uniform(8, h - 8), rnd.choice([0.6, 0.8, 1.0, 1.4])
        cls = f' class="tw tw{i % 3}"' if i % 4 == 0 else ""
        stars.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#ffffff" opacity="0.55"{cls}/>')
    typed = "> TEA. EARL GREY. HOT."
    typed_w = len(typed) * 22 * 0.6 + 4
    chips = [
        ("STATUS", "ON DUTY", C["live"]),
        ("HOME PORT", "CA COURTS", C["accent"]),
        ("FLEET", f"{stats.get('public_repos', '60+')} REPOS", C["accent2"]),
        ("DEV", f"{stats.get('dev_posts', '60+')} POSTS", C["docked"]),
    ]
    chip_svg, cx = [], 36
    for k, v, col in chips:
        label = f"{k} "
        cw = int((len(label) + len(v)) * 11 * 0.6 + 24)
        chip_svg.append(
            f'<rect x="{cx}" y="214" width="{cw}" height="26" rx="4" fill="{C["panel"]}" stroke="{col}" stroke-opacity="0.7"/>'
            f'<text x="{cx + 12}" y="231" font-size="11" fill="{C["dim"]}">{esc(label)}<tspan fill="{col}" font-weight="700">{esc(v)}</tspan></text>'
        )
        cx += cw + 10
    body = (
        panel_bg(w, h, 12)
        + "".join(stars)
        + brackets(14, 14, w - 28, h - 28, C["accent"])
        + f'<text x="36" y="46" font-size="12" fill="{C["dim"]}" letter-spacing="2">BRIDGE CONSOLE // {esc(profile["handle"].upper())}</text>'
        + f'<text x="{w - 36}" y="46" font-size="12" fill="{C["accent2"]}" text-anchor="end" letter-spacing="2">STARDATE {esc(stardate)}</text>'
        + f'<line x1="36" y1="58" x2="{w - 36}" y2="58" stroke="{C["line"]}"/>'
        + '<clipPath id="type"><rect x="34" y="70" height="34" width="' + f"{typed_w:.0f}" + '">'
        + f'<animate attributeName="width" values="0;{typed_w:.0f}" dur="2.2s" fill="freeze"/></rect></clipPath>'
        + f'<text x="36" y="96" font-size="22" fill="{C["accent"]}" clip-path="url(#type)">{esc(typed)}</text>'
        + f'<rect x="{36 + typed_w:.0f}" y="78" width="12" height="22" fill="{C["accent"]}" class="cursor"/>'
        + f'<text x="36" y="152" font-size="44" font-weight="700" fill="{C["text"]}" letter-spacing="3">{esc(profile["name"])}</text>'
        + f'<text x="36" y="182" font-size="17" fill="{C["accent2"]}">{esc(profile["tagline"])}</text>'
        + f'<text x="36" y="202" font-size="12.5" fill="{C["dim"]}">{esc(profile["subtitle"])}</text>'
        + "".join(chip_svg)
    )
    style = """
  .tw { animation: tw 3.2s ease-in-out infinite; }
  .tw1 { animation-delay: 1.1s; } .tw2 { animation-delay: 2.2s; }
  @keyframes tw { 0%,100% { opacity: .15; } 50% { opacity: .95; } }
  .cursor { animation: blink 1s steps(1) infinite; }
  @keyframes blink { 50% { opacity: 0; } }
"""
    label = f'{profile["name"]}: {profile["tagline"]} {profile["subtitle"]} Stardate {stardate}.'
    return svg(w, h, body, label, style)


def heading(num, title, code):
    w, h = WIDTH, 52
    tw = (len(title) + 3) * (16 * 0.6 + 1.5)  # include "// " and letter-spacing
    body = (
        panel_bg(w, h, 8)
        + f'<path d="M14,26 L22,18 L30,26 L22,34 Z" fill="{C["accent"]}"/>'
        f'<text x="42" y="32" font-size="13" fill="{C["accent2"]}" font-weight="700">{num:02d}</text>'
        f'<text x="70" y="32" font-size="16" font-weight="700" fill="{C["text"]}" letter-spacing="1.5">// {esc(title)}</text>'
        f'<line x1="{70 + tw + 14:.0f}" y1="27" x2="{w - 90}" y2="27" stroke="{C["line"]}"/>'
        f'<text x="{w - 14}" y="31" font-size="11" fill="{C["dim"]}" text-anchor="end" letter-spacing="2">{esc(code)}</text>'
    )
    return svg(w, h, body, title.title())


def mission_card(m):
    w, pad = WIDTH, 32
    inner = w - pad * 2
    hook = wrap(m["hook"], inner, 17)
    body_l = wrap(m["body"], inner, 14)
    y_name = 86
    y_hook = y_name + 38
    y_body = y_hook + len(hook) * 17 * 1.45 + 14
    y_stack = y_body + len(body_l) * 14 * 1.5 + 16
    h = int(y_stack + 56)
    color = C.get(m["status"], C["dim"])
    body = (
        panel_bg(w, h, 12)
        + brackets(12, 12, w - 24, h - 24, color)
        + status_dot(pad + 6, 48, m["status"])
        + f'<text x="{pad + 24}" y="53" font-size="12" letter-spacing="2" fill="{C["dim"]}">{esc(m["label"])}</text>'
        + f'<text x="{w - pad}" y="53" font-size="12" letter-spacing="2" fill="{color}" text-anchor="end" font-weight="700">{STATUS_LABEL[m["status"]]}</text>'
        + f'<text x="{pad}" y="{y_name}" font-size="30" font-weight="700" fill="{C["text"]}">{esc(m["name"])}</text>'
        + text_lines(hook, pad, y_hook, 17, C["accent"], weight=700)
        + text_lines(body_l, pad, y_body, 14, C["text"], gap=1.5)
        + f'<line x1="{pad}" y1="{y_stack - 6:.0f}" x2="{w - pad}" y2="{y_stack - 6:.0f}" stroke="{C["line"]}"/>'
        + f'<text x="{pad}" y="{y_stack + 16:.0f}" font-size="12.5" fill="{C["accent2"]}">{esc(m["stack"])}</text>'
        + f'<text x="{pad}" y="{y_stack + 38:.0f}" font-size="12" fill="{C["dim"]}">{esc(m["footer"])}</text>'
    )
    label = f'{m["label"].title()}: {m["name"]}, {STATUS_LABEL[m["status"]].lower()}. {m["hook"]} {m["body"]}'
    return svg(w, h, body, label)


def fleet_card(f):
    w, h, pad = 410, 214, 24
    color = C.get(f["status"], C["dim"])
    lines = wrap(f["line"], w - pad * 2, 13.5, max_lines=4)
    body = (
        panel_bg(w, h, 10)
        + brackets(8, 8, w - 16, h - 16, color, arm=10)
        + status_dot(pad + 6, 36, f["status"])
        + f'<text x="{pad + 22}" y="41" font-size="11" letter-spacing="2" fill="{color}" font-weight="700">{STATUS_LABEL[f["status"]]}</text>'
        + f'<text x="{w - pad}" y="41" font-size="11" letter-spacing="1.5" fill="{C["accent2"]}" text-anchor="end">{esc(f["role"].upper())}</text>'
        + f'<text x="{pad}" y="76" font-size="21" font-weight="700" fill="{C["text"]}">{esc(f["name"])}</text>'
        + text_lines(lines, pad, 104, 13.5, C["text"], gap=1.5)
        + f'<text x="{pad}" y="{h - 22}" font-size="11.5" fill="{C["dim"]}">{esc(f["note"])}</text>'
    )
    label = f'{f["name"]}, {f["role"]}, {STATUS_LABEL[f["status"]].lower()}. {f["line"]} {f["note"]}.'
    return svg(w, h, body, label)


def link_tile(link):
    w, h = 160, 64
    body = (
        panel_bg(w, h, 8)
        + f'<path d="M0,10 Q0,0 10,0 L14,0 L14,{h} L10,{h} Q0,{h} 0,{h - 10} Z" fill="{C["accent"]}"/>'
        + f'<text x="28" y="30" font-size="13" font-weight="700" fill="{C["text"]}" letter-spacing="1">{esc(link["label"])}</text>'
        + f'<text x="28" y="48" font-size="11" fill="{C["dim"]}">{esc(link["sub"])}</text>'
        + f'<text x="{w - 14}" y="48" font-size="14" fill="{C["accent2"]}" text-anchor="end">&gt;</text>'
    )
    return svg(w, h, body, f'{link["label"].title()} ({link["sub"]})')


TAG_COLOR = {"WIN": "drydock", "HONOR": "docked", "TALK": "accent"}


def commendations(rows):
    w, pad, row_h = WIDTH, 28, 54
    h = 40 + len(rows) * row_h + 16
    out = [panel_bg(w, h, 12), brackets(10, 10, w - 20, h - 20, C["accent2"])]
    for i, (tag, name, year, detail) in enumerate(rows):
        y = 40 + i * row_h
        col = C[TAG_COLOR.get(tag, "dim")]
        if i:
            out.append(f'<line x1="{pad}" y1="{y - 8}" x2="{w - pad}" y2="{y - 8}" stroke="{C["grid"]}"/>')
        out.append(f'<rect x="{pad}" y="{y + 2}" width="64" height="22" rx="4" fill="none" stroke="{col}"/>')
        out.append(f'<text x="{pad + 32}" y="{y + 17}" font-size="11" font-weight="700" fill="{col}" text-anchor="middle" letter-spacing="1.5">{esc(tag)}</text>')
        out.append(f'<text x="{pad + 82}" y="{y + 12}" font-size="14" font-weight="700" fill="{C["text"]}">{esc(name)}</text>')
        out.append(f'<text x="{pad + 82}" y="{y + 31}" font-size="12" fill="{C["dim"]}">{esc(detail)}</text>')
        out.append(f'<text x="{w - pad}" y="{y + 12}" font-size="12" fill="{C["accent2"]}" text-anchor="end">{esc(year)}</text>')
    label = "Commendations: " + "; ".join(f"{t.title()}: {n} ({y}), {d}" for t, n, y, d in rows)
    return svg(w, h, "".join(out), label)


def footer():
    w, h = WIDTH, 120
    msg = "> END TRANSMISSION"
    body = (
        panel_bg(w, h, 12)
        + brackets(10, 10, w - 20, h - 20, C["accent"])
        + f'<text x="{w / 2}" y="52" font-size="20" fill="{C["accent"]}" text-anchor="middle" letter-spacing="3">{esc(msg)}<tspan class="cursor">_</tspan></text>'
        + f'<text x="{w / 2}" y="80" font-size="12.5" fill="{C["text"]}" text-anchor="middle">AI assisted. Human approved. Powered by NLP. All mistakes are mine.</text>'
        + f'<text x="{w / 2}" y="100" font-size="11.5" fill="{C["dim"]}" text-anchor="middle">Home port Ventura · on duty in Santa Barbara · earl grey, hot</text>'
    )
    style = """
  .cursor { animation: blink 1s steps(1) infinite; }
  @keyframes blink { 50% { opacity: 0; } }
"""
    return svg(w, h, body, "End transmission. AI assisted. Human approved. Powered by NLP.", style)
