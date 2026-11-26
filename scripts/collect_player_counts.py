"""Record current Steam player counts for the tracked games.
Designed to run hourly via GitHub Actions. Appends to a history file and
writes a 'latest' snapshot for the website."""

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
TRACKED = ROOT / "data/live/tracked_games.csv"
HISTORY = ROOT / "data/live/player_counts.csv"
LATEST = ROOT / "data/live/latest.json"
LATEST_SITE = ROOT / "docs/data/latest.json"
URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"


def get_players(appid):
    for attempt in range(3):
        try:
            r = requests.get(URL, params={"appid": appid}, timeout=20)
            if r.status_code == 200:
                data = r.json().get("response", {})
                return data.get("player_count") if data.get("result") == 1 else None
        except requests.RequestException:
            pass
        time.sleep(2)
    return None


def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(TRACKED, newline="", encoding="utf-8") as f:
        games = list(csv.DictReader(f))

    rows = []
    for g in games:
        rows.append({"timestamp_utc": timestamp, "appID": g["appID"],
                     "name": g["name"], "players": get_players(g["appID"])})
        time.sleep(0.5)

    new_file = not HISTORY.exists()
    with open(HISTORY, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp_utc", "appID", "name", "players"])
        if new_file:
            writer.writeheader()
        writer.writerows(rows)

    ok = [r for r in rows if r["players"] is not None]
    ok.sort(key=lambda r: r["players"], reverse=True)
    snapshot = json.dumps({"updated_utc": timestamp, "games": ok}, indent=2)
    LATEST.write_text(snapshot)
    LATEST_SITE.write_text(snapshot)
    print(f"{timestamp}: recorded {len(ok)}/{len(rows)} games")


if __name__ == "__main__":
    main()