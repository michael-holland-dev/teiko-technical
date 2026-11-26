from html import escape
from typing import Iterable, Optional, Tuple

import streamlit as st

RED = "#FF3534"
RED_DARK = "#c92a29"
INK = "#111110"
INK_2 = "#3a3a38"
INK_3 = "#6e6e6a"
INK_4 = "#9f9f9b"
BORDER = "rgba(0, 0, 0, 0.1)"
BORDER_MID = "rgba(0, 0, 0, 0.18)"
MUTED = INK_3
GRID = "rgba(0, 0, 0, 0.07)"
FONT = "Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, .stApp, .stApp p, .stApp li, .stApp label, .stApp input,
.stApp button, .stMarkdown, [data-testid="stMetric"] {{
  font-family: {FONT};
}}
.stApp {{ color: {INK}; }}
header[data-testid="stHeader"], #MainMenu, footer {{ display: none; }}
.block-container {{ padding-top: 3rem; max-width: 1240px; }}

.page-header {{ margin-bottom: 1.35rem; }}
.page-title {{
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 0.3em;
  font-family: {FONT};
  font-weight: 700;
  font-size: clamp(2.16rem, 4.32vw, 3.36rem);  line-height: 1;
  letter-spacing: -0.03em;
  color: {RED};
}}
.page-title svg {{ height: 0.79em; width: auto; display: block; }}.page-byline {{ margin-top: 1.375rem; font-size: 1.05rem; color: {INK_3}; text-align: left; }}
.page-byline strong {{ color: inherit; font-weight: inherit; }}

.eyebrow {{
  display: inline-block;
  padding: 0.45rem 0.9rem;
  border: 1px solid rgba(255, 53, 52, 0.35);
  background: rgba(255, 53, 52, 0.08);
  color: {RED};
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin-bottom: 1.1rem;
}}

.headline {{
  font-family: {FONT};
  font-weight: 700;
  font-size: clamp(2rem, 4.2vw, 3.4rem);
  line-height: 1.06;
  letter-spacing: -0.035em;
  color: {INK};
  margin: 0 0 1rem 0;
  text-wrap: balance;
}}
.section-headline {{
  font-family: {FONT};
  font-weight: 700;
  font-size: clamp(1.6rem, 3vw, 2.3rem);
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: {INK};
  margin: 0.2rem 0 0.7rem 0;
  text-wrap: balance;
}}
.lead {{
  font-size: 1.2rem;
  line-height: 1.6;
  color: {INK_2};
  font-weight: 400;
  max-width: 62rem;
  margin-bottom: 1.8rem;
}}
.label {{
  font-size: 0.9rem;
  font-weight: 600;
  color: {INK_2};
  margin: 1.4rem 0 0.4rem 0;
}}
.caption {{ color: {MUTED}; font-size: 0.88rem; }}

.card {{
  background: #f9f9f8;
  border: 1px solid {BORDER};
  border-radius: 16px;
  padding: 0.4rem 1.6rem;
  margin: 0.4rem 0 1.4rem 0;
}}
.card-title {{
  padding: 1rem 0;
  border-bottom: 1px solid {BORDER};
  font-size: 1.02rem;
  color: {INK};
}}
.card-row {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  padding: 0.95rem 0;
  border-bottom: 1px solid {BORDER};
  font-size: 1rem;
}}
.card-row:last-child {{ border-bottom: none; }}
.card-value {{ font-variant-numeric: tabular-nums; color: {INK}; white-space: nowrap; }}
.card-note {{ color: {MUTED}; margin-left: 0.9rem; }}
.card-value.accent {{ color: {RED}; font-weight: 600; }}

.stTabs [role="tablist"] {{ gap: 0.75rem; border-bottom: none; flex-wrap: wrap; box-shadow: none; }}
.stTabs [role="tablist"]::after, .stTabs .react-aria-SelectionIndicator {{ display: none !important; }}
.stTabs [data-testid="stTab"] {{
  height: auto !important;
  padding: 0.8rem 1.4rem !important;
  border: 1px solid {BORDER_MID} !important;
  border-radius: 8px !important;
  background: #ffffff;
}}
.stTabs [data-testid="stTab"] p {{ font-size: 1.05rem !important; color: {INK}; margin: 0; }}
.stTabs [data-testid="stTab"][aria-selected="true"] {{ background: {RED}; border-color: {RED} !important; }}
.stTabs [data-testid="stTab"][aria-selected="true"] p {{ color: #ffffff; }}
.stTabs [data-testid="stTab"][aria-selected="true"]:hover {{ background: {RED_DARK}; border-color: {RED_DARK}; }}
.stTabs [data-testid="stTabPanel"] {{ padding-top: 2rem; }}

[data-testid="stBaseButton-segmented_control"] {{
  background: #ffffff; border: 1px solid {BORDER_MID}; color: {INK};
}}
[data-testid="stBaseButton-segmented_controlActive"] {{
  background: {RED}; border-color: {RED}; color: #ffffff;
}}
[data-testid="stBaseButton-segmented_controlActive"] p {{ color: #ffffff; }}

.stDownloadButton button {{ border-radius: 8px; border: 1px solid {BORDER_MID}; color: {INK}; }}
.stDownloadButton button:hover {{ border-color: {RED}; color: {RED}; }}
.stTabs [aria-selected="true"]:hover {{ background: {RED_DARK}; border-color: {RED_DARK}; }}
[data-testid="stBaseButton-segmented_controlActive"]:hover {{ background: {RED_DARK}; border-color: {RED_DARK}; }}
</style>
"""


def apply_style() -> None:
    """Inject the brand CSS into the page. Call once, right after st.set_page_config."""
    st.markdown(CSS, unsafe_allow_html=True)


def eyebrow(text: str) -> None:
    """Render a small red pill label. Used above headlines."""
    st.markdown(f'<span class="eyebrow">{escape(text)}</span>', unsafe_allow_html=True)


def headline(text: str, level: str = "headline") -> None:
    """Render a large bold headline. The level picks the page or section size."""
    st.markdown(f'<div class="{level}">{escape(text)}</div>', unsafe_allow_html=True)


def lead(text: str) -> None:
    """Render an introductory paragraph. Text is escaped before display."""
    st.markdown(f'<div class="lead">{escape(text)}</div>', unsafe_allow_html=True)


def label(text: str) -> None:
    """Render a small bold label above a chart or table. Text is escaped before display."""
    st.markdown(f'<div class="label">{escape(text)}</div>', unsafe_allow_html=True)


def page_header(title: str, byline_label: str, byline_name: str, logo_svg: str) -> None:
    """Render the logo and title on one line with a byline below. The logo is passed in as inline
    SVG.
    """
    st.markdown(
        f'<div class="page-header"><div class="page-title">{logo_svg}'
        f'<span>{escape(title)}</span></div>'
        f'<div class="page-byline">{escape(byline_label)} <strong>{escape(byline_name)}</strong></div></div>',
        unsafe_allow_html=True,
    )


def caption(text: str) -> None:
    """Render a small muted note. Text is escaped before display."""
    st.markdown(f'<div class="caption">{escape(text)}</div>', unsafe_allow_html=True)


def stat_card(title: str, rows: Iterable[Tuple[str, str, Optional[str], bool]]) -> None:
    """Render a card with a title row and label/value rows split by hairlines. Each row can carry a
    muted note and a red accent.
    """
    body = "".join(
        f'<div class="card-row"><span>{escape(lbl)}</span><span>'
        f'<span class="card-value{" accent" if accent else ""}">{escape(value)}</span>'
        + (f'<span class="card-note">{escape(note)}</span>' if note else "")
        + "</span></div>"
        for lbl, value, note, accent in rows
    )
    st.markdown(
        f'<div class="card"><div class="card-title">{escape(title)}</div>{body}</div>',
        unsafe_allow_html=True,
    )


def style_figure(fig, height: int = 420):
    """Apply the brand fonts, colors and gridlines to a Plotly figure. Returns the same figure for
    chaining.
    """
    fig.update_layout(
        height=height,
        template="none",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=13, color=INK),
        margin=dict(l=8, r=8, t=8, b=8),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None),
        hoverlabel=dict(font_family=FONT, font_size=13, bgcolor="#ffffff", bordercolor=INK_4),
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER_MID, tickcolor=BORDER_MID, ticks="outside", automargin=True)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor="rgba(0,0,0,0)", automargin=True)
    return fig
