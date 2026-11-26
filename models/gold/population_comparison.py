from typing import Optional

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..base import AUTOINCREMENT
from .base import GoldBase


class GoldPopulationComparison(GoldBase):
    """Statistics: responders vs non-responders, per population.

    Precomputed for every combination of unit of analysis and p-value
    correction, so the dashboard can switch between them. timepoint is NULL
    for the analysis across all timepoints, or 0, 7 or 14 for one timepoint
    on its own.
    """

    __tablename__ = "gold_population_comparisons"
    __table_args__ = (
        UniqueConstraint(
            "timepoint", "unit", "correction", "population", name="uq_gold_population_comparisons"
        ),
        AUTOINCREMENT,
    )

    timepoint: Mapped[Optional[int]]
    unit: Mapped[str] = mapped_column(String)
    correction: Mapped[str] = mapped_column(String)
    alpha: Mapped[float]
    population: Mapped[str] = mapped_column(String)
    n_responders: Mapped[int]
    n_non_responders: Mapped[int]
    responder_median: Mapped[float]
    non_responder_median: Mapped[float]
    responder_mean: Mapped[float]
    non_responder_mean: Mapped[float]
    median_difference: Mapped[float]
    u_statistic: Mapped[float]
    effect_size: Mapped[float]
    p_value: Mapped[float]
    adjusted_p_value: Mapped[float]
    significant: Mapped[bool]
