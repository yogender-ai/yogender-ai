"""Render the wall of people who have signed this profile.

Anyone who opens the "sign" issue gets added to data/visitors.json by the
workflow, and this redraws the wall. Their avatar then lives on the profile.

Avatars are downloaded and embedded as data URIs rather than linked. GitHub
sanitises SVG and will not fetch external images from inside one, so a linked
avatar renders as an empty circle.

    python .github/scripts/wall.py            # redraw from visitors.json
    python .github/scripts/wall.py --add foo  # add a person, then redraw
"""
import argparse
import base64
import datetime as dt
import json
import os
import urllib.error
import urllib.request
from xml.sax.saxutils import escape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data", "visitors.json")
OUT = os.path.join(ROOT, "assets", "wall.svg")
TZ = dt.timezone(dt.timedelta(hours=5, minutes=30))

BG, PANEL, EDGE = "#05060f", "#0b0d1a", "#1e1b4b"
VIOLET, CYAN, PINK, LIME, AMBER = "#8b5cf6", "#22d3ee", "#f472b6", "#a3e635", "#fbbf24"
TEXT, MUTED, DIM = "#e2e8f0", "#94a3b8", "#475569"
SANS = "'Segoe UI','SF Pro Display',system-ui,-apple-system,sans-serif"
MONO = "'JetBrains Mono','Cascadia Code','SF Mono',Consolas,Menlo,monospace"

PER_ROW = 10
AV = 62          # avatar diameter
GAP = 22
RING = [VIOLET, CYAN, PINK, LIME, AMBER]


def load():
    if not os.path.exists(DATA):
        return []
    with open(DATA, encoding="utf-8") as fh:
        return json.load(fh).get("visitors", [])


def save(visitors):
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    with open(DATA, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"updated": dt.datetime.now(TZ).isoformat(timespec="seconds"),
                   "count": len(visitors),
                   "visitors": visitors}, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def add(visitors, login):
    login = login.strip().lstrip("@")
    if not login:
        return visitors, False
    if any(v["login"].lower() == login.lower() for v in visitors):
        return visitors, False          # already signed, never duplicate
    visitors.append({"login": login, "at": dt.datetime.now(TZ).date().isoformat()})
    return visitors, True


def avatar_data_uri(login, size=140):
    """Fetch an avatar and inline it. Returns None if the person has vanished."""
    url = f"https://github.com/{login}.png?size={size}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "profile-wall/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
        return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")
    except Exception as exc:
        print(f"  ! could not fetch avatar for {login}: {exc}")
        return None


def render(visitors):
    n = max(len(visitors), 1)
    rows = (n + PER_ROW - 1) // PER_ROW
    W = 1200
    top = 150
    cell = AV + GAP
    H = top + rows * (cell + 26) + 70

    span = min(len(visitors), PER_ROW) * cell - GAP
    x0 = (W - max(span, cell - GAP)) / 2

    tiles, defs = [], []
    for i, v in enumerate(visitors):
        r, c = divmod(i, PER_ROW)
        # Last row is centred on its own count rather than left-aligned.
        in_row = min(len(visitors) - r * PER_ROW, PER_ROW)
        rx0 = (W - (in_row * cell - GAP)) / 2
        x = rx0 + c * cell
        y = top + r * (cell + 26)
        ring = RING[i % len(RING)]
        uri = avatar_data_uri(v["login"])
        cid = f"clip{i}"
        defs.append(f'<clipPath id="{cid}"><circle cx="{x + AV/2:.1f}" cy="{y + AV/2:.1f}" r="{AV/2 - 2:.1f}"/></clipPath>')
        if uri:
            tiles.append(f'<image href="{uri}" x="{x:.1f}" y="{y:.1f}" width="{AV}" height="{AV}" '
                         f'clip-path="url(#{cid})" preserveAspectRatio="xMidYMid slice"/>')
        else:
            tiles.append(f'<circle cx="{x + AV/2:.1f}" cy="{y + AV/2:.1f}" r="{AV/2 - 2:.1f}" fill="{PANEL}"/>')
        tiles.append(f'<circle cx="{x + AV/2:.1f}" cy="{y + AV/2:.1f}" r="{AV/2 - 1:.1f}" fill="none" '
                     f'stroke="{ring}" stroke-width="2" opacity=".85"/>')
        name = v["login"] if len(v["login"]) <= 11 else v["login"][:10] + "…"
        tiles.append(f'<text x="{x + AV/2:.1f}" y="{y + AV + 17:.1f}" text-anchor="middle" '
                     f'style="font:600 10px {MONO};fill:{MUTED}">{escape(name)}</text>')

    if not visitors:
        tiles.append(f'<text x="{W/2}" y="{top + 40}" text-anchor="middle" '
                     f'style="font:600 15px {MONO};fill:{DIM}">nobody yet — be the first</text>')

    count = len(visitors)
    inner = f"""
<defs>
  <linearGradient id="wg" x1="0" x2="1">
    <stop offset="0" stop-color="{VIOLET}"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0;0 0" dur="9s" repeatCount="indefinite"/>
  </linearGradient>
  {"".join(defs)}
</defs>
<style>
  .tag{{font:700 12px {MONO};letter-spacing:2px;fill:{PINK}}}
  .ttl{{font:800 28px {SANS};fill:url(#wg)}}
  .sub{{font:600 13px {MONO};fill:{MUTED}}}
  .cnt{{font:800 42px {SANS};fill:{TEXT}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="{BG}" stroke="{EDGE}"/>
<rect x="28" y="24" width="{W - 56}" height="{H - 48}" rx="16" fill="{PANEL}" fill-opacity=".5" stroke="{EDGE}"/>
<text x="56" y="62" class="tag">// THE WALL</text>
<text x="56" y="98" class="ttl">People who signed this profile</text>
<text x="56" y="122" class="sub">one click adds your face here, forever</text>
<text x="{W - 56}" y="98" text-anchor="end" class="cnt">{count}</text>
<text x="{W - 56}" y="122" text-anchor="end" class="sub">{'signature' if count == 1 else 'signatures'}</text>
{"".join(tiles)}
<text x="{W/2}" y="{H - 34}" text-anchor="middle" style="font:600 11px {MONO};fill:{DIM}">
  rebuilt automatically whenever someone signs · {escape(dt.datetime.now(TZ).strftime('%d %b %Y'))}
</text>
"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{count} people have signed this profile">'
            f"<title>{count} people have signed this profile</title>{inner}</svg>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", help="GitHub login to add before rendering")
    args = ap.parse_args()

    visitors = load()
    if args.add:
        visitors, added = add(visitors, args.add)
        print(f"{'added' if added else 'already present:'} {args.add}")
        save(visitors)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(visitors))
    print(f"wrote assets/wall.svg — {len(visitors)} signature(s)")


if __name__ == "__main__":
    main()
