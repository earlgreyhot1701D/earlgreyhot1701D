"""Network layer. Every call is wrapped; a failed source falls back to the last good cache."""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

TIMEOUT = 20
UA = {"User-Agent": "earlgreyhot1701D-profile-builder"}


def _get_json(url, headers=None, data=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})}, data=data)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.load(resp)


def fetch_devto(user):
    articles, page = [], 1
    while page <= 5:  # hard ceiling: 5 pages x 1000 posts
        batch = _get_json(f"https://dev.to/api/articles?username={user}&per_page=1000&page={page}")
        if not isinstance(batch, list):
            raise ValueError("DEV API returned an unexpected shape")
        articles.extend(batch)
        if len(batch) < 1000:
            break
        page += 1
    latest = []
    for a in articles[:3]:
        latest.append({
            "title": str(a.get("title", "")).strip() or "(untitled)",
            "url": str(a.get("url", "")),
            "slug": str(a.get("slug", "")),
            "date": str(a.get("readable_publish_date", "")),
            "reactions": int(a.get("public_reactions_count") or 0),
            "comments": int(a.get("comments_count") or 0),
        })
    return {
        "dev_posts": len(articles),
        "dev_reactions": sum(int(a.get("public_reactions_count") or 0) for a in articles),
        "latest": latest,
    }


def _gh_headers():
    token = os.environ.get("GITHUB_TOKEN", "")
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def fetch_github_user(login):
    u = _get_json(f"https://api.github.com/users/{login}", _gh_headers())
    return {"public_repos": int(u.get("public_repos") or 0), "followers": int(u.get("followers") or 0)}


QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def fetch_contributions(login):
    if not os.environ.get("GITHUB_TOKEN"):
        raise RuntimeError("GraphQL needs GITHUB_TOKEN")
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    res = _get_json("https://api.github.com/graphql", {**_gh_headers(), "Content-Type": "application/json"}, body)
    cal = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[LEVELS.get(d["contributionLevel"], 0) for d in w["contributionDays"]] for w in cal["weeks"]]
    days = [(d["date"], int(d["contributionCount"])) for w in cal["weeks"] for d in w["contributionDays"]]
    peak_date, peak = max(days, key=lambda d: d[1]) if days else ("", 0)
    longest = run = 0
    for _, count in days:
        run = run + 1 if count > 0 else 0
        longest = max(longest, run)
    return {"contrib_total": int(cal["totalContributions"]), "contrib_weeks": weeks,
            "contrib_peak": {"date": peak_date, "count": peak}, "contrib_longest_streak": longest,
            "contrib_week_starts": [w["contributionDays"][0]["date"] for w in cal["weeks"] if w["contributionDays"]]}


def gather(profile, cache_path):
    """Return live data. Each source that fails keeps its last cached value."""
    try:
        with open(cache_path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    sources = (
        ("dev", lambda: fetch_devto(profile["devto_user"])),
        ("github", lambda: fetch_github_user(profile["handle"])),
        ("contrib", lambda: fetch_contributions(profile["handle"])),
    )
    failures = []
    for name, fn in sources:
        try:
            data.update(fn())
        except Exception as exc:
            failures.append(name)
            print(f"[warn] {name} fetch failed, keeping cache: {exc}", file=sys.stderr)
    if len(failures) < len(sources):
        data["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data["failures"] = failures
    return data
