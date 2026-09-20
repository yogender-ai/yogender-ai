"""Sync live LeetCode statistics to GitHub profile README and SVGs.

Fetches real-time solve counts and streak from LeetCode GraphQL API,
updates build_assets.py and README.md, then rebuilds all animated SVGs.
"""
import urllib.request
import json
import re
import os
import subprocess
import sys

USERNAME = "yashyogender"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
README_PATH = os.path.join(ROOT_DIR, "README.md")
BUILD_ASSETS_PATH = os.path.join(os.path.dirname(__file__), "build_assets.py")
ECG_PATH = os.path.join(os.path.dirname(__file__), "ecg.py")
STATS_PATH = os.path.join(os.path.dirname(__file__), "leetcode_stats.json")


def fetch_leetcode_stats(username):
    url = "https://leetcode.com/graphql"
    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        username
        submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
        userCalendar {
          streak
          totalActiveDays
        }
      }
      userContestRanking(username: $username) {
        rating
        globalRanking
        totalParticipants
        topPercentage
        attendedContestsCount
      }
    }
    """
    req = urllib.request.Request(
        url,
        data=json.dumps({"query": query, "variables": {"username": username}}).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=10).read().decode("utf-8"))
        data = res.get("data") or {}
        matched = data.get("matchedUser") or {}
        if not matched:
            print(f"User {username} not found on LeetCode")
            return None

        diffs = {item["difficulty"]: item["count"] for item in matched["submitStatsGlobal"]["acSubmissionNum"]}
        cal = matched.get("userCalendar") or {}
        rank = data.get("userContestRanking") or {}

        return {
            "total": diffs.get("All", 0),
            "easy": diffs.get("Easy", 0),
            "medium": diffs.get("Medium", 0),
            "hard": diffs.get("Hard", 0),
            "streak": cal.get("streak") or 0,
            "active_days": cal.get("totalActiveDays") or 0,
            "rating": round(rank.get("rating") or 0, 2),
            "global_ranking": rank.get("globalRanking") or 0,
            "total_participants": rank.get("totalParticipants") or 0,
            "top_pct": rank.get("topPercentage") or 0,
            "contests": rank.get("attendedContestsCount") or 0,
            "level": 17,
            "rank_title": "Algorithm Grandmaster",
        }
    except Exception as e:
        print(f"Error querying LeetCode GraphQL: {e}")
        return None


def write_stats(stats):
    """Hand the numbers to build_assets.py as data.

    This used to rewrite literals inside build_assets.py with a handful of
    regexes. Any literal a regex did not match stayed frozen, which is how the
    terminal card kept advertising an old solve count and rating long after the
    badge above it had moved on.
    """
    with open(STATS_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"Wrote live statistics to {os.path.basename(STATS_PATH)}.")


def update_readme(stats):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Update LeetCode shield badge
    content = re.sub(
        r'https://img\.shields\.io/badge/LeetCode-\d+_solved_%C2%B7_\d+d_streak-FFA116',
        f'https://img.shields.io/badge/LeetCode-{stats["total"]}_solved_%C2%B7_{stats["streak"]}d_streak-FFA116',
        content
    )

    # Update hero quote block
    content = re.sub(
        r'\*\*\d+\+ LeetCode Solved\*\* · 🔥 \*\*\d+-Day Continuous Streak\*\*',
        f'**{stats["total"]}+ LeetCode Solved** · 🔥 **{stats["streak"]}-Day Continuous Streak**',
        content
    )

    with open(README_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("Updated README.md with live statistics.")


def rebuild_assets():
    subprocess.run([sys.executable, BUILD_ASSETS_PATH], check=True, cwd=ROOT_DIR)
    print("Regenerated all animated SVG assets.")


def rebuild_ecg():
    """Redraw the commit ECG. Never fail the whole sync over it: the LeetCode
    numbers are the point of this script, and the ECG reads a scraped page that
    GitHub may change the markup of without warning."""
    try:
        subprocess.run([sys.executable, ECG_PATH], check=True, cwd=ROOT_DIR)
    except Exception as exc:
        print(f"ECG rebuild failed ({exc}); leaving the existing card in place.")


if __name__ == "__main__":
    print(f"Fetching LeetCode stats for @{USERNAME}...")
    stats = fetch_leetcode_stats(USERNAME)
    if stats:
        print(f"Found: Total={stats['total']} (E={stats['easy']}, M={stats['medium']}, H={stats['hard']}), "
              f"Streak={stats['streak']}d, Rating={stats['rating']} (top {stats['top_pct']}%)")
        write_stats(stats)
        update_readme(stats)
        rebuild_assets()
        rebuild_ecg()
        print("Live sync completed successfully!")
    else:
        print("Failed to retrieve stats. Exiting.")
        sys.exit(1)
