"""Build an animated GitHub stats card (dist/stats.svg) from the GraphQL API.

In CI:   GITHUB_TOKEN=... GH_LOGIN=yogender-ai python .github/scripts/gen_stats.py --out dist/stats.svg
Locally: gh api graphql -F login=yogender-ai -f query=@.github/scripts/stats.graphql > data.json
         python .github/scripts/gen_stats.py --data data.json --out stats.svg
"""
import argparse
import datetime as dt
import json
import os
import urllib.request
from xml.sax.saxutils import escape

HERE = os.path.dirname(__file__)
PANEL, EDGE = "#0b0d1a", "#1e1b4b"
VIOLET, CYAN, PINK, LIME, AMBER = "#8b5cf6", "#22d3ee", "#f472b6", "#a3e635", "#fbbf24"
TEXT, MUTED, DIM = "#e2e8f0", "#94a3b8", "#475569"
SANS = "'Segoe UI', 'SF Pro Display', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', 'SF Mono', Consolas, Menlo, monospace"
SKIP_LANGS = {"HTML", "CSS", "SCSS", "Jupyter Notebook"}  # markup/notebooks would drown out real code
LEVELS = ["#161b33", "#3b1f7a", "#6d28d9", "#8b5cf6", "#c4b5fd"]


def fetch(login, token):
    query = open(os.path.join(HERE, "stats.graphql"), encoding="utf-8").read()
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": query, "variables": {"login": login}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today not counted yet
        i -= 1
    while i >= 0 and counts[i]:
        cur += 1
        i -= 1
    return cur, longest


def build(data):
    u = data["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    cur, longest = streaks(days)
    repos = u["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)
    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            if n in SKIP_LANGS:
                continue
            langs.setdefault(n, [0, e["node"]["color"] or MUTED])[0] += e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    total_bytes = sum(v[0] for _, v in top) or 1

    W, H = 1200, 400
    tiles = [("CONTRIBUTIONS", f"{cal['totalContributions']:,}", "last 12 months", VIOLET),
             ("CURRENT STREAK", f"{cur}", "days in a row", LIME),
             ("LONGEST STREAK", f"{longest}", "days", AMBER),
             ("PUBLIC REPOS", f"{u['repositories']['totalCount']}", f"{stars} stars earned", CYAN)]
    t_svg = []
    for i, (label, val, sub, col) in enumerate(tiles):
        x, y = 32 + (i % 2) * 200, 32 + (i // 2) * 128
        t_svg.append(f'<g transform="translate({x} {y})" class="fi" style="animation-duration:{.6 + i * .15:.2f}s">'
                     f'<rect width="184" height="112" rx="14" fill="{col}" fill-opacity=".07" stroke="{col}" stroke-opacity=".35"/>'
                     f'<text x="16" y="28" class="lb" fill="{col}">{label}</text>'
                     f'<text x="16" y="72" class="big">{escape(val)}</text>'
                     f'<text x="16" y="96" class="sub">{escape(sub)}</text></g>')

    # heatmap: last 30 weeks
    weeks = cal["weeks"][-30:]
    cell, gap, hx, hy = 15, 4, 470, 64
    mx = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=1) or 1
    h_svg = []
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            wd = dt.date.fromisoformat(d["date"]).isoweekday() % 7
            c = d["contributionCount"]
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / mx + .5))
            h_svg.append(f'<rect x="{hx + wi * (cell + gap)}" y="{hy + wd * (cell + gap)}" width="{cell}" height="{cell}" rx="4" '
                         f'fill="{LEVELS[lvl]}" class="hc" style="animation-delay:{wi * .06 + wd * .02:.2f}s"/>')
    legend = "".join(f'<rect x="{1044 + i * 19}" y="210" width="15" height="15" rx="4" fill="{c}"/>' for i, c in enumerate(LEVELS))

    # languages stacked bar
    bx, by, bw = 470, 290, 698
    segs, lg, x = [], [], bx
    for i, (name, (size, col)) in enumerate(top):
        w = bw * size / total_bytes
        segs.append(f'<rect x="{x:.1f}" y="{by}" width="{max(w - 3, 1):.1f}" height="14" rx="4" fill="{col}" class="gr" style="animation-duration:{.9 + i * .15:.2f}s"/>')
        x += w
        lx, ly = bx + (i % 3) * 232, by + 44 + (i // 3) * 28
        lg.append(f'<circle cx="{lx + 6}" cy="{ly - 5}" r="6" fill="{col}"/><text x="{lx + 20}" y="{ly}" class="lg">{escape(name)} '
                  f'<tspan fill="{DIM}">{100 * size / total_bytes:.1f}%</tspan></text>')

    updated = dt.datetime.utcnow().strftime("%d %b %Y · %H:%M UTC")
    inner = f"""
<style>
  .lb{{font:700 11px {MONO};letter-spacing:2px}} .big{{font:800 38px {SANS};fill:{TEXT}}} .sub{{font:500 12px {SANS};fill:{MUTED}}}
  .h{{font:700 13px {MONO};letter-spacing:3px;fill:{VIOLET}}} .lg{{font:500 14px {SANS};fill:{TEXT}}} .u{{font:500 11px {MONO};fill:{DIM}}}
  .fi{{animation:fi .8s ease-out}} @keyframes fi{{from{{opacity:0;transform:translateY(10px)}}}}
  .hc{{animation:hc 4s ease-in-out infinite}} @keyframes hc{{0%,70%,100%{{opacity:1}}80%{{opacity:.35}}}}
  .gr{{transform-box:fill-box;transform-origin:left;animation:gr 1.2s cubic-bezier(.2,.8,.2,1)}} @keyframes gr{{from{{transform:scaleX(0)}}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="{PANEL}" stroke="{EDGE}"/>
{''.join(t_svg)}
<text x="{hx}" y="44" class="h">// LAST 30 WEEKS</text>
{''.join(h_svg)}
<text x="1010" y="222" class="u">less</text>{legend}<text x="1142" y="222" class="u">more</text>
<text x="{bx}" y="276" class="h">// TOP LANGUAGES</text>
<rect x="{bx}" y="{by}" width="{bw}" height="14" rx="4" fill="{EDGE}" fill-opacity=".5"/>
{''.join(segs)}{''.join(lg)}
<text x="32" y="{H - 22}" class="u">auto-updated by GitHub Actions · {updated}</text>
"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="GitHub stats"><title>GitHub stats</title>{inner}</svg>\n')


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data")
    ap.add_argument("--out", default="dist/stats.svg")
    a = ap.parse_args()
    if a.data:
        data = json.load(open(a.data, encoding="utf-8"))
    else:
        data = fetch(os.environ.get("GH_LOGIN", "yogender-ai"), os.environ["GITHUB_TOKEN"])
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8", newline="\n").write(build(data))
    print("wrote", a.out)
