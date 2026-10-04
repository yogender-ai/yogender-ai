"""Generate the animated SVGs used by the profile README.

Edit the data below and run:  python .github/scripts/build_assets.py
Everything is pure SVG + CSS/SMIL (no JS, no external fonts) so GitHub renders it inside <img>.
"""
import datetime
import json
import os
import random
import re
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets")

# Live LeetCode numbers, written by sync_leetcode.py before this runs.
# These used to be literals scattered through the file that a set of regexes
# rewrote in place; every literal the regexes missed silently went stale.
STATS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leetcode_stats.json")

STATS_DEFAULT = {
    "total": 0, "easy": 0, "medium": 0, "hard": 0,
    "streak": 0, "active_days": 0,
    "rating": 0, "top_pct": 0, "contests": 0, "level": 17,
    "rank_title": "Algorithm Grandmaster",
}


def load_stats():
    s = dict(STATS_DEFAULT)
    try:
        with open(STATS_PATH, encoding="utf-8") as fh:
            s.update(json.load(fh))
    except FileNotFoundError:
        print(f"[assets] WARNING: {os.path.basename(STATS_PATH)} missing - "
              "run sync_leetcode.py first; rendering zeros")
    except Exception as exc:
        print(f"[assets] WARNING: could not read stats ({exc}); rendering zeros")
    return s


S = load_stats()
RATING_TXT = f"{round(S['rating'])} Rating (Top {round(S['top_pct'])}%)"

BG, PANEL, EDGE = "#05060f", "#0b0d1a", "#1e1b4b"
VIOLET, CYAN, PINK, LIME, AMBER, TEAL = "#8b5cf6", "#22d3ee", "#f472b6", "#a3e635", "#fbbf24", "#2dd4bf"
TEXT, MUTED, DIM = "#e2e8f0", "#94a3b8", "#475569"
SANS = "'Segoe UI', 'SF Pro Display', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', 'SF Mono', Consolas, Menlo, monospace"


def save(name, body):
    path = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body.strip() + "\n")


def svg(w, h, inner, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>{inner}</svg>')


def _starfield(rnd, w, h, n, sizes, cls):
    """A tile of stars `w` wide, drawn twice side by side so it can scroll forever."""
    tile = "".join(
        f'<circle cx="{rnd.uniform(0, w):.1f}" cy="{rnd.uniform(0, h):.1f}" r="{rnd.choice(sizes)}" '
        f'fill="{rnd.choice(["#fff", "#fff", "#fff", "#c7d2fe", "#a5f3fc", "#fbcfe8"])}" '
        f'class="tw" style="animation-delay:{rnd.uniform(0, 5):.2f}s;animation-duration:{rnd.uniform(2.5, 6):.1f}s"/>'
        for _ in range(n))
    return f'<g class="{cls}"><g>{tile}</g><g transform="translate({w} 0)">{tile}</g></g>'


def hero_day():
    """Days since epoch (UTC). HERO_DAY=<int> overrides it to preview another day."""
    if os.environ.get("HERO_DAY"):
        return int(os.environ["HERO_DAY"])
    return datetime.datetime.now(datetime.timezone.utc).date().toordinal()


# ── Celestial objects for the right side of the hero. Each returns SVG drawn around (x, y).
def _obj_giant(x, y, p):
    r = 165
    return f"""
<defs>
  <radialGradient id="pg" cx=".32" cy=".28" r=".8"><stop offset="0" stop-color="{p['c3']}"/><stop offset=".35" stop-color="{p['c1']}"/><stop offset=".7" stop-color="#1e1048"/><stop offset="1" stop-color="#05040f"/></radialGradient>
  <pattern id="bands" width="{r * 2}" height="34" patternUnits="userSpaceOnUse" patternTransform="rotate(-14)">
    <rect y="4" width="{r * 2}" height="7" fill="#fff" opacity=".1"/><rect y="17" width="{r * 2}" height="3" fill="{p['c2']}" opacity=".12"/>
    <rect y="25" width="{r * 2}" height="5" fill="{p['c3']}" opacity=".1"/>
    <animateTransform attributeName="patternTransform" type="translate" additive="sum" from="0 0" to="{r * 2} 0" dur="60s" repeatCount="indefinite"/></pattern>
  <radialGradient id="atmo" r=".5"><stop offset=".86" stop-color="{p['c2']}" stop-opacity="0"/><stop offset=".93" stop-color="{p['c2']}" stop-opacity=".55"/><stop offset="1" stop-color="{p['c1']}" stop-opacity="0"/></radialGradient>
  <linearGradient id="ring" x1="0" x2="1"><stop offset="0" stop-color="{p['c2']}" stop-opacity="0"/><stop offset=".3" stop-color="{p['c2']}" stop-opacity=".7"/><stop offset=".6" stop-color="#fff" stop-opacity=".8"/><stop offset="1" stop-color="{p['c3']}" stop-opacity=".1"/></linearGradient>
  <radialGradient id="moon" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#e2e8f0"/><stop offset=".6" stop-color="#64748b"/><stop offset="1" stop-color="#0f172a"/></radialGradient>
  <clipPath id="pclip"><circle cx="{x}" cy="{y}" r="{r}"/></clipPath>
</defs>
<style>.orbit{{animation:or 26s linear infinite;transform-origin:{x}px {y - 60}px}} @keyframes or{{to{{transform:rotate(360deg)}}}}</style>
<circle cx="{x}" cy="{y}" r="{r + 26}" fill="url(#atmo)"/>
<ellipse cx="{x}" cy="{y}" rx="{r + 150}" ry="40" fill="none" stroke="url(#ring)" stroke-width="10" opacity=".5" transform="rotate(12 {x} {y})"/>
<circle cx="{x}" cy="{y}" r="{r}" fill="url(#pg)"/>
<rect x="{x - r}" y="{y - r}" width="{r * 2}" height="{r * 2}" fill="url(#bands)" clip-path="url(#pclip)"/>
<path d="M{x - r - 150} {y} A{r + 150} 40 0 0 0 {x + r + 150} {y}" fill="none" stroke="url(#ring)" stroke-width="10" opacity=".9" transform="rotate(12 {x} {y})"/>
<g class="orbit"><circle cx="{x - r - 70}" cy="{y - 60}" r="13" fill="url(#moon)"/></g>"""


def _obj_blackhole(x, y, p):
    y -= 150
    return f"""
<defs>
  <linearGradient id="disk" x1="0" x2="1" spreadMethod="reflect"><stop offset="0" stop-color="#fff7ed"/><stop offset=".3" stop-color="{AMBER}"/><stop offset=".6" stop-color="#ea580c"/><stop offset="1" stop-color="{p['c3']}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0" dur="3s" repeatCount="indefinite"/></linearGradient>
  <radialGradient id="halo" r=".5"><stop offset=".3" stop-color="#000"/><stop offset=".42" stop-color="#fdba74" stop-opacity=".9"/><stop offset=".55" stop-color="{AMBER}" stop-opacity=".25"/><stop offset="1" stop-color="{p['c3']}" stop-opacity="0"/></radialGradient>
  <filter id="bh" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<style>.lens{{animation:ln 4s ease-in-out infinite;transform-origin:{x}px {y}px}} @keyframes ln{{50%{{transform:scale(1.06)}}}}</style>
<circle class="lens" cx="{x}" cy="{y}" r="150" fill="url(#halo)"/>
<path d="M{x - 190} {y} A190 34 0 0 1 {x + 190} {y}" fill="none" stroke="url(#disk)" stroke-width="16" filter="url(#bh)" opacity=".8"/>
<ellipse cx="{x}" cy="{y - 4}" rx="62" ry="66" fill="none" stroke="url(#disk)" stroke-width="7" filter="url(#bh)"/>
<circle cx="{x}" cy="{y}" r="56" fill="#000"/>
<path d="M{x - 210} {y} A210 40 0 0 0 {x + 210} {y}" fill="none" stroke="url(#disk)" stroke-width="20" filter="url(#bh)"/>
<path d="M{x - 210} {y} A210 40 0 0 0 {x + 210} {y}" fill="none" stroke="#fff" stroke-width="2" opacity=".6"/>"""


def _obj_eclipse(x, y, p):
    y -= 150
    rays = "".join(f'<path d="M{x} {y}L{x - 8} {y - 190}L{x + 8} {y - 190}Z" fill="#fff" opacity=".07" transform="rotate({a} {x} {y})"/>'
                   for a in range(0, 360, 24))
    return f"""
<defs>
  <radialGradient id="cor" r=".5"><stop offset=".38" stop-color="#fff"/><stop offset=".44" stop-color="{p['c2']}" stop-opacity=".8"/><stop offset=".7" stop-color="{p['c1']}" stop-opacity=".25"/><stop offset="1" stop-color="{p['c1']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="dia" r=".5"><stop offset="0" stop-color="#fff"/><stop offset=".2" stop-color="#fff" stop-opacity=".8"/><stop offset="1" stop-color="{p['c2']}" stop-opacity="0"/></radialGradient>
</defs>
<style>.rays{{animation:rr 80s linear infinite;transform-origin:{x}px {y}px}} @keyframes rr{{to{{transform:rotate(360deg)}}}}
  .cor{{animation:cp 5s ease-in-out infinite;transform-origin:{x}px {y}px}} @keyframes cp{{50%{{transform:scale(1.08);opacity:.85}}}}
  .dia{{animation:dd 5s ease-in-out infinite}} @keyframes dd{{0%,100%{{opacity:.4}}50%{{opacity:1}}}}</style>
<g class="rays">{rays}</g>
<circle class="cor" cx="{x}" cy="{y}" r="180" fill="url(#cor)"/>
<circle cx="{x}" cy="{y}" r="68" fill="#020208"/>
<circle class="dia" cx="{x - 50}" cy="{y - 46}" r="30" fill="url(#dia)"/>"""


def _obj_ice(x, y, p):
    r = 150
    y -= 40
    craters = "".join(f'<ellipse cx="{x + dx}" cy="{y + dy}" rx="{rr}" ry="{rr * .7:.0f}" fill="#0e7490" opacity=".25"/>'
                      for dx, dy, rr in [(-60, -40, 22), (30, 20, 30), (-20, 80, 16), (70, -70, 12), (-95, 40, 14)])
    return f"""
<defs>
  <radialGradient id="ice" cx=".3" cy=".28" r=".85"><stop offset="0" stop-color="#f0fdff"/><stop offset=".35" stop-color="#67e8f9"/><stop offset=".75" stop-color="#0e7490"/><stop offset="1" stop-color="#03111a"/></radialGradient>
  <radialGradient id="iatmo" r=".5"><stop offset=".84" stop-color="#a5f3fc" stop-opacity="0"/><stop offset=".92" stop-color="#a5f3fc" stop-opacity=".6"/><stop offset="1" stop-color="{p['c1']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="shade" cx=".25" cy=".2" r="1"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".85"/></radialGradient>
  <radialGradient id="m2" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#fde68a"/><stop offset="1" stop-color="#78350f"/></radialGradient>
</defs>
<style>.o1{{animation:o1 18s linear infinite;transform-origin:{x}px {y}px}} .o2{{animation:o1 30s linear infinite reverse;transform-origin:{x}px {y}px}}
  @keyframes o1{{to{{transform:rotate(360deg)}}}}</style>
<circle cx="{x}" cy="{y}" r="{r + 24}" fill="url(#iatmo)"/>
<circle cx="{x}" cy="{y}" r="{r}" fill="url(#ice)"/>{craters}
<circle cx="{x}" cy="{y}" r="{r}" fill="url(#shade)"/>
<g class="o1"><circle cx="{x - r - 40}" cy="{y}" r="9" fill="#e2e8f0"/></g>
<g class="o2"><circle cx="{x}" cy="{y - r - 60}" r="14" fill="url(#m2)"/></g>"""


def _obj_galaxy(x, y, p):
    rnd = random.Random(99)
    y -= 150
    import math
    dots = []
    for arm in range(3):
        for i in range(70):
            t = i / 70
            ang = arm * 2.094 + t * 4.2
            rad = 14 + t * 250
            px = x + math.cos(ang) * rad + rnd.gauss(0, 7)
            py = y + math.sin(ang) * rad + rnd.gauss(0, 7)
            col = rnd.choice(["#fff", p['c2'], p['c3'], "#c7d2fe"])
            dots.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="{rnd.uniform(.6, 2.2) * (1.2 - t * .6):.1f}" fill="{col}" opacity="{1 - t * .6:.2f}"/>')
    return f"""
<defs>
  <radialGradient id="core" r=".5"><stop offset="0" stop-color="#fff"/><stop offset=".25" stop-color="#fde68a" stop-opacity=".8"/><stop offset="1" stop-color="{p['c1']}" stop-opacity="0"/></radialGradient>
  <filter id="gb" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>
</defs>
<style>.gal{{animation:gr 120s linear infinite;transform-origin:{x}px {y}px}} @keyframes gr{{to{{transform:rotate(-360deg)}}}}</style>
<g transform="rotate(-18 {x} {y})">
  <ellipse cx="{x}" cy="{y}" rx="260" ry="110" fill="{p['c1']}" opacity=".35" filter="url(#gb)"/>
  <g transform="translate({x} {y}) scale(1 .42) translate({-x} {-y})"><g class="gal">
    {''.join(dots)}</g></g>
  <ellipse cx="{x}" cy="{y}" rx="80" ry="44" fill="url(#core)"/>
</g>"""


def _obj_binary(x, y, p):
    y -= 150
    return f"""
<defs>
  <radialGradient id="sA" r=".5"><stop offset="0" stop-color="#fff"/><stop offset=".25" stop-color="#93c5fd"/><stop offset=".6" stop-color="{p['c2']}" stop-opacity=".4"/><stop offset="1" stop-color="{p['c2']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="sB" r=".5"><stop offset="0" stop-color="#fff"/><stop offset=".25" stop-color="#fdba74"/><stop offset=".6" stop-color="#f97316" stop-opacity=".4"/><stop offset="1" stop-color="#f97316" stop-opacity="0"/></radialGradient>
</defs>
<style>.bin{{animation:bn 14s linear infinite;transform-origin:{x}px {y}px}} @keyframes bn{{to{{transform:rotate(360deg)}}}}
  .unbin{{animation:bn 14s linear infinite reverse}}
  .fl1{{animation:fl 2.6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}} @keyframes fl{{50%{{transform:scale(1.12)}}}}</style>
<ellipse cx="{x}" cy="{y}" rx="110" ry="110" fill="none" stroke="#fff" stroke-opacity=".08" stroke-dasharray="3 7"/>
<g class="bin">
  <circle class="fl1" cx="{x - 80}" cy="{y}" r="95" fill="url(#sA)"/>
  <circle class="fl1" cx="{x + 80}" cy="{y}" r="70" fill="url(#sB)" style="animation-delay:1.3s"/>
</g>"""


def _obj_mars(x, y, p):
    r = 160
    y -= 20
    return f"""
<defs>
  <radialGradient id="mars" cx=".3" cy=".28" r=".85"><stop offset="0" stop-color="#fed7aa"/><stop offset=".35" stop-color="#ea580c"/><stop offset=".75" stop-color="#7c2d12"/><stop offset="1" stop-color="#1c0a04"/></radialGradient>
  <radialGradient id="matmo" r=".5"><stop offset=".86" stop-color="#fb923c" stop-opacity="0"/><stop offset=".93" stop-color="#fb923c" stop-opacity=".5"/><stop offset="1" stop-color="#fb923c" stop-opacity="0"/></radialGradient>
  <filter id="dunes" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".02 .05" numOctaves="3" seed="4"/>
    <feColorMatrix type="matrix" values="0 0 0 0 .3  0 0 0 0 .08  0 0 0 0 .02  0 0 0 1.4 -.55"/></filter>
  <clipPath id="mclip"><circle cx="{x}" cy="{y}" r="{r}"/></clipPath>
  <radialGradient id="mshade" cx=".25" cy=".2" r="1"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".85"/></radialGradient>
</defs>
<style>.ph{{animation:ph 11s linear infinite;transform-origin:{x}px {y}px}} @keyframes ph{{to{{transform:rotate(360deg)}}}}</style>
<circle cx="{x}" cy="{y}" r="{r + 22}" fill="url(#matmo)"/>
<circle cx="{x}" cy="{y}" r="{r}" fill="url(#mars)"/>
<rect x="{x - r}" y="{y - r}" width="{r * 2}" height="{r * 2}" filter="url(#dunes)" clip-path="url(#mclip)" opacity=".8"/>
<ellipse cx="{x - 30}" cy="{y - r + 18}" rx="40" ry="10" fill="#fff" opacity=".7" clip-path="url(#mclip)"/>
<circle cx="{x}" cy="{y}" r="{r}" fill="url(#mshade)"/>
<g class="ph"><circle cx="{x - r - 50}" cy="{y}" r="7" fill="#a8a29e"/></g>"""


# name, sector label, nebula colours (c1, c2, c3), space tint, object
HERO_THEMES = [
    ("Ringed Giant", "SATURN DRIFT", ("#8b5cf6", "#22d3ee", "#f472b6"), "#120a2e", _obj_giant),
    ("Event Horizon", "SAGITTARIUS A*", ("#7c3aed", "#f97316", "#f43f5e"), "#170a12", _obj_blackhole),
    ("Total Eclipse", "UMBRA PASSAGE", ("#6366f1", "#e0e7ff", "#a78bfa"), "#0a0b24", _obj_eclipse),
    ("Frozen World", "EUROPA ORBIT", ("#0ea5e9", "#2dd4bf", "#a5f3fc"), "#041726", _obj_ice),
    ("Spiral Galaxy", "ANDROMEDA M31", ("#a855f7", "#38bdf8", "#f9a8d4"), "#100a26", _obj_galaxy),
    ("Binary Suns", "TATOOINE SYSTEM", ("#2563eb", "#22d3ee", "#fb923c"), "#07112a", _obj_binary),
    ("Red Planet", "MARS APPROACH", ("#dc2626", "#fb923c", "#f472b6"), "#1a0806", _obj_mars),
]


# ─────────────────────────────── HERO ───────────────────────────────
def hero():
    """A new space scene every day: the theme cycles weekly, the sky is seeded by the date."""
    day = hero_day()
    tname, sector, (c1, c2, c3), tint, obj = HERO_THEMES[day % len(HERO_THEMES)]
    pal = {"c1": c1, "c2": c2, "c3": c3}
    rnd = random.Random(day)
    W, H = 1200, 460
    far = _starfield(rnd, W, H, 140, [0.5, 0.6, 0.8], "drift-far")
    mid = _starfield(rnd, W, H, 60, [0.9, 1.1, 1.3], "drift-mid")
    near = _starfield(rnd, W, H, 18, [1.6, 2.0], "drift-near")
    tilt = rnd.uniform(.2, .6) * rnd.choice([-1, 1])
    band = "".join(
        f'<circle cx="{(t := rnd.uniform(-100, W + 100)):.0f}" cy="{H * (.95 if tilt > 0 else .05) - t * tilt + rnd.gauss(0, 34):.0f}" '
        f'r="{rnd.choice([0.4, 0.5, 0.7])}" fill="#fff" opacity="{rnd.uniform(.15, .55):.2f}"/>' for _ in range(260))
    spikes = "".join(
        f'<g transform="translate({rnd.randint(30, 820)} {rnd.randint(30, H - 90)})" class="sp" style="animation-delay:{rnd.uniform(0, 3):.1f}s">'
        f'<circle r="2.2" fill="#fff"/><path d="M-{(s := rnd.randint(8, 15))} 0H{s}M0 -{s}V{s}" stroke="{c}" stroke-width=".9" stroke-linecap="round"/>'
        f'<circle r="7" fill="{c}" opacity=".25"/></g>'
        for c in (c2, c3, "#fff", c1, "#c7d2fe"))
    shooting = "".join(
        f'<g class="meteor" style="animation-delay:{d:.1f}s;--x:{rnd.randint(150, 1100)}px;--y:{rnd.randint(0, 140)}px">'
        f'<line x1="0" y1="0" x2="-150" y2="-62" stroke="url(#trail)" stroke-width="2" stroke-linecap="round"/>'
        f'<circle r="1.8" fill="#fff"/></g>'
        for d in (0, 3.4, 6.9, 9.1))
    roles = [
        "AI / ML Engineer · High-Performance Systems",
        "Full-Stack Builder · FastAPI · React · Cloud",
        f"Level {S['level']} {S['rank_title']} · {S['total']} Solved · {S['streak']}d Streak 🔥",
        "I ship products, not notebooks"
    ]
    role_txt = "".join(f'<text x="600" y="262" class="role" style="animation-delay:{i * 3.2:.1f}s">{escape(r)}</text>'
                       for i, r in enumerate(roles))
    date_txt = datetime.date.fromordinal(day).strftime("%d %b %Y").upper()
    inner = f"""
<defs>
  <linearGradient id="name" x1="0" x2="1" y1="0" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="{c2}"/>
    <stop offset=".65" stop-color="{c3}"/><stop offset="1" stop-color="#fff"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0;0 0" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <radialGradient id="space" cx="{rnd.uniform(.2, .5):.2f}" cy=".3" r="1"><stop offset="0" stop-color="{tint}"/><stop offset=".55" stop-color="#070818"/><stop offset="1" stop-color="#02030a"/></radialGradient>
  <linearGradient id="trail" x1="1" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="{c2}" stop-opacity="0"/></linearGradient>
  <filter id="nebula" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="{rnd.uniform(.0025, .0045):.4f} {rnd.uniform(.004, .007):.4f}" numOctaves="5" seed="{day % 997}" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 2.6 -1.15" result="a"/>
    <feComposite in="SourceGraphic" in2="a" operator="in"/>
  </filter>
  <filter id="dust" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency=".012" numOctaves="4" seed="{(day * 7) % 991}" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 3 -1.7" result="a"/>
    <feComposite in="SourceGraphic" in2="a" operator="in"/>
  </filter>
  <linearGradient id="nebcol" x1="0" y1="0" x2="1" y2="{rnd.uniform(.3, .9):.2f}">
    <stop offset="0" stop-color="{c1}"/><stop offset=".4" stop-color="{c2}"/><stop offset=".75" stop-color="{c3}"/><stop offset="1" stop-color="{c1}"/>
  </linearGradient>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="7" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="26"/></clipPath>
</defs>
<style>
  .tw{{animation:tw 4s ease-in-out infinite}}
  @keyframes tw{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}
  .drift-far{{animation:dr 240s linear infinite}} .drift-mid{{animation:dr 120s linear infinite}} .drift-near{{animation:dr 60s linear infinite}}
  @keyframes dr{{to{{transform:translateX(-{W}px)}}}}
  .neb{{animation:nb 30s ease-in-out infinite alternate}}
  @keyframes nb{{from{{transform:translate(0,0) scale(1)}}to{{transform:translate(-40px,12px) scale(1.04)}}}}
  .sp{{animation:sp 5s ease-in-out infinite}} @keyframes sp{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
  .meteor{{opacity:0;animation:mt 12s linear infinite}}
  @keyframes mt{{0%{{opacity:0;transform:translate(var(--x),var(--y))}}1%{{opacity:1}}7%{{opacity:0;transform:translate(calc(var(--x) + 360px),calc(var(--y) + 150px))}}100%{{opacity:0;transform:translate(calc(var(--x) + 360px),calc(var(--y) + 150px))}}}}
  .sat{{animation:sat 38s linear infinite}}
  @keyframes sat{{0%{{transform:translate(-80px,150px) rotate(8deg)}}100%{{transform:translate(1300px,40px) rotate(8deg)}}}}
  .blink{{animation:bl 1.4s steps(1) infinite}} @keyframes bl{{50%{{opacity:.1}}}}
  .name{{font:800 104px {SANS};letter-spacing:14px;text-anchor:middle}}
  .g1{{fill:{c2};opacity:0;animation:g1 5s steps(1) infinite}} .g2{{fill:{c3};opacity:0;animation:g2 5s steps(1) infinite}}
  @keyframes g1{{0%,90%{{opacity:0;transform:none}}91%{{opacity:.7;transform:translate(-6px,2px)}}93%{{opacity:.7;transform:translate(4px,-2px)}}95%,100%{{opacity:0;transform:none}}}}
  @keyframes g2{{0%,90%{{opacity:0;transform:none}}91%{{opacity:.7;transform:translate(6px,-1px)}}93%{{opacity:.7;transform:translate(-5px,2px)}}95%,100%{{opacity:0;transform:none}}}}
  .role{{font:500 23px {MONO};fill:{c2};text-anchor:middle;opacity:0;animation:role 12.8s infinite}}
  @keyframes role{{0%{{opacity:0;transform:translateY(14px)}}3%,22%{{opacity:1;transform:none}}25%,100%{{opacity:0;transform:translateY(-14px)}}}}
  .chip{{font:600 13px {MONO};fill:{MUTED}}}
  .hud{{font:500 11px {MONO};fill:#64748b;letter-spacing:1.5px}} .hudb{{font:700 11px {MONO};fill:{c2};letter-spacing:1.5px}}
  .dot{{animation:pulse 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}}
  @keyframes pulse{{0%{{transform:scale(1);opacity:.9}}100%{{transform:scale(3.2);opacity:0}}}}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#space)"/>
  <g class="neb">
    <rect x="-60" y="-40" width="{W + 120}" height="{H + 80}" fill="url(#nebcol)" filter="url(#nebula)" opacity=".85"/>
    <rect x="-60" y="-40" width="{W + 120}" height="{H + 80}" fill="#0b0a20" filter="url(#dust)" opacity=".7"/>
  </g>
  <g filter="url(#soft)" opacity=".45">
    <ellipse cx="{rnd.randint(200, 500)}" cy="{rnd.randint(80, 200)}" rx="220" ry="90" fill="{c1}"/>
    <ellipse cx="{rnd.randint(600, 900)}" cy="{rnd.randint(60, 180)}" rx="200" ry="70" fill="{c2}" opacity=".6"/>
  </g>
  <g>{band}</g>
  {far}{mid}
  {spikes}
  {shooting}
  <g class="sat"><g transform="scale(.9)">
    <rect x="-16" y="-3" width="12" height="6" fill="#334155" stroke="{c2}" stroke-width=".6"/>
    <rect x="4" y="-3" width="12" height="6" fill="#334155" stroke="{c2}" stroke-width=".6"/>
    <rect x="-4" y="-4" width="8" height="8" rx="1.5" fill="#cbd5e1"/>
    <circle cx="0" cy="-6" r="1.3" fill="{c3}" class="blink"/></g></g>
  {obj(1075, 415, pal)}
  {near}
  <g transform="translate(40 36)">
    <rect width="232" height="32" rx="16" fill="{PANEL}" fill-opacity=".7" stroke="{EDGE}"/>
    <circle cx="20" cy="16" r="5" fill="{LIME}"/><circle class="dot" cx="20" cy="16" r="5" fill="{LIME}"/>
    <text x="34" y="21" class="chip">currently shipping</text>
  </g>
  <g transform="translate({W - 240} 36)">
    <rect width="200" height="32" rx="16" fill="{PANEL}" fill-opacity=".7" stroke="{EDGE}"/>
    <text x="100" y="21" class="chip" text-anchor="middle">🔥 {S['streak']}d streak · Level {S['level']}</text>
  </g>
  <text x="40" y="{H - 70}" class="hudb">◉ TODAY'S SKY · {escape(tname.upper())}</text>
  <text x="40" y="{H - 52}" class="hud">SECTOR · {escape(sector)}</text>
  <text x="40" y="{H - 34}" class="hud">STARDATE {date_txt} · NEW SKY EVERY DAY</text>
  <path d="M40 {H - 24}h190" stroke="{EDGE}"/><path d="M40 {H - 24}h60" stroke="{c2}" class="blink"/>
  <text x="600" y="200" class="name g1">YOGENDER</text>
  <text x="600" y="200" class="name g2">YOGENDER</text>
  <text x="600" y="200" class="name" fill="url(#name)" filter="url(#glow)">YOGENDER</text>
  {role_txt}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="26" fill="none" stroke="{EDGE}"/>
"""
    save("hero.svg", svg(W, H, inner, f"Yogender — AI/ML Engineer · Full-Stack Builder · today's sky: {tname}"))
    # Point the README at a per-day URL so GitHub's image cache can't serve yesterday's sky.
    readme = os.path.join(OUT, "..", "README.md")
    try:
        with open(readme, encoding="utf-8") as fh:
            text = fh.read()
        new = re.sub(r'src="\./assets/hero\.svg(\?d=\d+)?"', f'src="./assets/hero.svg?d={day}"', text)
        if new != text:
            with open(readme, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new)
    except FileNotFoundError:
        pass


# ───────────────────────────── TERMINAL ─────────────────────────────
def terminal():
    W, H, T = 1200, 390, 20.0
    CW = 9.3
    session = [
        ("whoami", [("yogender", PINK), ("  ·  AI/ML engineer & systems builder  ·  India", MUTED)]),
        ("cat stack.txt", [("python  c++  sql  ", AMBER), ("fastapi  react  pytorch  ", CYAN), ("postgres  redis  docker  kafka", VIOLET)]),
        ("ls ~/projects --shipped", [("DSA-Journey/  NewsIntel/  CloudCommand/  ParticleGravity/  KNN-Demo/  FinanceInsight/", TEAL)]),
        ("./dsa --stats", [(f"{S['total']} solved", LIME), ("  ·  ", DIM), (f"{S['easy']} easy", TEAL), ("  ·  ", DIM), (f"{S['medium']} med", AMBER), ("  ·  ", DIM), (f"{S['hard']} hard", PINK), (f"  ·  {S['streak']}-day streak 🔥  ·  top {round(S['top_pct'])}% contest", VIOLET)]),
        ("echo $MOTTO", [('"Consistency over intensity. Solve, build, ship every day."', PINK)]),
    ]
    y0, step, x0 = 92, 54, 40
    rows, t = [], 0.6
    end = T - 2.0
    for i, (cmd, out) in enumerate(session):
        y = y0 + i * step
        type_dur = 0.05 * len(cmd) + 0.25
        a, b, c = t / T, (t + type_dur) / T, (t + type_dur + 0.35) / T
        e = end / T
        w = (len(cmd) + 3) * CW + 12
        rows.append(f"""
  <clipPath id="c{i}"><rect x="{x0}" y="{y - 20}" height="28" width="0">
    <animate attributeName="width" values="0;0;{w:.0f};{w:.0f};0" keyTimes="0;{a:.3f};{b:.3f};{e:.3f};1" dur="{T}s" repeatCount="indefinite"/></rect></clipPath>
  <text x="{x0}" y="{y}" clip-path="url(#c{i})" class="m"><tspan fill="{PINK}">❯</tspan> <tspan fill="{TEXT}">{escape(cmd)}</tspan></text>
  <text x="{x0 + 22}" y="{y + 24}" class="m o" opacity="0">{''.join(f'<tspan fill="{col}">{escape(s)}</tspan>' for s, col in out)}
    <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{c:.3f};{min(c + .02, e - .01):.3f};{e:.3f};1" dur="{T}s" repeatCount="indefinite"/></text>""")
        t += type_dur + 0.9
    cy = y0 + len(session) * step
    a = t / T
    rows.append(f"""
  <g opacity="0"><text x="{x0}" y="{cy}" class="m" fill="{PINK}">❯</text>
    <rect x="{x0 + 20}" y="{cy - 15}" width="10" height="19" fill="{CYAN}" class="cur"/>
    <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{a:.3f};{a + .01:.3f};{end / T:.3f};1" dur="{T}s" repeatCount="indefinite"/></g>""")
    inner = f"""
<style>
  .m{{font:500 15px {MONO};white-space:pre}} .o{{font-size:14px}}
  .cur{{animation:blink 1s steps(1) infinite}} @keyframes blink{{50%{{opacity:0}}}}
</style>
<defs><linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".35"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".15"/></linearGradient></defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="{PANEL}" stroke="{EDGE}"/>
<path d="M.5 18.5a18 18 0 0 1 18-18h{W - 37}a18 18 0 0 1 18 18V44H.5z" fill="url(#bar)"/>
<circle cx="28" cy="22" r="7" fill="#ff5f57"/><circle cx="52" cy="22" r="7" fill="#febc2e"/><circle cx="76" cy="22" r="7" fill="#28c840"/>
<text x="600" y="27" text-anchor="middle" style="font:500 13px {MONO}" fill="{MUTED}">yogender@mission-control: ~ — zsh  ·  uplink stable</text>
{''.join(rows)}
"""
    save("terminal.svg", svg(W, H, inner, "Terminal: whoami, stack, projects, DSA stats"))


# ───────────────────────────── MARQUEE ──────────────────────────────
TECH_ROWS = [
    [("Python", "#4B8BBE"), ("C++", "#659AD2"), ("TypeScript", "#3178C6"), ("JavaScript", "#F7DF1E"), ("SQL", "#4479A1"),
     ("Bash", "#4EAA25"), ("HTML5", "#E34F26"), ("CSS3", "#1572B6")],
    [("PyTorch", "#EE4C2C"), ("TensorFlow", "#FF6F00"), ("scikit-learn", "#F7931E"), ("OpenCV", "#5C3EE8"),
     ("FastAPI", "#009688"), ("React", "#61DAFB"), ("Node.js", "#339933"), ("Express", "#FFFFFF"), ("Next.js", "#FFFFFF")],
    [("PostgreSQL", "#4169E1"), ("MySQL", "#4479A1"), ("Redis", "#DC382D"), ("Docker", "#2496ED"),
     ("Kubernetes", "#326CE5"), ("Kafka", "#231F20"), ("Prometheus", "#E6522C"), ("Grafana", "#F46800"),
     ("Git", "#F05032"), ("Linux", "#FCC624")]
]


def marquee():
    W, H = 1200, 190
    srnd = random.Random(9)
    mstars = "".join(
        f'<circle cx="{srnd.uniform(4, W - 4):.0f}" cy="{srnd.uniform(4, H - 4):.0f}" r="{srnd.choice([.5, .7, 1])}" fill="#fff" '
        f'class="tw" style="animation-delay:{srnd.uniform(0, 4):.1f}s"/>' for _ in range(70))
    row_h, gap = 44, 12
    durations = [32, 38, 30]
    rows = []
    for r_idx, (techs, dur) in enumerate(zip(TECH_ROWS, durations)):
        rev = r_idx == 1
        y = 16 + r_idx * (row_h + gap)
        items = []
        x = 0
        for name, col in techs:
            w = len(name) * 9 + 48
            items.append((name, col, w, x))
            x += w + gap
        row_w = x
        copies = 4
        all_chips = []
        for c in range(copies):
            shift = c * row_w
            for name, col, w, ix in items:
                all_chips.append(
                    f'<g transform="translate({ix + shift} 0)"><rect width="{w}" height="{row_h}" rx="{row_h / 2}" fill="{PANEL}" stroke="{EDGE}"/>'
                    f'<circle cx="20" cy="{row_h / 2}" r="5" fill="{col}"/><text x="34" y="{row_h / 2 + 5}" class="t">{escape(name)}</text></g>')
        anim = f"""<animateTransform attributeName="transform" type="translate" from="{'0' if not rev else f'-{row_w}'} {y}" to="{f'-{row_w}' if not rev else '0'} {y}" dur="{dur}s" repeatCount="indefinite"/>"""
        rows.append(f'<g><g>{anim}{"".join(all_chips)}</g></g>')
    inner = f"""
<defs>
  <radialGradient id="mbg" cx=".5" cy=".5" r=".8"><stop offset="0" stop-color="#110a2b"/><stop offset="1" stop-color="{BG}"/></radialGradient>
  <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/><stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<style>
  .t{{font:600 14px {MONO};fill:{TEXT}}}
  .tw{{animation:tw 3.5s ease-in-out infinite}} @keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.85}}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="url(#mbg)" stroke="{EDGE}"/>
{mstars}
<g mask="url(#fade)">{''.join(rows)}</g>
"""
    save("marquee.svg", svg(W, H, inner, "Tech stack"))


# ─────────────────────────── PROJECT CARDS ──────────────────────────
CARDS = [
    ("dsa-journey", "⚔️", "DSA · LeetCode Journey", "ALGORITHMS · RPG", [
        f"{S['total']} problems, {S['streak']}-day streak, Level {S['level']}",
        "Grandmaster. Organised chronologically",
        "by date & algorithmic pattern."
    ], ["C++", "Python", "SQL", "DSA"], True, (VIOLET, CYAN)),

    ("newsintel", "🛰️", "NewsIntel", "AI · DATA", [
        "Turns noisy live news into ranked,",
        "deduplicated, AI-enriched intelligence",
        "cards with source tracing."
    ], ["React", "FastAPI", "AI"], False, (VIOLET, CYAN)),

    ("cloud-command", "⚡", "Cloud Command", "DEVOPS", [
        "Mission control for your stack: uptime,",
        "encrypted API vault, Render + Vercel",
        "deploys and scheduled jobs."
    ], ["React", "FastAPI", "Docker"], True, (CYAN, LIME)),

    ("particle-gravity", "🌌", "Particle Gravity 3D", "CREATIVE · GAME", [
        "Interactive 3D particle-gravity sandbox",
        "running real-time physics and WebGL",
        "effects right in the browser."
    ], ["WebGL", "Three.js", "WASM"], True, (AMBER, PINK)),

    ("knn-cat-dog", "🐱", "KNN Cat vs Dog", "AI · CV", [
        "K-Nearest-Neighbours image classifier from",
        "scratch using custom Euclidean distance",
        "& feature maps in Python & OpenCV."
    ], ["Python", "OpenCV", "NumPy"], False, (PINK, VIOLET)),

    ("financeinsight", "📈", "FinanceInsight", "FINTECH · NLP", [
        "End-to-end annual report & 10-K reader:",
        "extracts financial statements, risk factors,",
        "and revenue tables using NLP."
    ], ["Python", "NLP", "Docker"], False, (TEAL, VIOLET)),
]


def cards():
    W, H = 580, 230
    for slug, icon, title, cat, desc, tags, live, (c1, c2) in CARDS:
        chips, x = [], 28
        for t in tags:
            w = len(t) * 7.6 + 24
            chips.append(f'<g transform="translate({x:.0f} 178)"><rect width="{w:.0f}" height="26" rx="13" fill="{c1}" fill-opacity=".12" stroke="{c1}" stroke-opacity=".45"/>'
                         f'<text x="{w / 2:.0f}" y="17.5" text-anchor="middle" class="tag" fill="{c1}">{escape(t)}</text></g>')
            x += w + 8
        status = (f'<circle cx="{W - 90}" cy="191" r="5" fill="{LIME}"/><circle cx="{W - 90}" cy="191" r="5" fill="{LIME}" class="dot"/>'
                  f'<text x="{W - 78}" y="196" class="st" fill="{LIME}">live ↗</text>') if live else \
                 f'<text x="{W - 28}" y="196" text-anchor="end" class="st" fill="{MUTED}">source ↗</text>'
        lines = "".join(f'<text x="28" y="{108 + i * 22}" class="d">{escape(l)}</text>' for i, l in enumerate(desc))
        inner = f"""
<defs>
  <linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset=".5" stop-color="{EDGE}"/><stop offset="1" stop-color="{c2}"/>
    <animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" dur="6s" repeatCount="indefinite"/></linearGradient>
  <linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <radialGradient id="gl" cx="0" cy="0" r="1"><stop offset="0" stop-color="{c1}" stop-opacity=".28"/><stop offset="1" stop-color="{c1}" stop-opacity="0"/></radialGradient>
  <clipPath id="cl"><rect width="{W}" height="{H}" rx="20"/></clipPath>
</defs>
<style>
  .t{{font:700 24px {SANS};fill:{TEXT}}} .c{{font:700 11px {MONO};letter-spacing:2px}} .d{{font:400 15px {SANS};fill:{MUTED}}}
  .tag{{font:600 12px {MONO}}} .st{{font:700 13px {MONO}}}
  .dot{{animation:p 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}} @keyframes p{{to{{transform:scale(3);opacity:0}}}}
  .sw{{animation:sw 5s ease-in-out infinite}} @keyframes sw{{0%{{transform:translateX(-300px) skewX(-20deg)}}60%,100%{{transform:translateX({W + 200}px) skewX(-20deg)}}}}
  .ic{{animation:bob 4s ease-in-out infinite}} @keyframes bob{{50%{{transform:translateY(-4px)}}}}
</style>
<g clip-path="url(#cl)">
  <rect width="{W}" height="{H}" fill="{PANEL}"/>
  <circle cx="0" cy="0" r="260" fill="url(#gl)"/>
  <rect class="sw" x="0" y="0" width="160" height="{H}" fill="url(#sh)"/>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="19" fill="none" stroke="url(#bd)" stroke-width="2"/>
<g class="ic"><rect x="28" y="26" width="46" height="46" rx="12" fill="{c1}" fill-opacity=".14" stroke="{c1}" stroke-opacity=".4"/>
  <text x="51" y="58" text-anchor="middle" font-size="24">{icon}</text></g>
<text x="88" y="58" class="t">{escape(title)}</text>
<text x="{W - 28}" y="44" text-anchor="end" class="c" fill="{c2}">{escape(cat)}</text>
{lines}
{''.join(chips)}
{status}
"""
        save(f"cards/{slug}.svg", svg(W, H, inner, f"{title} — {' '.join(desc)}"))


# ─────────────────────────────── DSA ────────────────────────────────
def dsa():
    W, H = 1200, 320
    easy, med, hard = S["easy"], S["medium"], S["hard"]
    total = easy + med + hard
    R = 80
    C = 2 * 3.14159 * R
    topics = [
        ("Arrays & Hashing", 45), ("Two Pointers", 16), ("Trees & BST", 16),
        ("Graphs & Search", 14), ("Stack & Queue", 12), ("Binary Search", 10), ("SQL", 30)
    ]
    mx = max(n for _, n in topics)
    bars = []
    for i, (name, n) in enumerate(topics):
        y = 58 + i * 33
        w = 330 * n / mx + 6
        bars.append(f'<text x="380" y="{y + 13}" class="l">{escape(name)}</text>'
                    f'<rect x="540" y="{y}" width="336" height="16" rx="8" fill="{EDGE}" fill-opacity=".6"/>'
                    f'<rect x="540" y="{y}" width="{w:.0f}" height="16" rx="8" fill="url(#bg)" class="gr" style="animation-duration:{1.0 + i * 0.18:.2f}s"/>'
                    f'<text x="{540 + w + 10:.0f}" y="{y + 13}" class="n">{n}</text>')
    e_len = C * easy / total
    m_len = C * med / total
    h_len = C * hard / total

    inner = f"""
<defs><linearGradient id="bg" x1="0" x2="1"><stop offset="0" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient></defs>
<style>
  .l{{font:500 14px {SANS};fill:{MUTED}}} .n{{font:700 13px {MONO};fill:{TEXT}}}
  .gr{{transform-box:fill-box;transform-origin:left;animation:grow 1.4s cubic-bezier(.2,.8,.2,1)}} @keyframes grow{{from{{transform:scaleX(0)}}}}
  .big{{font:800 46px {SANS};fill:{TEXT}}} .sm{{font:600 12px {MONO};fill:{MUTED};letter-spacing:2px}}
  .h{{font:700 13px {MONO};letter-spacing:3px;fill:{VIOLET}}} .k{{font:600 14px {SANS};fill:{TEXT}}}
  .ring{{animation:spin 18s linear infinite;transform-origin:170px 160px}} @keyframes spin{{to{{transform:rotate(360deg)}}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="{PANEL}" stroke="{EDGE}"/>
<circle cx="170" cy="160" r="108" fill="none" stroke="{VIOLET}" stroke-opacity=".35" stroke-dasharray="2 10" class="ring"/>
<circle cx="170" cy="160" r="{R}" fill="none" stroke="{EDGE}" stroke-width="16"/>
<g transform="rotate(-90 170 160)">
  <circle cx="170" cy="160" r="{R}" fill="none" stroke="{TEAL}" stroke-width="16" stroke-linecap="round" stroke-dasharray="{e_len - 4:.1f} {C:.1f}"><animate attributeName="stroke-dashoffset" from="{e_len:.1f}" to="0" dur="1.6s" fill="freeze"/></circle>
  <circle cx="170" cy="160" r="{R}" fill="none" stroke="{AMBER}" stroke-width="16" stroke-linecap="round" stroke-dasharray="{m_len - 4:.1f} {C:.1f}"
    stroke-dashoffset="{-e_len:.1f}"><animate attributeName="stroke-dashoffset" from="{-e_len + m_len:.1f}" to="{-e_len:.1f}" dur="1.6s" begin=".4s" fill="freeze"/></circle>
  <circle cx="170" cy="160" r="{R}" fill="none" stroke="{PINK}" stroke-width="16" stroke-linecap="round" stroke-dasharray="{h_len - 4:.1f} {C:.1f}"
    stroke-dashoffset="{-e_len - m_len:.1f}"><animate attributeName="stroke-dashoffset" from="{-e_len - m_len + h_len:.1f}" to="{-e_len - m_len:.1f}" dur="1.6s" begin=".8s" fill="freeze"/></circle>
</g>
<text x="170" y="166" text-anchor="middle" class="big">{total}</text>
<text x="170" y="190" text-anchor="middle" class="sm">SOLVED</text>
<text x="380" y="36" class="h">// PATTERNS PRACTISED</text>
{''.join(bars)}
<g transform="translate(940 50)">
  <text class="h" y="-14">// DIFFICULTY</text>
  <circle cx="7" cy="14" r="6" fill="{TEAL}"/><text x="22" y="19" class="k">Easy <tspan fill="{MUTED}">· {easy}</tspan></text>
  <circle cx="7" cy="42" r="6" fill="{AMBER}"/><text x="22" y="47" class="k">Medium <tspan fill="{MUTED}">· {med}</tspan></text>
  <circle cx="7" cy="70" r="6" fill="{PINK}"/><text x="22" y="75" class="k">Hard <tspan fill="{MUTED}">· {hard}</tspan></text>
  <text class="h" y="116">// STREAK &amp; RATING</text>
  <text y="142" class="k" fill="{LIME}">🔥 {S['streak']}-Day Continuous</text>
  <text y="166" class="k" fill="{CYAN}">⚔️ {RATING_TXT}</text>
  <text y="210" class="st" style="font:700 13px {MONO}" fill="{VIOLET}">open the journey →</text>
</g>
"""
    save("dsa.svg", svg(W, H, inner, f"DSA journey: {total} LeetCode problems solved · {S['streak']}-day streak"))


# ─────────────────────────── SECTION TITLES ─────────────────────────
SECTIONS = [("about", "01", "about me"), ("projects", "02", "featured work"), ("stack", "03", "tech stack"),
            ("dsa", "04", "dsa journey"), ("stats", "05", "live github stats"), ("connect", "06", "let's connect")]


def sections():
    W, H = 1200, 84
    for idx, (slug, num, label) in enumerate(SECTIONS):
        rnd = random.Random(100 + idx)
        stars = "".join(
            f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(4, H - 4):.0f}" r="{rnd.choice([.5, .7, 1])}" fill="#fff" '
            f'class="tw" style="animation-delay:{rnd.uniform(0, 4):.1f}s"/>' for _ in range(46))
        tw = len(label) * 16.5 + len(num + " // ") * 10.5  # rough rendered width of the title
        px, pc = 600 + tw / 2 + 30, [VIOLET, CYAN, PINK][idx % 3]
        inner = f"""
<defs><linearGradient id="g" x1="0" x2="1" spreadMethod="reflect"><stop offset="0" stop-color="#c4b5fd"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0;0 0" dur="6s" repeatCount="indefinite"/></linearGradient>
  <linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
  <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".25" stop-color="#fff"/><stop offset=".75" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
  <radialGradient id="pl" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fff"/><stop offset=".4" stop-color="{pc}"/><stop offset="1" stop-color="#0b0d1a"/></radialGradient></defs>
<style>
  .n{{font:700 15px {MONO};fill:{DIM};letter-spacing:2px}} .t{{font:800 30px {SANS};letter-spacing:1px}}
  .s{{animation:s 3.5s ease-in-out infinite}} @keyframes s{{0%{{transform:translateX(-420px)}}100%{{transform:translateX({W}px)}}}}
  .tw{{animation:tw 3.5s ease-in-out infinite}} @keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
  .mo{{animation:mo 6s linear infinite;transform-origin:{px:.0f}px 34px}} @keyframes mo{{to{{transform:rotate(360deg)}}}}
</style>
<g mask="url(#m)">{stars}</g>
<text x="600" y="44" text-anchor="middle"><tspan class="n">{num} // </tspan><tspan class="t" fill="url(#g)">{escape(label)}</tspan></text>
<circle cx="{px:.0f}" cy="34" r="7" fill="url(#pl)"/>
<ellipse cx="{px:.0f}" cy="34" rx="13" ry="3.6" fill="none" stroke="{pc}" stroke-opacity=".8" transform="rotate(-20 {px:.0f} 34)"/>
<g class="mo"><circle cx="{px + 20:.0f}" cy="34" r="1.8" fill="#e2e8f0"/></g>
<rect x="300" y="66" width="600" height="1" fill="{EDGE}"/>
<rect class="s" x="0" y="65" width="400" height="3" rx="1.5" fill="url(#ln)"/>
"""
        save(f"sections/{slug}.svg", svg(W, H, inner, label))


# ───────────────────────────── LAUNCH ──────────────────────────────
def launch():
    """A rocket crossing at warp, used as a divider under the hero."""
    rnd = random.Random(42)
    W, H = 1200, 110
    streaks = "".join(
        f'<line x1="0" y1="{(y := rnd.uniform(6, H - 6)):.0f}" x2="{rnd.uniform(20, 90):.0f}" y2="{y:.0f}" stroke="{rnd.choice(["#fff", "#c4b5fd", CYAN, PINK])}" '
        f'stroke-width="{rnd.choice([.6, 1, 1.4])}" stroke-linecap="round" class="wp" '
        f'style="animation-duration:{rnd.uniform(1.2, 3.2):.1f}s;animation-delay:-{rnd.uniform(0, 3):.1f}s"/>'
        for _ in range(40))
    sparks = "".join(
        f'<circle r="{rnd.uniform(1, 2.6):.1f}" fill="{rnd.choice([AMBER, PINK, "#fff", "#fb923c"])}" class="sk" '
        f'style="animation-delay:-{rnd.uniform(0, 1):.2f}s;--dy:{rnd.uniform(-14, 14):.0f}px"/>' for _ in range(16))
    inner = f"""
<defs>
  <linearGradient id="flame" x1="1" x2="0"><stop offset="0" stop-color="#fff"/><stop offset=".25" stop-color="{AMBER}"/><stop offset=".6" stop-color="{PINK}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
  <linearGradient id="hull" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f8fafc"/><stop offset=".55" stop-color="#cbd5e1"/><stop offset="1" stop-color="#64748b"/></linearGradient>
  <linearGradient id="trail" x1="0" x2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset=".7" stop-color="{CYAN}" stop-opacity=".5"/><stop offset="1" stop-color="{PINK}" stop-opacity=".9"/></linearGradient>
  <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".1" stop-color="#fff"/><stop offset=".9" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
</defs>
<style>
  .wp{{animation:wp 2s linear infinite}} @keyframes wp{{from{{transform:translateX({W + 100}px)}}to{{transform:translateX(-120px)}}}}
  .rk{{animation:rk 9s cubic-bezier(.45,.05,.55,.95) -4.5s infinite}}
  @keyframes rk{{0%{{transform:translate(-160px,58px)}}100%{{transform:translate({W + 160}px,52px)}}}}
  .bob{{animation:bob 1.2s ease-in-out infinite alternate}} @keyframes bob{{to{{transform:translateY(-5px) rotate(-2deg)}}}}
  .fl{{animation:fl .12s linear infinite alternate;transform-box:fill-box;transform-origin:right center}} @keyframes fl{{to{{transform:scaleX(1.35) scaleY(.85)}}}}
  .sk{{animation:sk 1s linear infinite}} @keyframes sk{{from{{opacity:1;transform:translate(-26px,0)}}to{{opacity:0;transform:translate(-120px,var(--dy))}}}}
  .tr{{animation:tr 9s cubic-bezier(.45,.05,.55,.95) -4.5s infinite}} @keyframes tr{{0%{{transform:translateX(-1520px)}}100%{{transform:translateX(0)}}}}
</style>
<g mask="url(#m)">
  {streaks}
  <rect class="tr" x="0" y="54" width="1340" height="3" rx="1.5" fill="url(#trail)"/>
</g>
<g class="rk"><g class="bob">
  <path class="fl" d="M-22 -7 Q-70 0 -22 7Z" fill="url(#flame)"/>
  {sparks}
  <path d="M-24 -10 L-34 -20 L-14 -10Z M-24 10 L-34 20 L-14 10Z" fill="{PINK}"/>
  <path d="M-24 -10 H22 Q44 0 22 10 H-24Z" fill="url(#hull)"/>
  <path d="M28 -6 Q44 0 28 6 Q32 0 28 -6Z" fill="{VIOLET}"/>
  <circle cx="8" cy="0" r="5" fill="#0b0d1a" stroke="{CYAN}" stroke-width="2"/><circle cx="6.5" cy="-1.5" r="1.4" fill="#fff" opacity=".8"/>
  <rect x="-18" y="-2" width="12" height="4" rx="2" fill="{VIOLET}"/>
</g></g>
"""
    save("launch.svg", svg(W, H, inner, "A rocket crossing at warp speed"))


# ─────────────────────────── TECH ORBITS ────────────────────────────
ORBITS = [  # (radius x, radius y, seconds per lap, [(name, colour)])
    (190, 62, 40, [("Python", "#4B8BBE"), ("C++", "#659AD2"), ("SQL", "#4479A1"), ("TypeScript", "#3178C6")]),
    (330, 108, 70, [("PyTorch", "#EE4C2C"), ("FastAPI", "#009688"), ("React", "#61DAFB"),
                    ("TensorFlow", "#FF6F00"), ("Node.js", "#339933")]),
    (480, 156, 110, [("Docker", "#2496ED"), ("PostgreSQL", "#4169E1"), ("Redis", "#DC382D"),
                     ("Kafka", "#e2e8f0"), ("Linux", "#FCC624"), ("Grafana", "#F46800")]),
]


def orbits():
    rnd = random.Random(21)
    W, H, CX, CY = 1200, 400, 600, 200
    stars = "".join(
        f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, H):.0f}" r="{rnd.choice([.5, .7, 1, 1.3])}" fill="#fff" '
        f'class="tw" style="animation-delay:{rnd.uniform(0, 4):.1f}s"/>' for _ in range(110))
    rings, planets = [], []
    for k, (rx, ry, dur, techs) in enumerate(ORBITS):
        rings.append(f'<ellipse cx="{CX}" cy="{CY}" rx="{rx}" ry="{ry}" fill="none" stroke="{[VIOLET, CYAN, PINK][k]}" '
                     f'stroke-opacity=".35" stroke-dasharray="{"2 6" if k % 2 else "none"}"/>')
        path = f"M{CX + rx} {CY}A{rx} {ry} 0 1 1 {CX - rx} {CY}A{rx} {ry} 0 1 1 {CX + rx} {CY}"
        for i, (name, col) in enumerate(techs):
            w = len(name) * 8.4 + 34
            begin = -dur * i / len(techs)
            planets.append(f"""
  <g><animateMotion dur="{dur}s" repeatCount="indefinite" begin="{begin:.2f}s" path="{path}"/>
    <circle r="16" fill="{col}" opacity=".18"/><circle r="6" fill="{col}"/>
    <g transform="translate(12 -14)"><rect width="{w:.0f}" height="24" rx="12" fill="{PANEL}" fill-opacity=".9" stroke="{EDGE}"/>
    <text x="{w / 2:.0f}" y="16.5" class="t" text-anchor="middle">{escape(name)}</text></g></g>""")
    inner = f"""
<defs>
  <radialGradient id="bg" cx=".5" cy=".5" r=".7"><stop offset="0" stop-color="#140c34"/><stop offset="1" stop-color="{BG}"/></radialGradient>
  <radialGradient id="sun" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="#c4b5fd"/><stop offset=".75" stop-color="{VIOLET}"/><stop offset="1" stop-color="#4c1d95"/></radialGradient>
  <radialGradient id="corona" r=".5"><stop offset=".45" stop-color="{VIOLET}" stop-opacity=".6"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<style>
  .t{{font:600 12.5px {MONO};fill:{TEXT}}}
  .tw{{animation:tw 3.5s ease-in-out infinite}} @keyframes tw{{0%,100%{{opacity:.2}}50%{{opacity:.95}}}}
  .co{{animation:co 4s ease-in-out infinite;transform-origin:{CX}px {CY}px}} @keyframes co{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.15)}}}}
  .core{{font:800 30px {SANS};fill:#fff}} .lbl{{font:600 11px {MONO};fill:{DIM};letter-spacing:2px}}
</style>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  {stars}
  {''.join(rings)}
  <circle class="co" cx="{CX}" cy="{CY}" r="80" fill="url(#corona)"/>
  <circle cx="{CX}" cy="{CY}" r="38" fill="url(#sun)"/>
  <text x="{CX}" y="{CY + 11}" text-anchor="middle" class="core">Y</text>
  {''.join(planets)}
  <text x="30" y="{H - 22}" class="lbl">INNER · LANGUAGES</text>
  <text x="{CX}" y="{H - 22}" text-anchor="middle" class="lbl">MIDDLE · FRAMEWORKS</text>
  <text x="{W - 30}" y="{H - 22}" text-anchor="end" class="lbl">OUTER · INFRA</text>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{EDGE}"/>
"""
    save("orbits.svg", svg(W, H, inner, "Tech stack as a solar system: languages, frameworks and infrastructure in orbit"))


# ─────────────────────────────── FOOTER ─────────────────────────────
def footer():
    rnd = random.Random(5)
    W, H = 1200, 230
    stars = "".join(
        f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, 150):.0f}" r="{rnd.choice([.5, .7, 1, 1.3])}" fill="#fff" '
        f'class="tw" style="animation-delay:{rnd.uniform(0, 4):.1f}s"/>' for _ in range(90))
    inner = f"""
<defs><linearGradient id="g" x1="0" x2="1" spreadMethod="reflect"><stop offset="0" stop-color="#c4b5fd"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0;0 0" dur="7s" repeatCount="indefinite"/></linearGradient>
  <radialGradient id="sky" cx=".5" cy="1" r=".9"><stop offset="0" stop-color="#2e1065"/><stop offset=".5" stop-color="#0b0820"/><stop offset="1" stop-color="{BG}"/></radialGradient>
  <radialGradient id="ground" cx=".5" cy="0" r=".7"><stop offset="0" stop-color="#1e1048"/><stop offset="1" stop-color="#03030a"/></radialGradient>
  <radialGradient id="flare" r=".5"><stop offset="0" stop-color="#fff"/><stop offset=".15" stop-color="{CYAN}" stop-opacity=".8"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
  <linearGradient id="rim" x1="0" x2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>
<style>
  .t{{font:700 26px {SANS}}} .s{{font:500 13px {MONO};fill:{MUTED}}}
  .tw{{animation:tw 3.5s ease-in-out infinite}} @keyframes tw{{0%,100%{{opacity:.2}}50%{{opacity:.95}}}}
  .rise{{animation:rise 6s ease-in-out infinite alternate}} @keyframes rise{{from{{opacity:.6;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
</style>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#sky)"/>
  {stars}
  <g class="rise"><ellipse cx="600" cy="{H - 92}" rx="260" ry="46" fill="url(#flare)" opacity=".7"/>
    <path d="M600 {H - 120}v56M560 {H - 92}h80" stroke="#fff" stroke-opacity=".5"/></g>
  <ellipse cx="600" cy="{H + 885}" rx="1500" ry="1000" fill="url(#ground)"/>
  <ellipse cx="600" cy="{H + 885}" rx="1500" ry="1000" fill="none" stroke="url(#rim)" stroke-width="2.5"/>
</g>
<text x="600" y="62" text-anchor="middle" class="t" fill="url(#g)">thanks for scrolling — let's build something great</text>
<text x="600" y="92" text-anchor="middle" class="s">yogender1.me  ·  transmitted from earth with svg, css and too much coffee</text>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{EDGE}"/>
"""
    save("footer.svg", svg(W, H, inner, "Thanks for scrolling"))


if __name__ == "__main__":
    hero(); terminal(); marquee(); cards(); dsa(); sections(); orbits(); launch(); footer()
    print("assets written to", os.path.abspath(OUT))
