"""Streamlit dashboard for war and wealth inequality."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

WEALTH_COLUMN = "Top 1% Wealth Share"
RETURN_COLUMN = "LMT_Return"


def mock_merged_frame() -> pd.DataFrame:
    """Build a stand-in annual table so the dashboard runs without source data."""
    years = np.arange(2000, 2027)
    rng = np.random.default_rng(11)
    wealth_share = 27.0 + np.cumsum(rng.normal(0.12, 0.35, size=years.size))
    lmt_return = rng.normal(14.0, 18.0, size=years.size)
    return pd.DataFrame(
        {
            "Year": years,
            WEALTH_COLUMN: wealth_share,
            RETURN_COLUMN: lmt_return,
        }
    )


def load_frame() -> pd.DataFrame:
    # Replace the mock frame with the merged inequality and LMT return table:
    # from merge_defense_returns import merge_inequality_with_returns
    # frame = merge_inequality_with_returns(inequality, lmt_prices)
    # frame = frame.rename(
    #     columns={
    #         "Share (top 1%, wealth)": "Top 1% Wealth Share",
    #         "Annual_Percentage_Return": "LMT_Return",
    #     }
    # )
    return mock_merged_frame()


def dual_axis_chart(frame: pd.DataFrame) -> go.Figure:
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_trace(
        go.Scatter(
            x=frame["Year"],
            y=frame[WEALTH_COLUMN],
            name=WEALTH_COLUMN,
            mode="lines",
            line={"color": "red"},
            hovertemplate=f"{WEALTH_COLUMN}: %{{y:.0f}}%<extra></extra>",
        ),
        secondary_y=False,
    )
    figure.add_trace(
        go.Scatter(
            x=frame["Year"],
            y=frame[RETURN_COLUMN],
            name=RETURN_COLUMN,
            mode="lines",
            line={"color": "blue"},
            hovertemplate=f"{RETURN_COLUMN}: $%{{y:.0f}}<extra></extra>",
        ),
        secondary_y=True,
    )
    figure.update_xaxes(title_text="Year")
    figure.update_yaxes(title_text=WEALTH_COLUMN, secondary_y=False, color="red")
    figure.update_yaxes(title_text=RETURN_COLUMN, secondary_y=True, color="blue")
    figure.update_layout(
        title="Top 1% wealth Share and Lockhead Martin Annual Return",
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
        margin={"t": 80},
    )
    return figure


def main() -> None:
    st.set_page_config(page_title="War and Wealth Inequality", layout="wide")
    st.title("War and Wealth Inequality")

    frame = load_frame()
    year_min = int(frame["Year"].min())
    year_max = int(frame["Year"].max())
    start_year, end_year = st.sidebar.slider(
        "Year range",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
    )
    selected = frame.loc[frame["Year"].between(start_year, end_year)].copy()
    st.plotly_chart(dual_axis_chart(selected), use_container_width=True)


if __name__ == "__main__":
    main()
