"""Fetch normal (pre-discount) US prices from the Steam store API for a
random sample of paid games. Saves progress so it can resume if stopped."""

import json
import time
from pathlib import Path

import pandas as pd
import requests

CLEAN = Path("data/processed/steam_clean.parquet")
PROGRESS = Path("data/raw/steam_prices_sample.json")
OUT = Path("data/processed/steam_prices_sample.csv")
URL = "https://store.steampowered.com/api/appdetails"

SAMPLE_SIZE = 5000
SEED = 42      # fixed seed = the same random sample every time
DELAY = 1.6    # seconds between requests (stays under ~200 per 5 minutes)


def fetch_price(appid):
    entry = None
    for attempt in range(5):
        try:
            r = requests.get(URL, params={"appids": appid, "cc": "us",
                                          "filters": "price_overview"}, timeout=30)
            if r.status_code == 429:  # too many requests
                print("Rate limited, waiting 5 minutes...")
                time.sleep(300)
                continue
            r.raise_for_status()
            entry = r.json().get(str(appid), {})
            break
        except Exception as e:
            print(f"{appid}: attempt {attempt + 1} failed: {e}")
            time.sleep(30)

    if entry is None:
        return {"status": "error"}
    if not entry.get("success"):
        return {"status": "unavailable"}   # e.g. removed from the store
    data = entry.get("data")
    if not data or "price_overview" not in data:
        return {"status": "no_price"}
    p = data["price_overview"]
    return {
        "status": "ok",
        "currency": p.get("currency"),
        "initial_price": p.get("initial", 0) / 100,   # cents -> dollars
        "final_price": p.get("final", 0) / 100,
        "discount_percent": p.get("discount_percent"),
    }


def main():
    df = pd.read_parquet(CLEAN, columns=["appID", "is_free"])
    paid = df[~df["is_free"]]
    sample = paid.sample(n=SAMPLE_SIZE, random_state=SEED)["appID"].tolist()

    results = json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {}
    todo = [a for a in sample if str(a) not in results]
    print(f"{len(results)} already done, {len(todo)} to go")

    for i, appid in enumerate(todo, 1):
        results[str(appid)] = fetch_price(appid)
        if i % 50 == 0 or i == len(todo):
            PROGRESS.write_text(json.dumps(results))
            print(f"{len(results)}/{SAMPLE_SIZE} done")
        time.sleep(DELAY)

    out = pd.DataFrame.from_dict(results, orient="index")
    out.index.name = "appID"
    out.reset_index().to_csv(OUT, index=False)
    print(out["status"].value_counts())


if __name__ == "__main__":
    main()