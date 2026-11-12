"""Orchestrator: load data, draw every panel, write README. Usage: python build.py [--mock]"""

import json
import sys
from datetime import datetime, timezone
from html import escape as html_escape
from pathlib import Path

import fetch
import panels_live as live_p
import panels_static as static_p

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
TEMPLATE = Path(__file__).with_name("readme_template.md")

HEADINGS = [
    ("log", "CAPTAIN'S LOG"), ("primary", "PRIMARY MISSION"), ("second", "SECOND IN COMMAND"),
    ("drydock", "IN DRYDOCK"), ("fleet", "ACTIVE FLEET"), ("away", "AWAY MISSIONS"),
    ("commendations", "COMMENDATIONS"), ("transmissions", "TRANSMISSIONS FROM DEV"),
    ("sensors", "SHIP'S SENSORS"), ("orders", "STANDING ORDERS"), ("hailing", "HAILING FREQUENCIES OPEN"),
]


def write(name, content):
    path = ASSETS / name
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")


def alt(text):
    return html_escape(" ".join(str(text).split()), quote=True)


def card_link(url, src, label, width):
    return f'<a href="{alt(url)}"><img src="{src}" width="{width}" alt="{alt(label)}"></a>'


def main(mock=False):
    profile = json.loads((DATA / "profile.json").read_text(encoding="utf-8"))
    if mock:
        live = json.loads((DATA / "mock-live.json").read_text(encoding="utf-8"))
    else:
        live = fetch.gather(profile, DATA / "live-cache.json")
        cache = {k: v for k, v in live.items() if k != "failures"}
        (DATA / "live-cache.json").write_text(json.dumps(cache, indent=1) + "\n", encoding="utf-8")

    ASSETS.mkdir(exist_ok=True)
    stardate = datetime.now(timezone.utc).strftime("%Y.%m")

    write("header.svg", static_p.header(profile, live, stardate))
    for i, (slug, title) in enumerate(HEADINGS, 1):
        write(f"h-{slug}.svg", static_p.heading(i, title, f"SEC.{i:02d}"))
    write("mission-verity.svg", static_p.mission_card(profile["primary"]))
    write("mission-agentis.svg", static_p.mission_card(profile["second"]))
    write("mission-deadkeys.svg", static_p.mission_card(profile["drydock"]))
    for f in profile["fleet"] + profile["away"]:
        write(f"card-{f['slug']}.svg", static_p.fleet_card(f))
    for link in profile["links"]:
        write(f"link-{link['slug']}.svg", static_p.link_tile(link))
    write("commendations.svg", static_p.commendations(profile["commendations"]))
    write("footer.svg", static_p.footer())
    write("stats.svg", live_p.stats(live))
    write("starchart.svg", live_p.starchart(live))

    gems = set(profile.get("gem_slugs", []))
    tx_md = []
    latest = live.get("latest") or []
    for i, post in enumerate(latest[:3], 1):
        is_gem = post.get("slug") in gems
        write(f"post-{i}.svg", live_p.transmission(post, is_gem))
        tx_md.append(card_link(post["url"], f"assets/post-{i}.svg", f'DEV post: {post["title"]}', "100%"))
    for i in range(len(latest[:3]) + 1, 4):  # never leave a stale card behind
        stale = ASSETS / f"post-{i}.svg"
        if stale.exists():
            stale.unlink()
    if not tx_md:
        write("post-empty.svg", live_p.transmission_empty())
        tx_md.append(card_link(f"https://dev.to/{profile['devto_user']}", "assets/post-empty.svg", "Latest DEV posts unavailable right now", "100%"))

    def cards(items):
        return "\n".join(card_link(f["url"], f"assets/card-{f['slug']}.svg",
                                   f'{f["name"]}, {f["role"]}: {f["line"]}', "49%") for f in items)

    tiles = "\n".join(card_link(l["url"], f"assets/link-{l['slug']}.svg", f'{l["label"]} ({l["sub"]})', "19%")
                      for l in profile["links"])

    m = profile
    fills = {
        "header_alt": alt(f'{m["name"]}: {m["tagline"]} {m["subtitle"]}'),
        "alt_verity": alt(f'Primary mission: Verity Lex, live. {m["primary"]["hook"]} {m["primary"]["body"]}'),
        "alt_agentis": alt(f'Second in command: Agentis Lux, live. {m["second"]["hook"]} {m["second"]["body"]}'),
        "alt_deadkeys": alt(f'In drydock: Dead Keys. {m["drydock"]["hook"]} {m["drydock"]["body"]}'),
        "fleet_cards": cards(m["fleet"]),
        "away_cards": cards(m["away"]),
        "alt_commendations": alt("Commendations: " + "; ".join(f"{n} ({y}): {d}" for _, n, y, d in m["commendations"])),
        "transmissions": "\n\n".join(tx_md),
        "alt_stats": alt(f'Ship\'s sensors: {live.get("public_repos", "--")} public repos, {live.get("dev_posts", "--")} DEV posts, '
                         f'{live.get("dev_reactions", "--")} DEV reactions, {live.get("contrib_total", "--")} contributions this year'),
        "alt_starchart": alt(f'Star chart: one star per day of GitHub contributions over the last year, {live.get("contrib_total", "--")} in total'),
        "link_tiles": tiles,
        "fetched_at": alt(live.get("fetched_at", "pending")),
    }
    readme = TEMPLATE.read_text(encoding="utf-8")
    for key, val in fills.items():
        readme = readme.replace("{{" + key + "}}", val)
    leftover = [p for p in ("{{",) if p in readme]
    if leftover:
        raise SystemExit("Template placeholder left unfilled")
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    failed = live.get("failures") or []
    print(f"Built profile. Failed sources (cache used): {failed or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(mock="--mock" in sys.argv))
