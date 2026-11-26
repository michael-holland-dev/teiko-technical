from typing import List

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.data import (
    POPULATION_LABELS,
    POPULATION_ORDER,
    RESPONSE_COLORS,
    RESPONSE_LABELS,
    format_p,
    load_population_comparisons,
    load_population_comparisons_by_timepoint,
    load_responder_frequencies,
    with_labels,
)
from dashboard.style import headline, label, lead, stat_card, style_figure

UNITS = {"Per patient": "subject", "Per sample": "sample"}
CORRECTIONS = {"Benjamini-Hochberg": "fdr_bh", "Bonferroni": "bonferroni", "None": "none"}
CORRECTION_NAMES = {"fdr_bh": "Benjamini-Hochberg correction", "bonferroni": "Bonferroni correction", "none": "no correction"}

def render() -> None:
    """Render the Treatment Response tab. Shows the headline, verdict, boxplot, statistics and
    timepoint tables.
    """
    header = st.container()
    unit, correction = _controls()

    stats = with_labels(load_population_comparisons(unit, correction))
    by_day = with_labels(load_population_comparisons_by_timepoint(correction))
    resp = with_labels(load_responder_frequencies(unit)).assign(
        response=lambda d: d["response"].map(RESPONSE_LABELS)
    )

    with header:
        _headline(stats, unit)
    _verdict(stats, by_day, correction)
    _boxplot(resp)
    _stats_table(stats)
    _timepoint_table(by_day)


def _choice(title: str, options: dict, key: str, help_text: str, default: str = None) -> str:
    """Render a segmented control and return the value for the selected option. Falls back to the
    default when nothing is selected.
    """
    default = default or list(options)[0]
    picked = st.segmented_control(title, list(options), default=default, key=key, help=help_text)
    return options[picked or default]


def _controls():
    """Render the unit of analysis and correction controls. Returns the selected unit and
    correction.
    """
    c1, c2 = st.columns(2)
    with c1:
        unit = _choice(
            "Unit of analysis",
            UNITS,
            "resp_unit",
            "Per patient averages each patient's samples so every patient counts once. "
            "Per sample treats every sample as independent.",
        )
    with c2:
        correction = _choice(
            "Multiple-testing correction",
            CORRECTIONS,
            "resp_correction",
            "Adjusts p-values for testing five populations at once.",
            default="None",
        )
    return unit, correction


def _significant(df: pd.DataFrame) -> pd.DataFrame:
    """Return the populations that are significant after correction. Sorted by adjusted p-value."""
    return df[df["significant"].astype(bool)].sort_values("adjusted_p_value")


def _nominal_only(df: pd.DataFrame) -> pd.DataFrame:
    """Return the populations with raw p below alpha that are not significant after correction.
    Sorted by raw p-value.
    """
    alpha = float(df["alpha"].iloc[0])
    return df[(df["p_value"] < alpha) & ~df["significant"].astype(bool)].sort_values("p_value")


def _names(df: pd.DataFrame) -> str:
    """Join population names into a comma-separated list. Returns 'none' for an empty table."""
    return ", ".join(df["population"]) if len(df) else "none"


def _headline(stats: pd.DataFrame, unit: str) -> None:
    """Render the headline finding and the sample description. The headline names the top
    significant population, or the strongest signal.
    """
    alpha = float(stats["alpha"].iloc[0])
    n_resp = int(stats["n_responders"].iloc[0])
    n_non = int(stats["n_non_responders"].iloc[0])
    noun = "patients" if unit == "subject" else "samples"
    sig = _significant(stats)

    if len(sig):
        top = sig.iloc[0]
        direction = "higher" if top["median_difference"] > 0 else "lower"
        others = len(sig) - 1
        headline(
            f"{top['population']} are {direction} in responders"
            + (f", with {others} other population{'s' if others > 1 else ''}." if others else "."),
            "section-headline",
        )
    else:
        strongest = stats.loc[stats["p_value"].idxmin()]
        direction = "higher" if strongest["median_difference"] > 0 else "lower"
        headline(
            f"{strongest['population']} show the strongest signal, {direction} in responders.",
            "section-headline",
        )
    lead(
        f"Melanoma patients treated with miraclib, PBMC samples: {n_resp:,} responder and "
        f"{n_non:,} non-responder {noun}. Each population is compared with a two-sided "
        f"Mann-Whitney U test at α = {alpha:g}."
    )


def _evidence(r) -> str:
    """Summarize one population's statistics in a single line. Includes medians, difference, effect
    size and both p-values.
    """
    return (
        f"median {r.responder_median:.2f}% vs {r.non_responder_median:.2f}% "
        f"({r.median_difference:+.2f} pts), r = {r.effect_size:+.2f}, "
        f"p = {format_p(r.p_value)}, adjusted p = {format_p(r.adjusted_p_value)}"
    )


def _verdict(stats: pd.DataFrame, by_day: pd.DataFrame, correction: str) -> None:
    """Render the per-population card and the written conclusion. States what is significant, what
    is nominal and what it means.
    """
    alpha = float(stats["alpha"].iloc[0])
    sig, nominal = _significant(stats), _nominal_only(stats)
    correction_name = CORRECTION_NAMES[correction]

    stat_card(
        f"Responders vs non-responders by population, adjusted p-value ({correction_name}).",
        [
            (
                r.population,
                f"p = {format_p(r.adjusted_p_value)}",
                f"(n = {r.n_responders} vs {r.n_non_responders} · median {r.median_difference:+.2f} pts"
                f" · r = {r.effect_size:+.2f} · raw p = {format_p(r.p_value)})",
                bool(r.significant),
            )
            for r in stats.itertuples()
        ],
    )

    label("Conclusion")
    lines: List[str] = []
    if len(sig):
        lines.append(
            f"**Significant at α = {alpha:g} after {correction_name}:** "
            + "; ".join(f"**{r.population}** ({_evidence(r)})" for r in sig.itertuples())
            + "."
        )
    else:
        lines.append(f"**Significant at α = {alpha:g} after {correction_name}:** none.")
    if correction != "none":
        if len(nominal):
            lines.append(
                "**Nominal signal only (raw p < α, not significant after correction):** "
                + "; ".join(f"**{r.population}** ({_evidence(r)})" for r in nominal.itertuples())
                + "."
            )
        else:
            lines.append("**Nominal signal only (raw p < α, not significant after correction):** none.")

    abs_r = stats["effect_size"].abs()
    abs_diff = stats["median_difference"].abs()
    lines.append(
        f"**What it means for predicting response:** effect sizes are small "
        f"(|r| = {abs_r.min():.2f}–{abs_r.max():.2f}) and responder and non-responder medians differ "
        f"by at most {abs_diff.max():.2f} percentage points. The two groups' distributions overlap "
        f"almost completely, so no single population's relative frequency separates responders "
        f"from non-responders well enough to predict response on its own."
    )
    lines.append(f"**By timepoint:** {_timepoint_summary(by_day, correction)}")
    st.markdown("\n\n".join(lines))


def _timepoint_summary(by_day: pd.DataFrame, correction: str) -> str:
    """Describe the results at each timepoint in a sentence. Notes whether baseline differs from
    later timepoints.
    """
    parts = []
    for day, df in by_day.groupby("timepoint", sort=True):
        sig, nominal = _significant(df), _nominal_only(df)
        when = "baseline (day 0)" if day == 0 else f"day {int(day)}"
        if len(sig):
            parts.append(f"at {when}, {_names(sig)} are significant")
        elif len(nominal) and correction != "none":
            parts.append(
                f"at {when}, nothing is significant after correction; only {_names(nominal)} "
                f"show a nominal signal "
                f"(p = {', '.join(format_p(p) for p in nominal['p_value'])})"
            )
        else:
            parts.append(f"at {when}, no population differs")
    def flagged(day):
        df = by_day[by_day["timepoint"] == day]
        return set(_significant(df)["population"]) | set(_nominal_only(df)["population"])

    text = "; ".join(parts) + "."
    later = [flagged(day) for day in sorted(by_day["timepoint"].unique()) if day != 0]
    if not flagged(0) and any(later):
        consistent = len(later) > 1 and all(f == later[0] for f in later)
        text += (
            " Responders and non-responders look alike before treatment; any signal appears only "
            "after treatment starts"
            + ("." if consistent else " and points to different populations on different days.")
            + " That doesn't change the takeaway: no population is a reliable predictor on its own."
        )
    elif not flagged(0):
        text += " Responders and non-responders look alike at every timepoint."
    return text[0].upper() + text[1:]


def _boxplot(resp: pd.DataFrame) -> None:
    """Render boxplots of relative frequency by response for each population. Outliers are shown as
    points.
    """
    label("Relative frequency by response")
    fig = px.box(
        resp,
        x="population",
        y="percentage",
        color="response",
        category_orders={"population": POPULATION_ORDER, "response": list(RESPONSE_COLORS)},
        color_discrete_map=RESPONSE_COLORS,
        points="outliers",
        labels={"percentage": "Relative frequency (%)", "population": "", "response": ""},
    )
    fig.update_traces(line_width=2, marker=dict(size=4, opacity=0.6))
    style_figure(fig, height=460)
    fig.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig, theme=None, config={"displayModeBar": False})


def _stats_table(stats: pd.DataFrame) -> None:
    """Render the full statistics table. One row per population with sizes, medians, effect size
    and p-values.
    """
    alpha = float(stats["alpha"].iloc[0])
    label("Statistical comparison")
    table = stats[
        [
            "population",
            "n_responders",
            "n_non_responders",
            "responder_median",
            "non_responder_median",
            "median_difference",
            "effect_size",
            "p_value",
            "adjusted_p_value",
            "significant",
        ]
    ].assign(significant=lambda d: d["significant"].astype(bool).map({True: "Yes", False: "No"}))
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={
            "population": st.column_config.TextColumn("Population"),
            "n_responders": st.column_config.NumberColumn("n responders", format="%d"),
            "n_non_responders": st.column_config.NumberColumn("n non-responders", format="%d"),
            "responder_median": st.column_config.NumberColumn("Responder median", format="%.2f%%"),
            "non_responder_median": st.column_config.NumberColumn("Non-responder median", format="%.2f%%"),
            "median_difference": st.column_config.NumberColumn(
                "Difference", format="%+.2f pts", help="Responder median minus non-responder median"
            ),
            "effect_size": st.column_config.NumberColumn(
                "Effect size (r)",
                format="%+.3f",
                help="Rank-biserial correlation from -1 to 1. Positive values mean responders tend to be higher.",
            ),
            "p_value": st.column_config.NumberColumn("p-value", format="%.4f"),
            "adjusted_p_value": st.column_config.NumberColumn("Adjusted p-value", format="%.4f"),
            "significant": st.column_config.TextColumn(f"Significant (α = {alpha:g})"),
        },
    )


def _timepoint_table(by_day: pd.DataFrame) -> None:
    """Render raw and adjusted p-values by population for each timepoint. Significant cells are
    marked with an asterisk.
    """
    label("By timepoint · p-value (adjusted p-value), one sample per patient")
    cells = by_day.assign(
        value=lambda d: [
            f"{format_p(p)} ({format_p(q)})" + (" *" if s else "")
            for p, q, s in zip(d["p_value"], d["adjusted_p_value"], d["significant"].astype(bool))
        ],
        day=lambda d: d["timepoint"].map(lambda t: "Day 0 (baseline)" if t == 0 else f"Day {int(t)}"),
    )
    day_order = list(dict.fromkeys(cells.sort_values("timepoint")["day"]))
    table = cells.pivot(index="population", columns="day", values="value").reindex(
        index=[POPULATION_LABELS[p] for p in POPULATION_LABELS], columns=day_order
    )
    st.dataframe(table.rename_axis("Population").reset_index(), hide_index=True, width="stretch")
