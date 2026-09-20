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
    }
    """
    req = urllib.request.Request(
        url,
        data=json.dumps({"query": query, "variables": {"username": username}}).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=10).read().decode("utf-8"))
        matched = res.get("data", {}).get("matchedUser", {})
        if not matched:
            print(f"User {username} not found on LeetCode")
            return None

        diffs = {item["difficulty"]: item["count"] for item in matched["submitStatsGlobal"]["acSubmissionNum"]}
        streak = matched.get("userCalendar", {}).get("streak", 0)
        active_days = matched.get("userCalendar", {}).get("totalActiveDays", 0)

        return {
            "total": diffs.get("All", 0),
            "easy": diffs.get("Easy", 0),
            "medium": diffs.get("Medium", 0),
            "hard": diffs.get("Hard", 0),
            "streak": streak,
            "active_days": active_days
        }
    except Exception as e:
        print(f"Error querying LeetCode GraphQL: {e}")
        return None


def update_build_assets(stats):
    with open(BUILD_ASSETS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Update easy, med, hard in dsa()
    content = re.sub(
        r'easy, med, hard = \d+, \d+, \d+',
        f'easy, med, hard = {stats["easy"]}, {stats["medium"]}, {stats["hard"]}',
        content
    )

    # Update streak text in dsa()
    content = re.sub(
        r'🔥 \d+-Day Continuous',
        f'🔥 {stats["streak"]}-Day Continuous',
        content
    )

    # Update CARDS line
    content = re.sub(
        r'"\d+ problems, \d+-day streak, Level 17"',
        f'"{stats["total"]} problems, {stats["streak"]}-day streak, Level 17"',
        content
    )

    # Update hero role line
    content = re.sub(
        r'"Level 17 Algorithm Grandmaster · \d+ Solved · \d+d Streak 🔥"',
        f'"Level 17 Algorithm Grandmaster · {stats["total"]} Solved · {stats["streak"]}d Streak 🔥"',
        content
    )

    with open(BUILD_ASSETS_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("Updated build_assets.py with live statistics.")


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


if __name__ == "__main__":
    print(f"Fetching LeetCode stats for @{USERNAME}...")
    stats = fetch_leetcode_stats(USERNAME)
    if stats:
        print(f"Found: Total={stats['total']} (E={stats['easy']}, M={stats['medium']}, H={stats['hard']}), Streak={stats['streak']}d")
        update_build_assets(stats)
        update_readme(stats)
        rebuild_assets()
        print("Live sync completed successfully!")
    else:
        print("Failed to retrieve stats. Exiting.")
        sys.exit(1)
