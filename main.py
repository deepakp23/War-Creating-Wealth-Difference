"""Scaffold for country-year observations of conflict and wealth inequality.

The frame defines where data belongs. It does not include measurements.
"""

from __future__ import annotations

import pandas as pd

# One row is one country in one year.
SCHEMA: dict[str, str] = {
    "country": "string",
    "iso3": "string",
    "year": "Int64",
    "in_conflict": "boolean",
    "conflict_name": "string",
    "gini_coefficient": "Float64",
    "top_1pct_wealth_share": "Float64",
    "bottom_50pct_wealth_share": "Float64",
    "mean_net_wealth_usd": "Float64",
    "median_net_wealth_usd": "Float64",
}


def create_dataset(records: list[dict] | None = None) -> pd.DataFrame:
    """Return a DataFrame that follows SCHEMA.

    Missing columns are added. Columns outside the schema are dropped.
    """
    frame = pd.DataFrame(records or [])
    for column, dtype in SCHEMA.items():
        if column not in frame.columns:
            frame[column] = pd.Series(dtype=dtype)
    frame = frame.loc[:, list(SCHEMA)].copy()
    for column, dtype in SCHEMA.items():
        frame[column] = frame[column].astype(dtype)
    return frame


def main() -> None:
    dataset = create_dataset()
    expected = list(SCHEMA)
    if list(dataset.columns) != expected:
        raise SystemExit(f"unexpected columns: {list(dataset.columns)}")
    if len(dataset) != 0:
        raise SystemExit(f"expected an empty scaffold, found {len(dataset)} rows")
    print(dataset.to_string(index=False))
    print()
    print(dataset.dtypes.to_string())
    print(f"\nrows={len(dataset)} columns={len(dataset.columns)}")


if __name__ == "__main__":
    main()
