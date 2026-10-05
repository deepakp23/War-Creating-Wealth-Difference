"""Read the OWID top 1% wealth share for the United States and the World."""

from __future__ import annotations

import urllib.request

import pandas as pd

OWID_URL = (
    "https://ourworldindata.org/grapher/wealth-share-richest.csv"
    "?v=1&csvType=full&useColumnShortNames=false&quantile=richest_1pct"
)
VALUE_COLUMN = "Share (top 1%, wealth)"
KEEP_COLUMNS = ["Entity", "Year", VALUE_COLUMN]
ENTITIES = ("United States", "World")


def load_us_and_world(url: str = OWID_URL) -> pd.DataFrame:
    """Return Entity, Year, and the top 1% wealth share for two series.

    Our World in Data rejects the default download client, so this installs
    a browser user agent before ``pandas.read_csv`` requests the URL.
    The World rows are the chart's World series.
    """
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)

    frame = pd.read_csv(url)
    missing = [column for column in KEEP_COLUMNS if column not in frame.columns]
    if missing:
        raise SystemExit(f"CSV is missing columns: {missing}")

    selected = frame.loc[frame["Entity"].isin(ENTITIES), KEEP_COLUMNS].copy()
    selected = selected.sort_values(["Entity", "Year"], kind="stable")
    return selected.reset_index(drop=True)


def main() -> None:
    selected = load_us_and_world()
    if list(selected.columns) != KEEP_COLUMNS:
        raise SystemExit(f"unexpected columns: {list(selected.columns)}")
    present = set(selected["Entity"])
    missing_entities = [entity for entity in ENTITIES if entity not in present]
    if missing_entities:
        raise SystemExit(f"missing entities: {missing_entities}")
    print(selected.to_string(index=False))
    print()
    for entity in ENTITIES:
        rows = selected.loc[selected["Entity"] == entity]
        print(
            f"{entity}: rows={len(rows)} "
            f"years={int(rows['Year'].min())}-{int(rows['Year'].max())}"
        )


if __name__ == "__main__":
    main()
