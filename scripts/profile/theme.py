"""Shared look: palette, font, and small SVG helpers. No panel logic here."""

from xml.sax.saxutils import escape as _escape

WIDTH = 840

C = {
    "bg": "#0b0f1a",
    "panel": "#111827",
    "grid": "#1f2937",
    "line": "#2d3748",
    "text": "#e6edf3",
    "dim": "#8b949e",
    "accent": "#9B59B6",
    "accent2": "#D97757",
    "live": "#3FB950",
    "docked": "#58A6FF",
    "drydock": "#E3B341",
}

STATUS_LABEL = {"live": "LIVE", "docked": "DOCKED", "drydock": "UNDER CONSTRUCTION"}

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"
CHAR_W = 0.6  # monospace advance width, as a fraction of font size


def esc(text):
    """XML-escape any text before it goes into an SVG."""
    return _escape(str(text), {'"': "&quot;"})


def wrap(text, width_px, size, max_lines=None):
    """Greedy word wrap using monospace metrics. Adds an ellipsis only if max_lines cuts it."""
    per_line = max(10, int(width_px / (size * CHAR_W)))
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) <= per_line:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        lines[-1] = (last[: per_line - 1] if len(last) >= per_line else last).rstrip() + "…"
    return lines


def text_lines(lines, x, y, size, color, gap=1.45, weight=400):
    out = []
    for i, line in enumerate(lines):
        out.append(
            f'<text x="{x}" y="{y + i * size * gap:.1f}" font-size="{size}" font-weight="{weight}" fill="{color}">{esc(line)}</text>'
        )
    return "".join(out)


def brackets(x, y, w, h, color, arm=14):
    """Corner brackets: the console frame motif."""
    p = []
    for cx, cy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        p.append(f"M{cx + dx * arm},{cy} L{cx},{cy} L{cx},{cy + dy * arm}")
    return f'<path d="{" ".join(p)}" fill="none" stroke="{color}" stroke-width="2"/>'


def status_dot(x, y, status, pulse=True):
    color = C.get(status, C["dim"])
    cls = ' class="pulse"' if pulse and status == "live" else ""
    return (
        f'<circle cx="{x}" cy="{y}" r="9" fill="{color}" opacity="0.18"{cls}/>'
        f'<circle cx="{x}" cy="{y}" r="4.5" fill="{color}"/>'
    )


BASE_STYLE = f"""
  text {{ font-family: {FONT}; }}
  .pulse {{ animation: pulse 2.4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes pulse {{ 0%,100% {{ opacity: .15; transform: scale(1); }} 50% {{ opacity: .45; transform: scale(1.5); }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""


def svg(w, h, body, label, style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(label)}"><title>{esc(label)}</title>'
        f"<style>{BASE_STYLE}{style}</style>{body}</svg>\n"
    )


def panel_bg(w, h, r=10):
    return (
        f'<rect width="{w}" height="{h}" rx="{r}" fill="{C["bg"]}"/>'
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="none" stroke="{C["line"]}"/>'
    )
