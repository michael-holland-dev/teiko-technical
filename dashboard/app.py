import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

ASSETS = Path(__file__).parent / "assets"

st.set_page_config(
    page_title="Michael H. Assessment",
    page_icon=str(ASSETS / "logo.svg"),
    layout="wide",
    initial_sidebar_state="collapsed",
)

from dashboard.data import gold_ready
from dashboard.style import apply_style, page_header
from dashboard.tabs import TABS

apply_style()

if not gold_ready():
    st.error("Results are not available yet. Run `make pipeline`, then reload this page.")
    st.stop()

logo_svg = (ASSETS / "logo_work.svg").read_text()
logo_svg = logo_svg[logo_svg.index("<svg"):]
page_header("Technical Assessment", "By", "Michael Holland", logo_svg)

for tab, render in zip(st.tabs(list(TABS)), TABS.values()):
    with tab:
        render()
