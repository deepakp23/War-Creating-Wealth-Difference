"""Streamlit dashboard for war and wealth inequality."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

WEALTH_COLUMN = "Top 1% Wealth Share"
RETURN_COLUMN = "LMT_Return"
WAR_PERIODS = [
    {"name": "Gulf War", "start": 1990, "end": 1991, "color": "rgba(255, 165, 0, 0.2)"},
    {"name": "War in Afghanistan", "start": 2001, "end": 2021, "color": "rgba(255, 0, 0, 0.12)"},
    {"name": "Iraq War", "start": 2003, "end": 2011, "color": "rgba(255, 99, 71, 0.2)"},
    {"name": "Russo-Ukrainian War", "start": 2022, "end": 2023, "color": "rgba(135, 206, 250, 0.25)"},
    {"name": "US-Iran Conflict", "start": 2026, "end": 2026, "color": "rgba(128, 0, 128, 0.25)"},
]


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


def visible_conflict_span(
    war: dict,
    start_year: int,
    end_year: int,
) -> tuple[int, int] | None:
    """Return the shaded year span that overlaps the slider, inclusive of the end year."""
    x0 = max(int(war["start"]), int(start_year))
    x1 = min(int(war["end"]) + 1, int(end_year) + 1)
    if x0 >= x1:
        return None
    return x0, x1


def add_conflict_regions(
    figure: go.Figure,
    start_year: int,
    end_year: int,
) -> None:
    """Shade wars that overlap the selected years and label each band."""
    label_offsets: dict[int, int] = {}
    for war in WAR_PERIODS:
        span = visible_conflict_span(war, start_year, end_year)
        if span is None:
            continue
        x0, x1 = span
        yshift = -label_offsets.get(x0, 0)
        label_offsets[x0] = label_offsets.get(x0, 0) + 16
        figure.add_vrect(
            x0=x0,
            x1=x1,
            fillcolor=war["color"],
            opacity=1,
            layer="below",
            line_width=0,
            annotation_text=war["name"],
            annotation_position="top left",
            annotation_font_size=12,
            annotation_yshift=yshift,
        )


def dual_axis_chart(
    frame: pd.DataFrame,
    highlight_conflicts: bool = False,
    start_year: int | None = None,
    end_year: int | None = None,
) -> go.Figure:
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
    if highlight_conflicts:
        if start_year is None:
            start_year = int(frame["Year"].min())
        if end_year is None:
            end_year = int(frame["Year"].max())
        add_conflict_regions(figure, start_year, end_year)
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
    highlight_conflicts = st.sidebar.checkbox("Highlight Major Conflicts", value=True)
    selected = frame.loc[frame["Year"].between(start_year, end_year)].copy()
    st.plotly_chart(
        dual_axis_chart(selected, highlight_conflicts, start_year, end_year),
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
