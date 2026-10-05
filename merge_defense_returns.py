"""Attach annual defense-stock returns to yearly wealth-inequality data."""

from __future__ import annotations

import math

import pandas as pd

RETURN_COLUMN = "Annual_Percentage_Return"


def annual_percentage_return(
    stocks: pd.DataFrame,
    date_column: str = "Date",
    price_column: str = "Close",
) -> pd.DataFrame:
    """Return one percentage return for each calendar year.

    The return is the change from the first daily price in the year to the
    last, in percent: ``(last / first - 1) * 100``.
    """
    prices = stocks.loc[:, [date_column, price_column]].copy()
    prices[date_column] = pd.to_datetime(prices[date_column])
    prices[price_column] = pd.to_numeric(prices[price_column])
    prices = prices.dropna().sort_values(date_column, kind="stable")
    prices["Year"] = prices[date_column].dt.year.astype(int)

    annual = prices.groupby("Year", as_index=False)[price_column].agg(
        first_price="first",
        last_price="last",
    )
    annual[RETURN_COLUMN] = (annual["last_price"] / annual["first_price"] - 1.0) * 100.0
    return annual.loc[:, ["Year", RETURN_COLUMN]]


def merge_inequality_with_returns(
    inequality: pd.DataFrame,
    stocks: pd.DataFrame,
    date_column: str = "Date",
    price_column: str = "Close",
) -> pd.DataFrame:
    """Merge annual stock returns onto inequality rows by ``Year``.

    Inequality rows whose year has no stock prices stay in the result with a
    missing return. Every inequality row in a matched year receives that year's
    return.
    """
    if "Year" not in inequality.columns:
        raise ValueError("inequality dataframe must include a Year column")

    returns = annual_percentage_return(stocks, date_column, price_column)
    annual_inequality = inequality.copy()
    annual_inequality["Year"] = annual_inequality["Year"].astype(int)
    return annual_inequality.merge(returns, on="Year", how="left")


def main() -> None:
    inequality = pd.DataFrame(
        {
            "Entity": ["United States", "United States", "World", "World"],
            "Year": [2020, 2021, 2020, 2021],
            "Share (top 1%, wealth)": [30.7, 30.7, 35.1, 35.4],
        }
    )
    stocks = pd.DataFrame(
        {
            "Date": ["2020-12-31", "2020-01-02", "2020-06-01", "2021-12-31", "2021-01-04"],
            "Close": [120.0, 100.0, 105.0, 90.0, 120.0],
        }
    )

    merged = merge_inequality_with_returns(inequality, stocks)
    expected = {2020: 20.0, 2021: -25.0}
    for year, percentage in expected.items():
        actual = merged.loc[merged["Year"] == year, RETURN_COLUMN]
        if not actual.map(lambda value: math.isclose(value, percentage)).all():
            raise SystemExit(f"{year} return was {actual.tolist()}, expected {percentage}")
    if list(merged.columns) != [
        "Entity",
        "Year",
        "Share (top 1%, wealth)",
        RETURN_COLUMN,
    ]:
        raise SystemExit(f"unexpected columns: {list(merged.columns)}")

    print(merged.to_string(index=False, float_format=lambda value: f"{value:.1f}"))


if __name__ == "__main__":
    main()
