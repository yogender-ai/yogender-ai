"""Render the galaxy: everyone who signed this profile orbits it as a planet.

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
import sys
import urllib.error
import urllib.request
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live import publish  # noqa: E402

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


def avatar_data_uri(login, size=96):
    """Fetch an avatar and inline it. Returns None if the person has vanished."""
    url = f"https://github.com/{login}.png?size={size}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "profile-wall/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
        # GitHub hands back JPEG for uploaded photos and PNG for identicons; label it truthfully.
        mime = "image/jpeg" if raw[:3] == b"\xff\xd8\xff" else "image/png"
        return f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")
    except Exception as exc:
        print(f"  ! could not fetch avatar for {login}: {exc}")
        return None


def render(visitors):
    """Everyone who signed becomes a planet orbiting the profile's sun."""
    import math
    import random
    W, H, CX, CY = 1200, 560, 600, 318
    rnd = random.Random(len(visitors))
    stars = "".join(
        f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, H):.0f}" r="{rnd.choice([.5, .7, 1, 1.3])}" fill="#fff" '
        f'class="tw" style="animation-delay:{rnd.uniform(0, 4):.1f}s"/>' for _ in range(150))

    # Fill rings from the inside out; the outermost ring takes any overflow.
    caps, rings, left = [6, 10, 14, 18], [], list(enumerate(visitors))
    for k, cap in enumerate(caps):
        take = left if k == len(caps) - 1 else left[:cap]
        if take:
            rings.append((k, take))
        left = left[len(take):]

    orbits, planets, defs = [], [], []
    newest = len(visitors) - 1
    for k in range(len(caps)):  # every orbit is drawn, so empty ones read as room to join
        rx = 170 + 118 * k
        orbits.append(f'<ellipse cx="{CX}" cy="{CY}" rx="{rx}" ry="{rx * .3:.0f}" fill="none" stroke="{RING[k % len(RING)]}" '
                      f'stroke-opacity=".3" stroke-dasharray="{"3 7" if k % 2 else "none"}"/>')
    for k, members in rings:
        rx = 170 + 118 * k
        ry = rx * .3
        dur = 60 + 30 * k
        col = RING[k % len(RING)]
        path = f"M{CX + rx} {CY}A{rx} {ry:.0f} 0 1 1 {CX - rx} {CY}A{rx} {ry:.0f} 0 1 1 {CX + rx} {CY}"
        for j, (i, v) in enumerate(members):
            begin = -dur * j / len(members)
            r = 21 if i != newest else 26
            uri = avatar_data_uri(v["login"])
            cid = f"c{i}"
            defs.append(f'<clipPath id="{cid}"><circle r="{r - 2}"/></clipPath>')
            face = (f'<image href="{uri}" x="{-r}" y="{-r}" width="{2 * r}" height="{2 * r}" clip-path="url(#{cid})" '
                    f'preserveAspectRatio="xMidYMid slice"/>' if uri else f'<circle r="{r - 2}" fill="{PANEL}"/>')
            name = v["login"] if len(v["login"]) <= 12 else v["login"][:11] + "…"
            glow = (f'<circle r="{r + 4}" fill="none" stroke="{LIME}" stroke-width="2" class="new"/>'
                    if i == newest else "")
            planets.append(f"""
  <g><animateMotion dur="{dur}s" repeatCount="indefinite" begin="{begin:.2f}s" path="{path}"/>
    <circle r="{r + 9}" fill="{col}" opacity=".16"/>{glow}{face}
    <circle r="{r - 1}" fill="none" stroke="{col}" stroke-width="2"/>
    <text y="{r + 15}" text-anchor="middle" class="nm">@{escape(name)}</text></g>""")

    count = len(visitors)
    latest = escape(visitors[-1]["login"]) if visitors else "nobody yet"
    inner = f"""
<defs>
  <radialGradient id="bg" cx=".5" cy=".55" r=".75"><stop offset="0" stop-color="#160c38"/><stop offset=".6" stop-color="#080818"/><stop offset="1" stop-color="{BG}"/></radialGradient>
  <radialGradient id="sun" cx=".38" cy=".33" r=".7"><stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="#fde68a"/><stop offset=".7" stop-color="{AMBER}"/><stop offset="1" stop-color="#b45309"/></radialGradient>
  <radialGradient id="corona" r=".5"><stop offset=".35" stop-color="{AMBER}" stop-opacity=".55"/><stop offset=".7" stop-color="{PINK}" stop-opacity=".15"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
  <linearGradient id="wg" x1="0" x2="1" spreadMethod="reflect">
    <stop offset="0" stop-color="#c4b5fd"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0;0 0" dur="9s" repeatCount="indefinite"/>
  </linearGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  {"".join(defs)}
</defs>
<style>
  .tw{{animation:tw 3.5s ease-in-out infinite}} @keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.95}}}}
  .co{{animation:co 4s ease-in-out infinite;transform-origin:{CX}px {CY}px}} @keyframes co{{50%{{transform:scale(1.15)}}}}
  .new{{animation:nw 1.6s ease-out infinite;transform-box:fill-box;transform-origin:center}} @keyframes nw{{from{{transform:scale(1);opacity:1}}to{{transform:scale(1.6);opacity:0}}}}
  .tag{{font:700 12px {MONO};letter-spacing:2px;fill:{PINK}}}
  .ttl{{font:800 30px {SANS};fill:url(#wg)}}
  .sub{{font:600 13px {MONO};fill:{MUTED}}}
  .cnt{{font:800 46px {SANS};fill:{TEXT}}}
  .nm{{font:600 10.5px {MONO};fill:{TEXT};paint-order:stroke;stroke:{BG};stroke-width:3px}}
  .core{{font:800 22px {SANS};fill:#3b1d00}}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  {stars}
  {"".join(orbits)}
  <circle class="co" cx="{CX}" cy="{CY}" r="95" fill="url(#corona)"/>
  <circle cx="{CX}" cy="{CY}" r="40" fill="url(#sun)"/>
  <text x="{CX}" y="{CY + 8}" text-anchor="middle" class="core">Y</text>
  {"".join(planets)}
  <text x="40" y="56" class="tag">// THE GALAXY</text>
  <text x="40" y="92" class="ttl">Join my galaxy — become a planet</text>
  <text x="40" y="116" class="sub">click 🪐 join below · a bot puts your avatar in orbit, forever</text>
  <text x="{W - 40}" y="92" text-anchor="end" class="cnt">{count}</text>
  <text x="{W - 40}" y="116" text-anchor="end" class="sub">{'planet' if count == 1 else 'planets'} in orbit</text>
  <text x="40" y="{H - 26}" class="sub"><tspan fill="{LIME}">●</tspan> newest arrival: @{latest}</text>
  <text x="{W - 40}" y="{H - 26}" text-anchor="end" class="sub" fill="{DIM}">updated {escape(dt.datetime.now(TZ).strftime('%d %b %Y'))}</text>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{EDGE}"/>
"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{count} people have joined this profile\'s galaxy">'
            f"<title>{count} people have joined this profile's galaxy</title>{inner}</svg>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", help="GitHub login to add before rendering")
    args = ap.parse_args()

    visitors = load()
    if args.add:
        visitors, added = add(visitors, args.add)
        print(f"{'added' if added else 'already present:'} {args.add}")
        save(visitors)

    body = render(visitors)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    print(f"wrote assets/wall.svg and assets/live/{publish('wall', body)} — {len(visitors)} planet(s)")


if __name__ == "__main__":
    main()
