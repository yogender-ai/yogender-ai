"""Community Connect Four, played through issues.

Anyone opens an issue titled "c4: drop <column>" (1-7). The workflow runs this,
the piece drops for whichever team's turn it is, and the board is redrawn.
Nobody may move twice in a row, so a game needs at least two people.

    python .github/scripts/c4.py                                    # redraw only
    python .github/scripts/c4.py --title "c4: drop 4" --by octocat --result out.txt
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live import publish  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data", "c4.json")
OUT = os.path.join(ROOT, "assets", "c4.svg")
TZ = dt.timezone(dt.timedelta(hours=5, minutes=30))

ROWS, COLS = 6, 7
TEAMS = {"R": ("RED", "#f43f5e", "#fda4af"), "Y": ("YELLOW", "#fbbf24", "#fde68a")}
BG, PANEL, EDGE = "#05060f", "#0b0d1a", "#1e1b4b"
VIOLET, CYAN, PINK, LIME = "#8b5cf6", "#22d3ee", "#f472b6", "#a3e635"
TEXT, MUTED, DIM = "#e2e8f0", "#94a3b8", "#475569"
SANS = "'Segoe UI','SF Pro Display',system-ui,-apple-system,sans-serif"
MONO = "'JetBrains Mono','Cascadia Code','SF Mono',Consolas,Menlo,monospace"


def new_game(number):
    return {"game": number, "board": [["." for _ in range(COLS)] for _ in range(ROWS)],
            "turn": "R", "moves": [], "winner": None, "line": []}


def load():
    if os.path.exists(DATA):
        with open(DATA, encoding="utf-8") as fh:
            return json.load(fh)
    return {"current": new_game(1), "record": {"R": 0, "Y": 0, "draw": 0}, "players": {}}


def save(state):
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    with open(DATA, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def four(board, r, c):
    """The winning line through (r, c), or [] if that piece didn't make four."""
    me = board[r][c]
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        line = [(r, c)]
        for sign in (1, -1):
            rr, cc = r + dr * sign, c + dc * sign
            while 0 <= rr < ROWS and 0 <= cc < COLS and board[rr][cc] == me:
                line.append((rr, cc))
                rr, cc = rr + dr * sign, cc + dc * sign
        if len(line) >= 4:
            return sorted(line)
    return []


def play(state, title, who):
    """Apply one move. Returns (ok, message for the issue reply)."""
    m = re.match(r"^\s*c4\s*:\s*(?:drop\s*)?([1-7])\s*$", title, re.I)
    if not m:
        return False, "Couldn't read a column. Use a title like `c4: drop 4` (columns 1 to 7)."
    col = int(m.group(1)) - 1
    g = state["current"]

    started = ""
    if g["winner"]:  # the previous game is over: this move opens the next one
        g = state["current"] = new_game(g["game"] + 1)
        started = f"Game #{g['game']} starts now. "

    if g["moves"] and g["moves"][-1]["by"].lower() == who.lower():
        return False, ("You made the last move, so someone else has to go next. "
                       "Send the profile to a friend and get them to drop a piece! 🙂")

    board = g["board"]
    row = next((r for r in range(ROWS - 1, -1, -1) if board[r][col] == "."), None)
    if row is None:
        return False, f"Column {col + 1} is full. Pick another one."

    team = g["turn"]
    board[row][col] = team
    g["moves"].append({"by": who, "col": col, "row": row, "team": team,
                       "at": dt.datetime.now(TZ).isoformat(timespec="seconds")})
    p = state["players"].setdefault(who, {"moves": 0, "wins": 0})
    p["moves"] += 1

    name = TEAMS[team][0]
    line = four(board, row, col)
    if line:
        g["winner"], g["line"] = team, line
        state["record"][team] += 1
        p["wins"] += 1
        return True, (f"{started}🎉 **{name} WINS game #{g['game']}!** @{who} dropped the winning piece in column {col + 1}. "
                      "The next move starts a new game.")
    if all(board[0][c] != "." for c in range(COLS)):
        g["winner"] = "draw"
        state["record"]["draw"] += 1
        return True, f"{started}The board is full: game #{g['game']} is a draw. The next move starts a new game."
    g["turn"] = "Y" if team == "R" else "R"
    nxt = TEAMS[g["turn"]][0]
    return True, (f"{started}You dropped a {name} piece in column {col + 1}. "
                  f"It's {nxt}'s turn now, and the next move has to come from someone other than you.")


def render(state):
    g = state["current"]
    board, last = g["board"], (g["moves"][-1] if g["moves"] else None)
    W, H = 1200, 560
    CELL, BX, BY = 66, 70, 110
    BW, BH = CELL * COLS, CELL * ROWS
    win = {tuple(x) for x in g.get("line", [])}

    cells = []
    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = BX + c * CELL + CELL / 2, BY + r * CELL + CELL / 2
            v = board[r][c]
            if v == ".":
                cells.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="25" fill="#03030a" stroke="{EDGE}"/>')
                continue
            _, col, light = TEAMS[v]
            drop = ""
            if last and (r, c) == (last["row"], last["col"]):
                drop = (f'<animate attributeName="cy" from="{BY - 40}" to="{cy:.0f}" dur=".7s" fill="freeze" '
                        f'calcMode="spline" keyTimes="0;1" keySplines=".5 0 1 1"/>')
            cells.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="25" fill="url(#g{v})">{drop}</circle>')
            if (r, c) in win:
                cells.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="29" fill="none" stroke="#fff" stroke-width="3" class="win"/>')
    labels = "".join(f'<text x="{BX + c * CELL + CELL / 2:.0f}" y="{BY - 14}" text-anchor="middle" class="col">{c + 1}</text>'
                     for c in range(COLS))

    if g["winner"] == "draw":
        status, scol = "DRAW — next move starts a new game", MUTED
    elif g["winner"]:
        status, scol = f"{TEAMS[g['winner']][0]} WINS! next move starts a new game", TEAMS[g["winner"]][1]
    else:
        status, scol = f"{TEAMS[g['turn']][0]}'S TURN", TEAMS[g["turn"]][1]
    last_txt = (f"@{escape(last['by'])} dropped {TEAMS[last['team']][0].lower()} in column {last['col'] + 1}"
                if last else "no moves yet — be the first")

    top = sorted(state["players"].items(), key=lambda kv: (-kv[1]["wins"], -kv[1]["moves"], kv[0].lower()))[:5]
    PX = 620
    board_rows = "".join(
        f'<text x="{PX}" y="{322 + i * 26}" class="lb"><tspan fill="{[LIME, CYAN, VIOLET, PINK, MUTED][i]}">{i + 1}.</tspan> '
        f'@{escape(login[:18])}</text>'
        f'<text x="{W - 50}" y="{322 + i * 26}" text-anchor="end" class="lb" fill="{MUTED}">{p["wins"]}W · {p["moves"]} moves</text>'
        for i, (login, p) in enumerate(top)) or f'<text x="{PX}" y="322" class="lb" fill="{DIM}">empty — your name could be here</text>'
    rec = state["record"]
    inner = f"""
<defs>
  <radialGradient id="bg" cx=".3" cy=".4" r=".9"><stop offset="0" stop-color="#140c34"/><stop offset="1" stop-color="{BG}"/></radialGradient>
  <radialGradient id="gR" cx=".35" cy=".3" r=".7"><stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="{TEAMS['R'][2]}"/><stop offset="1" stop-color="{TEAMS['R'][1]}"/></radialGradient>
  <radialGradient id="gY" cx=".35" cy=".3" r=".7"><stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="{TEAMS['Y'][2]}"/><stop offset="1" stop-color="{TEAMS['Y'][1]}"/></radialGradient>
  <linearGradient id="frame" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#312e81"/><stop offset="1" stop-color="#1e1b4b"/></linearGradient>
  <linearGradient id="tg" x1="0" x2="1" spreadMethod="reflect"><stop offset="0" stop-color="{TEAMS['R'][1]}"/><stop offset=".5" stop-color="{PINK}"/><stop offset="1" stop-color="{TEAMS['Y'][1]}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0;0 0" dur="8s" repeatCount="indefinite"/></linearGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<style>
  .tag{{font:700 12px {MONO};letter-spacing:2px;fill:{PINK}}}
  .ttl{{font:800 30px {SANS};fill:url(#tg)}}
  .st{{font:800 24px {SANS}}}
  .sub{{font:600 13px {MONO};fill:{MUTED}}}
  .col{{font:700 15px {MONO};fill:{DIM}}}
  .lb{{font:600 14px {MONO};fill:{TEXT}}}
  .h{{font:700 11px {MONO};letter-spacing:2px;fill:{DIM}}}
  .big{{font:800 34px {SANS}}}
  .win{{animation:w 1s ease-in-out infinite}} @keyframes w{{50%{{opacity:.2}}}}
  .pulse{{animation:p 1.4s ease-in-out infinite}} @keyframes p{{50%{{opacity:.45}}}}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect x="{BX - 14}" y="{BY - 8}" width="{BW + 28}" height="{BH + 22}" rx="20" fill="url(#frame)" stroke="{VIOLET}" stroke-opacity=".5"/>
  {labels}
  {''.join(cells)}
  <text x="{BX + BW / 2}" y="{H - 22}" text-anchor="middle" class="sub">game #{g['game']} · move {len(g['moves'])}</text>

  <text x="{PX}" y="56" class="tag">// COMMUNITY CONNECT FOUR</text>
  <text x="{PX}" y="94" class="ttl">Everyone vs everyone</text>
  <text x="{PX}" y="120" class="sub">pick a column below · you can't move twice in a row</text>
  <circle cx="{PX + 10}" cy="160" r="10" fill="{scol}" class="pulse"/>
  <text x="{PX + 30}" y="169" class="st" fill="{scol}">{escape(status)}</text>
  <text x="{PX}" y="200" class="sub">last: {last_txt}</text>

  <text x="{PX}" y="246" class="h">ALL-TIME RECORD</text>
  <text x="{PX}" y="282" class="big" fill="{TEAMS['R'][1]}">{rec['R']}</text><text x="{PX + 48}" y="282" class="sub">red</text>
  <text x="{PX + 130}" y="282" class="big" fill="{TEAMS['Y'][1]}">{rec['Y']}</text><text x="{PX + 178}" y="282" class="sub">yellow</text>
  <text x="{PX + 290}" y="282" class="big" fill="{MUTED}">{rec['draw']}</text><text x="{PX + 338}" y="282" class="sub">draws</text>

  <g transform="translate(0 40)">
    <text x="{PX}" y="290" class="h">TOP PLAYERS</text>
    {board_rows}
  </g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{EDGE}"/>
"""
    label = f"Community Connect Four, game {g['game']}: {status}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{escape(label)}"><title>{escape(label)}</title>{inner}</svg>')


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--title")
    ap.add_argument("--by")
    ap.add_argument("--result", help="file to write the reply text into")
    args = ap.parse_args()

    state = load()
    ok, msg = True, ""
    if args.title:
        ok, msg = play(state, args.title, (args.by or "someone").lstrip("@"))
        if ok:
            save(state)
        print(msg)
        if args.result:
            with open(args.result, "w", encoding="utf-8") as fh:
                fh.write(msg + "\n")
    else:
        save(state)

    body = render(state)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    print(f"wrote assets/c4.svg and assets/live/{publish('c4', body)}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
