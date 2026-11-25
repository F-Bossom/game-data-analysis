"""Fetch every IGDB game that is on at least one Nintendo, PlayStation or Xbox
platform and has a critic rating. Saves raw results to data/raw."""

import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

OUT = ROOT / "data/raw/igdb_console_games.json"
URL = "https://api.igdb.com/v4/games"

# console platform IDs from IGDB's platform list (add-ons and services excluded)
NINTENDO = [307, 18, 99, 33, 19, 58, 87, 22, 4, 24, 21, 20, 159, 5, 41, 137, 37, 130, 508, 166]
PLAYSTATION = [7, 8, 9, 38, 165, 48, 46, 167, 390]
XBOX = [11, 12, 49, 169]
CONSOLE_IDS = NINTENDO + PLAYSTATION + XBOX

FIELDS = ("name, first_release_date, aggregated_rating, aggregated_rating_count, "
          "rating, rating_count, platforms, game_type.type, franchise.name, franchises.name, "
          "involved_companies.company.name, involved_companies.developer, "
          "involved_companies.publisher")


def get_token():
    r = requests.post("https://id.twitch.tv/oauth2/token", params={
        "client_id": os.environ["TWITCH_CLIENT_ID"],
        "client_secret": os.environ["TWITCH_CLIENT_SECRET"],
        "grant_type": "client_credentials",
    }, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


def main():
    headers = {"Client-ID": os.environ["TWITCH_CLIENT_ID"],
               "Authorization": f"Bearer {get_token()}"}
    ids = ",".join(map(str, CONSOLE_IDS))

    games, last_id = [], 0
    while True:
        body = (f"fields {FIELDS}; "
                f"where platforms = ({ids}) & aggregated_rating != null & id > {last_id}; "
                f"sort id asc; limit 500;")
        r = requests.post(URL, headers=headers, data=body, timeout=60)
        if r.status_code == 429:  # too many requests: pause and retry
            time.sleep(5)
            continue
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        games.extend(batch)
        last_id = batch[-1]["id"]
        print(f"{len(games)} games so far")
        time.sleep(0.3)  # stay under 4 requests per second

    OUT.write_text(json.dumps(games))
    print(f"Done: {len(games)} games saved to {OUT}")


if __name__ == "__main__":
    main()