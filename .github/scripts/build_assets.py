"""Generate the animated SVGs used by the profile README.

Edit the data below and run:  python .github/scripts/build_assets.py
Everything is pure SVG + CSS/SMIL (no JS, no external fonts) so GitHub renders it inside <img>.
"""
import os
import random
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets")

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


# ─────────────────────────────── HERO ───────────────────────────────
def hero():
    rnd = random.Random(7)
    W, H, HZ = 1200, 420, 285  # HZ = horizon line of the grid floor
    stars = "".join(
        f'<circle cx="{rnd.randint(10, W - 10)}" cy="{rnd.randint(10, HZ - 20)}" r="{rnd.choice([0.8, 1, 1.2, 1.6])}" '
        f'fill="#fff" class="tw" style="animation-delay:{rnd.uniform(0, 4):.2f}s"/>' for _ in range(55))
    radials = "".join(f'<line x1="600" y1="{HZ}" x2="{x}" y2="{H}"/>' for x in range(-1800, 3001, 160))
    floor = "".join(
        f'<line x1="0" x2="{W}" y1="{HZ}" y2="{HZ}"><animate attributeName="y1" values="{HZ};{H}" dur="3.2s" '
        f'begin="-{i * 0.4:.1f}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines=".55 0 1 .45"/>'
        f'<animate attributeName="y2" values="{HZ};{H}" dur="3.2s" begin="-{i * 0.4:.1f}s" repeatCount="indefinite" '
        f'calcMode="spline" keyTimes="0;1" keySplines=".55 0 1 .45"/></line>' for i in range(8))
    roles = [
        "AI / ML Engineer · High-Performance Systems",
        "Full-Stack Builder · FastAPI · React · Cloud",
        "Level 17 Algorithm Grandmaster · 276 Solved · 74d Streak 🔥",
        "I ship products, not notebooks"
    ]
    role_txt = "".join(f'<text x="600" y="252" class="role" style="animation-delay:{i * 3.2:.1f}s">{escape(r)}</text>'
                       for i, r in enumerate(roles))
    inner = f"""
<defs>
  <linearGradient id="name" x1="0" x2="1" y1="0" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="{VIOLET}"/><stop offset=".35" stop-color="{CYAN}"/>
    <stop offset=".7" stop-color="{PINK}"/><stop offset="1" stop-color="{VIOLET}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0;0 0" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="floorfade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/>
  </linearGradient>
  <mask id="floormask"><rect x="0" y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#floorfade)"/></mask>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="26"/></clipPath>
</defs>
<style>
  .tw{{animation:tw 3.5s ease-in-out infinite}}
  @keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
  .b1{{animation:f1 14s ease-in-out infinite}} .b2{{animation:f2 18s ease-in-out infinite}} .b3{{animation:f3 16s ease-in-out infinite}}
  @keyframes f1{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(260px,50px)}}}}
  @keyframes f2{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-300px,30px)}}}}
  @keyframes f3{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(120px,-60px)}}}}
  .name{{font:800 104px {SANS};letter-spacing:12px;text-anchor:middle}}
  .g1{{fill:{CYAN};opacity:0;animation:g1 4s steps(1) infinite}} .g2{{fill:{PINK};opacity:0;animation:g2 4s steps(1) infinite}}
  @keyframes g1{{0%,88%{{opacity:0;transform:none}}89%{{opacity:.75;transform:translate(-6px,2px)}}91%{{opacity:.75;transform:translate(4px,-2px)}}93%,100%{{opacity:0;transform:none}}}}
  @keyframes g2{{0%,88%{{opacity:0;transform:none}}89%{{opacity:.75;transform:translate(6px,-1px)}}91%{{opacity:.75;transform:translate(-5px,2px)}}93%,100%{{opacity:0;transform:none}}}}
  .role{{font:500 24px {MONO};fill:{CYAN};text-anchor:middle;opacity:0;animation:role 12.8s infinite}}
  @keyframes role{{0%{{opacity:0;transform:translateY(14px)}}3%,22%{{opacity:1;transform:none}}25%,100%{{opacity:0;transform:translateY(-14px)}}}}
  .chip{{font:600 13px {MONO};fill:{MUTED}}}
  .dot{{animation:pulse 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}}
  @keyframes pulse{{0%{{transform:scale(1);opacity:.9}}100%{{transform:scale(3.2);opacity:0}}}}
  .scan{{animation:scan 6s linear infinite}}
  @keyframes scan{{0%{{transform:translateY(-40px)}}100%{{transform:translateY({H + 40}px)}}}}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <g filter="url(#blur)" opacity=".75">
    <circle class="b1" cx="260" cy="120" r="170" fill="{VIOLET}"/>
    <circle class="b2" cx="930" cy="110" r="160" fill="{CYAN}" opacity=".7"/>
    <circle class="b3" cx="620" cy="300" r="140" fill="{PINK}" opacity=".55"/>
  </g>
  {stars}
  <g mask="url(#floormask)" stroke="{VIOLET}" stroke-width="1.2" opacity=".75">{radials}{floor}</g>
  <line x1="0" x2="{W}" y1="{HZ}" y2="{HZ}" stroke="{PINK}" stroke-opacity=".6" stroke-width="1.5"/>
  <rect class="scan" x="0" y="0" width="{W}" height="40" fill="url(#floorfade)" opacity=".05"/>

  <g transform="translate(40 36)">
    <rect width="232" height="32" rx="16" fill="{PANEL}" fill-opacity=".75" stroke="{EDGE}"/>
    <circle cx="20" cy="16" r="5" fill="{LIME}"/><circle class="dot" cx="20" cy="16" r="5" fill="{LIME}"/>
    <text x="34" y="21" class="chip">currently shipping</text>
  </g>
  <g transform="translate({W - 240} 36)">
    <rect width="200" height="32" rx="16" fill="{PANEL}" fill-opacity=".75" stroke="{EDGE}"/>
    <text x="100" y="21" class="chip" text-anchor="middle">🔥 74d streak · Level 17</text>
  </g>

  <text x="600" y="190" class="name g1">YOGENDER</text>
  <text x="600" y="190" class="name g2">YOGENDER</text>
  <text x="600" y="190" class="name" fill="url(#name)" filter="url(#glow)">YOGENDER</text>
  {role_txt}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="26" fill="none" stroke="{EDGE}"/>
"""
    save("hero.svg", svg(W, H, inner, "Yogender — AI/ML Engineer · Full-Stack Builder"))


# ───────────────────────────── TERMINAL ─────────────────────────────
def terminal():
    W, H, T = 1200, 390, 20.0
    CW = 9.3
    session = [
        ("whoami", [("yogender", PINK), ("  ·  AI/ML engineer & systems builder  ·  India", MUTED)]),
        ("cat stack.txt", [("python  c++  sql  ", AMBER), ("fastapi  react  pytorch  ", CYAN), ("postgres  redis  docker  kafka", VIOLET)]),
        ("ls ~/projects --shipped", [("DSA-Journey/  NewsIntel/  CloudCommand/  ParticleGravity/  KNN-Demo/  FinanceInsight/", TEAL)]),
        ("./dsa --stats", [("276 solved", LIME), ("  ·  ", DIM), ("158 easy", TEAL), ("  ·  ", DIM), ("109 med", AMBER), ("  ·  ", DIM), ("9 hard", PINK), ("  ·  74-day streak 🔥  ·  top 26% contest", VIOLET)]),
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
<text x="600" y="27" text-anchor="middle" style="font:500 13px {MONO}" fill="{MUTED}">yogender@dev: ~ — zsh</text>
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
  <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/><stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<style>
  .t{{font:600 14px {MONO};fill:{TEXT}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="{BG}" stroke="{EDGE}"/>
<g mask="url(#fade)">{''.join(rows)}</g>
"""
    save("marquee.svg", svg(W, H, inner, "Tech stack"))


# ─────────────────────────── PROJECT CARDS ──────────────────────────
CARDS = [
    ("dsa-journey", "⚔️", "DSA · LeetCode Journey", "ALGORITHMS · RPG", [
        "276 problems, 74-day streak, Level 17",
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
    easy, med, hard = 158, 109, 9
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
  <text y="142" class="k" fill="{LIME}">🔥 74-Day Continuous</text>
  <text y="166" class="k" fill="{CYAN}">⚔️ 1585 Rating (Top 26%)</text>
  <text y="210" class="st" style="font:700 13px {MONO}" fill="{VIOLET}">open the journey →</text>
</g>
"""
    save("dsa.svg", svg(W, H, inner, f"DSA journey: {total} LeetCode problems solved · 74-day streak"))


# ─────────────────────────── SECTION TITLES ─────────────────────────
SECTIONS = [("about", "01", "about me"), ("projects", "02", "featured work"), ("stack", "03", "tech stack"),
            ("dsa", "04", "dsa journey"), ("stats", "05", "live github stats"), ("connect", "06", "let's connect")]


def sections():
    W, H = 1200, 70
    for slug, num, label in SECTIONS:
        inner = f"""
<defs><linearGradient id="g" x1="0" x2="1" spreadMethod="reflect"><stop offset="0" stop-color="{VIOLET}"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0;0 0" dur="6s" repeatCount="indefinite"/></linearGradient>
  <linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient></defs>
<style>
  .n{{font:700 15px {MONO};fill:{DIM};letter-spacing:2px}} .t{{font:800 30px {SANS};letter-spacing:1px}}
  .s{{animation:s 3.5s ease-in-out infinite}} @keyframes s{{0%{{transform:translateX(-420px)}}100%{{transform:translateX({W}px)}}}}
</style>
<text x="600" y="38" text-anchor="middle"><tspan class="n">{num} // </tspan><tspan class="t" fill="url(#g)">{escape(label)}</tspan></text>
<rect x="300" y="56" width="600" height="1" fill="{EDGE}"/>
<rect class="s" x="0" y="55" width="400" height="3" rx="1.5" fill="url(#ln)"/>
"""
        save(f"sections/{slug}.svg", svg(W, H, inner, label))


# ─────────────────────────────── FOOTER ─────────────────────────────
def footer():
    W, H = 1200, 190

    def wave(amp, y, length):
        pts = [f"M0 {y}"]
        for i in range(0, 2 * W + length, length):
            pts.append(f"q{length / 4} {-amp} {length / 2} 0 t{length / 2} 0")
        return "".join(pts) + f"V{H}H0z"
    inner = f"""
<defs><linearGradient id="g" x1="0" x2="1" spreadMethod="reflect"><stop offset="0" stop-color="{VIOLET}"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0;0 0" dur="7s" repeatCount="indefinite"/></linearGradient>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>
<style>
  .w1{{animation:m 9s linear infinite}} .w2{{animation:m 13s linear infinite reverse}} .w3{{animation:m 17s linear infinite}}
  @keyframes m{{to{{transform:translateX(-{W // 2}px)}}}}
  .t{{font:700 24px {SANS}}} .s{{font:500 13px {MONO};fill:{MUTED}}}
</style>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <path class="w1" d="{wave(18, 125, 300)}" fill="{VIOLET}" opacity=".35"/>
  <path class="w2" d="{wave(14, 140, 400)}" fill="{CYAN}" opacity=".22"/>
  <path class="w3" d="{wave(10, 155, 240)}" fill="{PINK}" opacity=".2"/>
</g>
<text x="600" y="62" text-anchor="middle" class="t" fill="url(#g)">thanks for scrolling — let's build something great</text>
<text x="600" y="92" text-anchor="middle" class="s">yogender1.me  ·  made with svg, css and too much coffee</text>
"""
    save("footer.svg", svg(W, H, inner, "Thanks for scrolling"))


if __name__ == "__main__":
    hero(); terminal(); marquee(); cards(); dsa(); sections(); footer()
    print("assets written to", os.path.abspath(OUT))
