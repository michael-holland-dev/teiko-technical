import plotly.express as px
import streamlit as st

from dashboard.data import POPULATION_COLORS, POPULATION_ORDER, load_cell_frequencies, with_labels
from dashboard.grid import summary_table
from dashboard.style import caption, headline, label, lead, style_figure


def render() -> None:
    """Render the Cell Populations tab. Shows the filterable summary table and the sample
    composition chart.
    """
    freq = load_cell_frequencies()

    headline("Cell population frequencies per sample.", "section-headline")
    lead(
        "Each population's share of its sample's total cell count. Use the ⋮ menu on any "
        "column to sort or filter it; number filters accept several conditions, such as "
        "> 0 and < 10. Select samples below to compare their composition."
    )

    shown = summary_table(freq)
    caption(f"Showing {len(shown):,} of {len(freq):,} rows · {shown['sample'].nunique():,} samples")

    _composition_chart(freq)


def _composition_chart(freq) -> None:
    """Render a stacked bar chart of population shares for the selected samples. Draws nothing when
    no sample is selected.
    """
    all_samples = freq["sample"].unique().tolist()
    label("Sample composition")
    picked = st.multiselect(
        "Samples",
        all_samples,
        default=all_samples[:6],
        max_selections=30,
        placeholder="Choose samples",
        key="freq_samples",
    )
    if not picked:
        return

    comp = with_labels(freq[freq["sample"].isin(picked)])
    fig = px.bar(
        comp,
        x="percentage",
        y="sample",
        color="population",
        orientation="h",
        category_orders={"population": POPULATION_ORDER, "sample": picked},
        color_discrete_map=POPULATION_COLORS,
        hover_data={"count": ":,", "total_count": ":,", "percentage": ":.2f"},
        labels={
            "percentage": "Share of sample (%)",
            "sample": "",
            "population": "Population",
            "count": "Count",
            "total_count": "Total count",
        },
    )
    fig.update_traces(marker_line_width=1.5, marker_line_color="#ffffff")
    style_figure(fig, height=max(220, 34 * comp["sample"].nunique() + 80))
    fig.update_xaxes(range=[0, 100], ticksuffix="%")
    st.plotly_chart(fig, theme=None, config={"displayModeBar": False})
