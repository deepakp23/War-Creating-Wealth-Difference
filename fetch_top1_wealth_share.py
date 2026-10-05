"""Fetch the FRED top 1% wealth share and reduce it to annual averages."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pandas_datareader.data as web

SERIES_ID = "WFRBST01134"
VALUE_COLUMN = "Top_1_Percent_Wealth_Share"


def fetch_top1_wealth_share(
    start: str = "2000-01-01",
    end: datetime | None = None,
) -> pd.DataFrame:
    """Return annual averages of the top 1% wealth share from FRED.

    ``WFRBST01134`` is the share of total net worth held by the top 1%.
    Observations from ``start`` through ``end`` are averaged within each year.
    """
    if end is None:
        end = datetime.now()

    frame = web.DataReader(SERIES_ID, "fred", start=start, end=end)
    frame.index = pd.to_datetime(frame.index)
    frame.index.name = "Date"
    frame = frame.rename(columns={SERIES_ID: VALUE_COLUMN})
    annual = frame.resample("YE").mean()
    annual.index.name = "Date"
    return annual


def main() -> None:
    annual = fetch_top1_wealth_share()
    if not isinstance(annual.index, pd.DatetimeIndex):
        raise SystemExit("index is not a datetime index")
    if list(annual.columns) != [VALUE_COLUMN]:
        raise SystemExit(f"unexpected columns: {list(annual.columns)}")
    if annual.empty or annual[VALUE_COLUMN].isna().all():
        raise SystemExit("FRED returned no wealth-share observations")
    print(annual.to_string(float_format=lambda value: f"{value:.4f}"))
    print(
        f"\nrows={len(annual)} "
        f"start={annual.index.min().date()} "
        f"end={annual.index.max().date()}"
    )


if __name__ == "__main__":
    main()
