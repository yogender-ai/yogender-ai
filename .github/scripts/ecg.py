"""Draw a commit history as an ECG trace.

Every beat is a real day. The amplitude is that day's contribution count, so a
heavy day spikes and a day you did not code is a genuine flatline. The pulse
that runs along the trace is the reader's eye being dragged through your year.

Both data sources are public and need no token:
  * https://github.com/users/<login>/contributions - exact per-day counts
  * /users/<login>/events/public                   - push times, for peak hour

    python .github/scripts/ecg.py
"""
import datetime as dt
import json
import os
import re
import urllib.request
from collections import Counter
from xml.sax.saxutils import escape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "ecg.svg")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecg_data.json")
USER = "yogender-ai"
TZ = dt.timezone(dt.timedelta(hours=5, minutes=30))  # IST

DAYS = 90            # how much history the trace shows
W, H = 1200, 400
BASE_Y = 250         # the flatline
MAX_AMP = 78         # tallest possible spike

BG, PANEL, EDGE = "#05060f", "#0b0d1a", "#1e1b4b"
VIOLET, CYAN, PINK, LIME, AMBER = "#8b5cf6", "#22d3ee", "#f472b6", "#a3e635", "#fbbf24"
TEXT, MUTED, DIM = "#e2e8f0", "#94a3b8", "#475569"
TRACE = "#4ade80"
SANS = "'Segoe UI','SF Pro Display',system-ui,-apple-system,sans-serif"
MONO = "'JetBrains Mono','Cascadia Code','SF Mono',Consolas,Menlo,monospace"

UA = {"User-Agent": "Mozilla/5.0 (compatible; commit-ecg/1.0)", "Accept": "text/html"}


def fetch_days(user=USER):
    """Per-day contribution counts for the last year, straight off the profile."""
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "replace")

    # Each day cell has an id; the exact count lives in the tool-tip that points at it.
    ids = dict(re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"\s+id="(contribution-day-component-[0-9-]+)"', html))
    by_id = {}
    for tip_for, text in re.findall(r'<tool-tip[^>]*for="(contribution-day-component-[0-9-]+)"[^>]*>([^<]*)', html):
        m = re.match(r"([\d,]+) contribution", text.strip())
        by_id[tip_for] = int(m.group(1).replace(",", "")) if m else 0

    days = {date: by_id.get(cid, 0) for date, cid in ids.items()}
    if not days:
        raise ValueError("could not parse the contributions calendar")
    return days


def fetch_push_hours(user=USER):
    """Hour-of-day histogram from recent public pushes. Best effort."""
    try:
        req = urllib.request.Request(f"https://api.github.com/users/{user}/events/public?per_page=100",
                                     headers={"User-Agent": UA["User-Agent"]})
        with urllib.request.urlopen(req, timeout=30) as r:
            events = json.load(r)
    except Exception as exc:
        print(f"  ! could not read public events ({exc}); skipping peak hour")
        return Counter()

    hours = Counter()
    for e in events:
        if e.get("type") != "PushEvent":
            continue
        when = dt.datetime.strptime(e["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
        hours[when.astimezone(TZ).hour] += 1
    return hours


def beat(x, w, y0, amp):
    """One heartbeat: flat, P bump, the QRS spike, T bump, flat.

    A day with no contributions returns a flat segment, so the gaps in the year
    read as an actual flatline rather than a small bump.
    """
    if amp <= 0:
        return [(x, y0), (x + w, y0)]
    return [
        (x, y0),
        (x + w * 0.14, y0),
        (x + w * 0.22, y0 - amp * 0.13),   # P wave
        (x + w * 0.30, y0),
        (x + w * 0.36, y0 + amp * 0.10),   # Q dip
        (x + w * 0.44, y0 - amp),          # R spike
        (x + w * 0.52, y0 + amp * 0.30),   # S trough
        (x + w * 0.60, y0),
        (x + w * 0.72, y0 - amp * 0.20),   # T wave
        (x + w * 0.84, y0),
        (x + w, y0),
    ]


def build(days, window=DAYS):
    today = dt.datetime.now(TZ).date()
    span = [today - dt.timedelta(days=i) for i in range(window - 1, -1, -1)]
    counts = [days.get(d.isoformat(), 0) for d in span]

    peak = max(counts) if counts else 0
    left, right = 56, W - 56
    w = (right - left) / window

    pts = []
    for i, c in enumerate(counts):
        amp = 0 if c == 0 else max(14, MAX_AMP * (c / peak) ** 0.75)
        pts.extend(beat(left + i * w, w, BASE_Y, amp))

    path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return path, span, counts, peak


def stats(days, counts, span, hours):
    total = sum(counts)
    active = sum(1 for c in counts if c)
    avg = total / max(len(counts), 1)

    # An empty today does not break a streak - the day is not over yet, which
    # is how GitHub counts it too. Otherwise the card reads 0 every morning.
    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    streak = 0
    for c in reversed(tail):
        if c == 0:
            break
        streak += 1

    longest_flat, run = 0, 0
    for c in counts:
        run = run + 1 if c == 0 else 0
        longest_flat = max(longest_flat, run)

    peak_i = max(range(len(counts)), key=lambda i: counts[i]) if counts else 0
    peak_hour = hours.most_common(1)[0][0] if hours else None

    return {
        "bpm": round(avg, 1),
        "total": total,
        "active": active,
        "window": len(counts),
        "streak": streak,
        "flatline": longest_flat,
        "peak": counts[peak_i] if counts else 0,
        "peak_day": span[peak_i].strftime("%d %b") if span else "",
        "peak_hour": peak_hour,
        "year_total": sum(days.values()),
    }


def render(path, s):
    dur = 14  # seconds for one sweep of the whole trace
    grid = []
    for gx in range(56, W - 40, 24):
        grid.append(f'<line x1="{gx}" y1="150" x2="{gx}" y2="330" stroke="#14351f" stroke-width="1" opacity=".5"/>')
    for gy in range(150, 331, 24):
        grid.append(f'<line x1="56" y1="{gy}" x2="{W - 56}" y2="{gy}" stroke="#14351f" stroke-width="1" opacity=".5"/>')

    hour_txt = f"{s['peak_hour']:02d}:00" if s["peak_hour"] is not None else "--"
    tiles = [
        ("AVG / DAY", f"{s['bpm']}", f"{s['total']} in {s['window']} days", LIME),
        ("PEAK", f"{s['peak']}", f"on {s['peak_day']}", AMBER),
        ("CURRENT STREAK", f"{s['streak']}d", f"{s['active']}/{s['window']} days active", CYAN),
        ("LONGEST FLATLINE", f"{s['flatline']}d", "silence in the window", PINK),
        ("PEAK HOUR", hour_txt, "when the pushes land (IST)", VIOLET),
    ]
    tile_w = (W - 112 - 4 * 14) / 5
    tile_svg = "".join(
        f'<g transform="translate({56 + i * (tile_w + 14):.1f} 344)">'
        f'<rect width="{tile_w:.1f}" height="44" rx="10" fill="{c}" fill-opacity=".07" stroke="{c}" stroke-opacity=".32"/>'
        f'<text x="12" y="17" style="font:700 9px {MONO};letter-spacing:1.1px;fill:{c}">{escape(k)}</text>'
        f'<text x="12" y="36" style="font:800 15px {SANS};fill:{TEXT}">{escape(v)}</text>'
        f'<text x="{tile_w - 12:.1f}" y="36" text-anchor="end" style="font:500 9px {MONO};fill:{MUTED}">{escape(sub)}</text>'
        f"</g>"
        for i, (k, v, sub, c) in enumerate(tiles)
    )

    inner = f"""
<defs>
  <filter id="glow" x="-20%" y="-60%" width="140%" height="220%">
    <feGaussianBlur stdDeviation="3.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <linearGradient id="fade" x1="0" x2="1">
    <stop offset="0" stop-color="{TRACE}" stop-opacity=".25"/>
    <stop offset=".55" stop-color="{TRACE}" stop-opacity=".9"/>
    <stop offset="1" stop-color="{TRACE}" stop-opacity=".25"/>
  </linearGradient>
</defs>
<style>
  .tag{{font:700 12px {MONO};letter-spacing:2px;fill:{PINK}}}
  .ttl{{font:800 26px {SANS};fill:{TEXT}}}
  .sub{{font:600 12px {MONO};fill:{MUTED}}}
  .draw{{stroke-dasharray:14000;stroke-dashoffset:14000;animation:draw {dur}s linear infinite}}
  @keyframes draw{{to{{stroke-dashoffset:0}}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="{BG}" stroke="{EDGE}"/>
<rect x="28" y="24" width="{W - 56}" height="{H - 48}" rx="16" fill="{PANEL}" fill-opacity=".5" stroke="{EDGE}"/>
<text x="56" y="60" class="tag">// COMMIT ECG · LAST {s['window']} DAYS</text>
<text x="56" y="94" class="ttl">This is what my year sounds like</text>
<text x="56" y="116" class="sub">every beat is a real day · a flat stretch is a day I wrote nothing · {s['year_total']:,} contributions this year</text>
<g opacity=".55">{"".join(grid)}</g>
<line x1="56" y1="{BASE_Y}" x2="{W - 56}" y2="{BASE_Y}" stroke="{TRACE}" stroke-opacity=".12" stroke-width="1"/>
<path id="trace" d="{path}" fill="none" stroke="url(#fade)" stroke-width="2" stroke-opacity=".28"
      stroke-linejoin="round" stroke-linecap="round"/>
<path d="{path}" fill="none" stroke="{TRACE}" stroke-width="2.4" stroke-linejoin="round"
      stroke-linecap="round" filter="url(#glow)" class="draw"/>
<circle r="4.5" fill="#eafff2" filter="url(#glow)">
  <animateMotion dur="{dur}s" repeatCount="indefinite" rotate="auto">
    <mpath xlink:href="#trace" href="#trace"/>
  </animateMotion>
</circle>
{tile_svg}
"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Commit history drawn as an ECG trace over the last {s["window"]} days">'
            f'<title>Commit ECG — {s["total"]} contributions over {s["window"]} days</title>{inner}</svg>')


def main():
    try:
        days = fetch_days()
        with open(CACHE, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"fetched": dt.datetime.now(TZ).isoformat(timespec="seconds"), "days": days},
                      fh, indent=0, sort_keys=True)
            fh.write("\n")
    except Exception as exc:
        print(f"  ! live fetch failed ({exc})")
        if not os.path.exists(CACHE):
            raise SystemExit("no contribution data and no cache - refusing to draw a flat year")
        with open(CACHE, encoding="utf-8") as fh:
            days = json.load(fh)["days"]
        print("  falling back to the cached calendar")

    path, span, counts, peak = build(days)
    s = stats(days, counts, span, fetch_push_hours())

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(path, s))
    print(f"wrote assets/ecg.svg - {s['total']} contributions over {s['window']} days, "
          f"peak {s['peak']} on {s['peak_day']}, longest flatline {s['flatline']}d")


if __name__ == "__main__":
    main()
