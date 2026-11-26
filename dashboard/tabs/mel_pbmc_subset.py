from typing import Callable

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.data import (
    RESPONSE_LABELS,
    SEX_LABELS,
    UNKNOWN_LABEL,
    display_label,
    load_mel_pbmc_subset_counts,
    load_mel_pbmc_subset_samples,
    project_label,
)
from dashboard.grid import filter_table
from dashboard.style import RED, caption, headline, label, lead, stat_card, style_figure
from models.data import BASELINE_MEL_PBMC_SUBSET
from models.gold import Breakdown, Counted
from models.silver import NON_RESPONDER, RESPONDER

# Plural names for the composition card, e.g. "Responders: 331 patients".
CARD_RESPONSE_LABELS = {RESPONDER: "Responders", NON_RESPONDER: "Non-responders"}
UNIT_NAMES = {Counted.SAMPLES: "samples", Counted.SUBJECTS: "patients"}


def _project_name(category) -> str:
    """Display name for a project category. Missing values show as Unknown."""
    return UNKNOWN_LABEL if pd.isna(category) else project_label(category)


def render() -> None:
    """Render the Melanoma PBMC tab for the baseline subset. Shows the composition card, three
    breakdown charts and the sample table.
    """
    subset = BASELINE_MEL_PBMC_SUBSET.name
    counts = load_mel_pbmc_subset_counts(subset)
    samples = load_mel_pbmc_subset_samples(subset).drop(columns="subset")

    headline("Melanoma PBMC samples before treatment.", "section-headline")
    lead(
        "Melanoma patients treated with miraclib, PBMC samples taken at baseline "
        "(day 0 from treatment start)."
    )

    _composition_card(counts)

    c1, c2, c3 = st.columns(3)
    with c1:
        _breakdown_chart(counts, Breakdown.PROJECT, "Samples by project", _project_name)
    with c2:
        _breakdown_chart(
            counts, Breakdown.RESPONSE, "Patients by response",
            lambda c: display_label(c, RESPONSE_LABELS),
        )
    with c3:
        _breakdown_chart(
            counts, Breakdown.SEX, "Patients by sex", lambda c: display_label(c, SEX_LABELS)
        )
    caption("Project counts are samples. Response and sex counts are distinct patients.")

    _samples_table(samples)


def _rows(counts: pd.DataFrame, breakdown: Breakdown) -> pd.DataFrame:
    """Select one breakdown's rows, in table order."""
    return counts[counts["breakdown"] == breakdown.value]


def _total(counts: pd.DataFrame, counted: Counted) -> int:
    """Return the subset total for samples or subjects. Raises if the gold table doesn't have
    exactly one total row, so a pipeline problem isn't shown as a believable 0.
    """
    rows = _rows(counts, Breakdown.TOTAL)
    matches = rows.loc[rows["counted"] == counted.value, "count"]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one total {counted.value} row in gold_mel_pbmc_subset_counts, found {len(matches)}. "
            "Run `make pipeline` again."
        )
    return int(matches.iloc[0])


def _composition_card(counts: pd.DataFrame) -> None:
    """Render the card of baseline subset totals. Lists samples, patients, then every project,
    response and sex row in the gold table, including zeros and Unknown.
    """
    items = [
        ("Samples", f"{_total(counts, Counted.SAMPLES):,}", None, False),
        ("Patients", f"{_total(counts, Counted.SUBJECTS):,}", None, False),
    ]
    for breakdown, name in [
        (Breakdown.PROJECT, _project_name),
        (Breakdown.RESPONSE, lambda c: display_label(c, CARD_RESPONSE_LABELS)),
        (Breakdown.SEX, lambda c: display_label(c, SEX_LABELS)),
    ]:
        for row in _rows(counts, breakdown).to_dict("records"):
            unit = UNIT_NAMES[Counted(row["counted"])]
            items.append((name(row["category"]), f"{row['count']:,} {unit}", None, False))
    stat_card("Baseline melanoma PBMC composition.", items)


def _breakdown_chart(
    counts: pd.DataFrame, breakdown: Breakdown, title: str, relabel: Callable[[object], str]
) -> None:
    """Render a horizontal bar chart for one breakdown. Categories are relabeled for display, and
    an empty breakdown shows a note instead of a chart.
    """
    label(title)
    df = _rows(counts, breakdown).copy()
    if df.empty:
        caption("No data for this breakdown.")
        return
    df["category"] = df["category"].map(relabel)
    fig = px.bar(
        df,
        x="count",
        y="category",
        orientation="h",
        text="count",
        labels={"count": df["counted"].iloc[0].capitalize(), "category": ""},
        hover_data={"counted": False},
    )
    fig.update_traces(marker_color=RED, width=0.55, textposition="outside", cliponaxis=False)
    style_figure(fig, height=60 * len(df) + 70)
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(
        range=[0, max(df["count"].max(), 1) * 1.2],
        showticklabels=False,
        title=None,
        ticks="",
        linecolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, theme=None, config={"displayModeBar": False})


def _samples_table(samples: pd.DataFrame) -> None:
    """Render the subset's samples in the same filterable grid as the Cell Populations tab."""
    label("Melanoma PBMC samples")
    shown = filter_table(
        samples,
        key="mel_pbmc_subset_samples_table",
        text_columns=("sample", "subject", "project", "response", "sex"),
        number_columns=("age",),
    )
    caption(
        f"Showing {len(shown):,} of {len(samples):,} samples · "
        f"{shown['subject'].nunique():,} patients"
    )
