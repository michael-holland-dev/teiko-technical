import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from dashboard.style import INK_2, INK_3, RED
from lib.database import DB_PATH, get_engine, has_layer
from models.gold import GoldBase
from models.silver import FEMALE, MALE, NON_RESPONDER, POPULATIONS, RESPONDER
from repos import GoldRepo, Unit

POPULATION_LABELS = {
    "b_cell": "B cells",
    "cd8_t_cell": "CD8⁺ T cells",
    "cd4_t_cell": "CD4⁺ T cells",
    "nk_cell": "NK cells",
    "monocyte": "Monocytes",
}
POPULATION_ORDER = [POPULATION_LABELS[p] for p in POPULATIONS]

POPULATION_COLORS = dict(zip(POPULATION_ORDER, [RED, "#2a78d6", "#1baf7a", "#eda100", INK_2]))
RESPONSE_LABELS = {RESPONDER: "Responder", NON_RESPONDER: "Non-responder"}
SEX_LABELS = {MALE: "Male", FEMALE: "Female"}
UNKNOWN_LABEL = "Unknown"
RESPONSE_COLORS = {"Responder": RED, "Non-responder": INK_3}


def project_label(project_id: str) -> str:
    """Turn a project id such as prj1 into a display name such as Project 1. Ids that don't
    follow the prjN pattern are shown as they are.
    """
    suffix = project_id[3:] if project_id.startswith("prj") else ""
    return f"Project {suffix}" if suffix.isdigit() else project_id


def display_label(category, labels=None) -> str:
    """Turn a stored category into a display name. Missing values show as Unknown, and values
    with no entry in labels are shown as they are.
    """
    if category is None or pd.isna(category):
        return UNKNOWN_LABEL
    return (labels or {}).get(category, category)


@st.cache_resource
def gold_engine():
    """Create the SQLAlchemy engine for cell_counts.db. Cached so every rerun reuses one engine."""
    return get_engine(DB_PATH)


def gold_ready() -> bool:
    """Check whether the gold tables exist yet. Returns False until `make pipeline` has run."""
    return DB_PATH.exists() and has_layer(gold_engine(), GoldBase.metadata)


def _gold(query) -> pd.DataFrame:
    """Run one GoldRepo query in a fresh session and return its DataFrame."""
    with Session(gold_engine()) as session:
        return query(GoldRepo(session))


# One cached loader per gold query. Typed functions (rather than a method name passed as a
# string) let the IDE and type checker catch typos and renames.


@st.cache_data
def load_cell_frequencies() -> pd.DataFrame:
    """Load the relative frequency of every population in every sample."""
    return _gold(lambda repo: repo.cell_frequencies())


@st.cache_data
def load_responder_frequencies(unit: Unit) -> pd.DataFrame:
    """Load responder and non-responder frequencies for one unit of analysis."""
    return _gold(lambda repo: repo.responder_frequencies(unit))


@st.cache_data
def load_population_comparisons(unit: Unit, correction: str) -> pd.DataFrame:
    """Load the statistics across all timepoints for one unit and correction."""
    return _gold(lambda repo: repo.population_comparisons(unit, correction))


@st.cache_data
def load_population_comparisons_by_timepoint(correction: str) -> pd.DataFrame:
    """Load the statistics at each timepoint for one correction."""
    return _gold(lambda repo: repo.population_comparisons_by_timepoint(correction))


@st.cache_data
def load_mel_pbmc_subset_samples(subset: str) -> pd.DataFrame:
    """Load one melanoma PBMC subset's samples, by subset name."""
    return _gold(lambda repo: repo.mel_pbmc_subset_samples(subset))


@st.cache_data
def load_mel_pbmc_subset_counts(subset: str) -> pd.DataFrame:
    """Load one melanoma PBMC subset's counts, by subset name."""
    return _gold(lambda repo: repo.mel_pbmc_subset_counts(subset))


def with_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Replace population ids such as b_cell with display names such as B cells. Returns a new
    DataFrame.
    """
    return df.assign(population=df["population"].map(POPULATION_LABELS))


def format_p(p: float) -> str:
    """Format a p-value for display. Values below 0.001 are shown as < 0.001."""
    return "< 0.001" if p < 0.001 else f"{p:.3f}"
