"""A shared pixel canvas that lives on a GitHub profile.

Anyone opens an issue titled `place: <x> <y> <colour>` and that pixel changes
for everyone, forever. The canvas is the only thing on this profile that other
people own.

    python .github/scripts/place.py                     # redraw
    python .github/scripts/place.py --paint 12 30 red --by octocat
"""
import argparse
import datetime as dt
import json
import os
import re
from xml.sax.saxutils import escape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data", "place.json")
OUT = os.path.join(ROOT, "assets", "place.svg")
TZ = dt.timezone(dt.timedelta(hours=5, minutes=30))

GRID = 48            # canvas is GRID x GRID pixels
COOLDOWN_MIN = 10    # minutes one person must wait between pixels

BG, PANEL, EDGE = "#05060f", "#0b0d1a", "#1e1b4b"
TEXT, MUTED, DIM = "#e2e8f0", "#94a3b8", "#475569"
SANS = "'Segoe UI','SF Pro Display',system-ui,-apple-system,sans-serif"
MONO = "'JetBrains Mono','Cascadia Code','SF Mono',Consolas,Menlo,monospace"

# Deliberately small, so the canvas keeps a coherent look however many
# strangers paint on it.
COLORS = {
    "violet": "#8b5cf6",
    "cyan": "#22d3ee",
    "pink": "#f472b6",
    "lime": "#a3e635",
    "amber": "#fbbf24",
    "teal": "#2dd4bf",
    "red": "#ff5370",
    "white": "#e2e8f0",
    "slate": "#475569",
    "black": "#0b0d1a",
}
EMPTY = "#0a0c18"


def load():
    if not os.path.exists(DATA):
        return {"pixels": {}, "history": []}
    with open(DATA, encoding="utf-8") as fh:
        return json.load(fh)


def save(state):
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    state["updated"] = dt.datetime.now(TZ).isoformat(timespec="seconds")
    state["painted"] = len(state["pixels"])
    with open(DATA, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")


def parse_request(title):
    """Pull `place: <x> <y> <colour>` out of an issue title.

    Returns (x, y, colour) or raises ValueError with a message meant to be
    posted straight back to the person.
    """
    m = re.match(r"\s*place\s*:\s*(\d{1,3})\s+(\d{1,3})\s+([a-zA-Z]+)\s*$", title or "")
    if not m:
        raise ValueError(
            "I could not read that. The title needs to look like `place: 12 30 cyan` - "
            "an x, a y, and one colour."
        )
    x, y, colour = int(m.group(1)), int(m.group(2)), m.group(3).lower()
    if not (0 <= x < GRID and 0 <= y < GRID):
        raise ValueError(f"`{x} {y}` is off the canvas. Both numbers must be between 0 and {GRID - 1}.")
    if colour not in COLORS:
        raise ValueError(f"`{colour}` is not on the palette. Pick one of: {', '.join(COLORS)}.")
    return x, y, colour


def paint(state, x, y, colour, by):
    """Apply one pixel. Returns (ok, message)."""
    now = dt.datetime.now(TZ)

    last = None
    for h in reversed(state.get("history", [])):
        if h["by"].lower() == by.lower():
            last = dt.datetime.fromisoformat(h["at"])
            break
    if last is not None:
        waited = (now - last).total_seconds() / 60
        if waited < COOLDOWN_MIN:
            left = COOLDOWN_MIN - waited
            return False, (f"You painted {waited:.0f} minute(s) ago. One pixel per "
                           f"{COOLDOWN_MIN} minutes, so try again in about {left:.0f} minute(s).")

    key = f"{x},{y}"
    previous = state["pixels"].get(key, {}).get("colour")
    state["pixels"][key] = {"colour": colour, "by": by, "at": now.isoformat(timespec="seconds")}
    state.setdefault("history", []).append(
        {"x": x, "y": y, "colour": colour, "by": by, "at": now.isoformat(timespec="seconds")}
    )
    state["history"] = state["history"][-500:]

    note = f"over {previous}" if previous else "on empty canvas"
    return True, f"Painted ({x}, {y}) {colour} - {note}."


def render(state):
    pixels = state.get("pixels", {})
    history = state.get("history", [])

    cell = 13
    pad = 3
    board = GRID * cell
    W = 1200
    top = 148
    H = top + board + 116
    x0 = (W - board) / 2

    # Only non-empty cells are drawn; one flat rect carries the background.
    cells = [f'<rect x="{x0}" y="{top}" width="{board}" height="{board}" rx="8" fill="{EMPTY}"/>']
    for key, p in pixels.items():
        cx, cy = (int(v) for v in key.split(","))
        cells.append(
            f'<rect x="{x0 + cx * cell:.1f}" y="{top + cy * cell:.1f}" width="{cell}" height="{cell}" '
            f'fill="{COLORS.get(p["colour"], EMPTY)}"><title>({cx}, {cy}) by {escape(p["by"])}</title></rect>'
        )
    # Grid lines on top, so the coordinates stay countable.
    for i in range(0, GRID + 1, 4):
        cells.append(f'<line x1="{x0 + i * cell:.1f}" y1="{top}" x2="{x0 + i * cell:.1f}" y2="{top + board}" '
                     f'stroke="{EDGE}" stroke-width=".6" opacity=".7"/>')
        cells.append(f'<line x1="{x0}" y1="{top + i * cell:.1f}" x2="{x0 + board}" y2="{top + i * cell:.1f}" '
                     f'stroke="{EDGE}" stroke-width=".6" opacity=".7"/>')

    # Axis labels every 8 cells.
    labels = []
    for i in range(0, GRID, 8):
        labels.append(f'<text x="{x0 + i * cell + cell / 2:.1f}" y="{top - 8}" text-anchor="middle" '
                      f'style="font:600 9px {MONO};fill:{DIM}">{i}</text>')
        labels.append(f'<text x="{x0 - 10}" y="{top + i * cell + cell / 2 + 3:.1f}" text-anchor="end" '
                      f'style="font:600 9px {MONO};fill:{DIM}">{i}</text>')

    swatch = "".join(
        f'<g transform="translate({x0 + i * 52:.1f} {top + board + 22})">'
        f'<rect width="16" height="16" rx="4" fill="{hexv}" stroke="{EDGE}"/>'
        f'<text x="20" y="12" style="font:600 9px {MONO};fill:{MUTED}">{escape(name)}</text></g>'
        for i, (name, hexv) in enumerate(list(COLORS.items())[:10])
    )

    painters = len({h["by"] for h in history})
    recent = history[-1] if history else None
    recent_txt = (f'last: ({recent["x"]}, {recent["y"]}) {recent["colour"]} by {recent["by"]}'
                  if recent else "nobody has painted yet")

    inner = f"""
<defs>
  <linearGradient id="pg" x1="0" x2="1">
    <stop offset="0" stop-color="#8b5cf6"/><stop offset=".5" stop-color="#22d3ee"/><stop offset="1" stop-color="#f472b6"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0;0 0" dur="10s" repeatCount="indefinite"/>
  </linearGradient>
</defs>
<style>
  .tag{{font:700 12px {MONO};letter-spacing:2px;fill:#f472b6}}
  .ttl{{font:800 28px {SANS};fill:url(#pg)}}
  .sub{{font:600 12px {MONO};fill:{MUTED}}}
  .big{{font:800 34px {SANS};fill:{TEXT}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="{BG}" stroke="{EDGE}"/>
<rect x="28" y="24" width="{W - 56}" height="{H - 48}" rx="16" fill="{PANEL}" fill-opacity=".5" stroke="{EDGE}"/>
<text x="56" y="62" class="tag">// THE CANVAS</text>
<text x="56" y="98" class="ttl">{GRID} x {GRID}, and none of it is mine</text>
<text x="56" y="122" class="sub">anyone can change one pixel · {COOLDOWN_MIN} minute cooldown · it stays changed</text>
<text x="{W - 56}" y="98" text-anchor="end" class="big">{len(pixels)}</text>
<text x="{W - 56}" y="122" text-anchor="end" class="sub">pixels by {painters} {'person' if painters == 1 else 'people'}</text>
{"".join(cells)}
{"".join(labels)}
{swatch}
<text x="{W - 56}" y="{top + board + 34}" text-anchor="end" style="font:600 10px {MONO};fill:{DIM}">{escape(recent_txt)}</text>
"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="A shared {GRID} by {GRID} pixel canvas, {len(pixels)} pixels painted">'
            f'<title>Shared canvas - {len(pixels)} pixels painted by {painters} '
            f'{"person" if painters == 1 else "people"}</title>{inner}</svg>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", help="issue title to parse, e.g. 'place: 12 30 cyan'")
    ap.add_argument("--paint", nargs=3, metavar=("X", "Y", "COLOUR"))
    ap.add_argument("--by", help="GitHub login of the painter")
    ap.add_argument("--result", help="write the outcome message to this file")
    args = ap.parse_args()

    state = load()
    message, ok = "", True

    if args.title or args.paint:
        try:
            if args.title:
                x, y, colour = parse_request(args.title)
            else:
                x, y, colour = int(args.paint[0]), int(args.paint[1]), args.paint[2].lower()
                if not (0 <= x < GRID and 0 <= y < GRID) or colour not in COLORS:
                    raise ValueError("coordinates or colour out of range")
            ok, message = paint(state, x, y, colour, args.by or "anonymous")
        except ValueError as exc:
            ok, message = False, str(exc)
        print(message)
        if ok:
            save(state)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(state))
    print(f"wrote assets/place.svg - {len(state.get('pixels', {}))} pixels")

    if args.result:
        with open(args.result, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(message or "canvas redrawn")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
