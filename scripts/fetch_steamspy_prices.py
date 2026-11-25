"""Download every page of SteamSpy's 'all' endpoint to get each game's
normal (pre-discount) price. Saves progress after each page, so it can
be stopped and restarted without starting over."""

import json
import time
from pathlib import Path

import requests

OUT = Path("data/raw/steamspy_all.json")
URL = "https://steamspy.com/api.php"


def main():
    # resume from saved progress if it exists
    if OUT.exists():
        state = json.loads(OUT.read_text())
    else:
        state = {"next_page": 0, "games": {}}

    page = state["next_page"]
    while True:
        data = None
        for attempt in range(3):
            try:
                r = requests.get(URL, params={"request": "all", "page": page}, timeout=120)
                r.raise_for_status()
                data = r.json()
                break
            except Exception as e:
                print(f"Page {page}, attempt {attempt + 1} failed: {e}")
                time.sleep(60)

        if data is None:
            print(f"Stopped at page {page} after 3 failed attempts. Run again to resume.")
            break
        if not data:
            print(f"No more pages. Done: {len(state['games'])} games saved.")
            break

        state["games"].update(data)
        state["next_page"] = page + 1
        OUT.write_text(json.dumps(state))
        print(f"Page {page}: {len(data)} games (total so far: {len(state['games'])})")

        page += 1
        time.sleep(60)  # SteamSpy allows one 'all' request per 60 seconds


if __name__ == "__main__":
    main()