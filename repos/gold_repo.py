from typing import Optional

import pandas as pd
from sqlalchemy import Select, select

from models.gold import (
    Breakdown,
    GoldCellFrequency,
    GoldMelPBMCSubsetCount,
    GoldMelPBMCSubsetSample,
    GoldPopulationComparison,
    GoldResponderFrequency,
)

from .base_repo import BaseRepo


def _columns(model):
    """List a gold model's columns except the surrogate id. Keeps table order."""
    return [c for c in model.__table__.columns if c.name != "id"]


class GoldRepo(BaseRepo):
    def frame(self, stmt: Select) -> pd.DataFrame:
        """Run a query and return the result as a DataFrame. Used by every gold query."""
        return pd.read_sql(stmt, self.session.connection())

    def cell_frequencies(self) -> pd.DataFrame:
        """Return the relative frequency summary table. One row per sample and population."""
        return self.frame(select(*_columns(GoldCellFrequency)).order_by(GoldCellFrequency.id))

    def responder_frequencies(self, unit: str) -> pd.DataFrame:
        """Return responder and non-responder frequencies for one unit of analysis. Used for the
        boxplot.
        """
        stmt = (
            select(*_columns(GoldResponderFrequency))
            .where(GoldResponderFrequency.unit == unit)
            .order_by(GoldResponderFrequency.id)
        )
        return self.frame(stmt)

    def population_comparisons(self, unit: str, correction: str) -> pd.DataFrame:
        """Return the statistics across all timepoints for one unit and correction. One row per
        population.
        """
        stmt = (
            select(*_columns(GoldPopulationComparison))
            .where(
                GoldPopulationComparison.timepoint.is_(None),
                GoldPopulationComparison.unit == unit,
                GoldPopulationComparison.correction == correction,
            )
            .order_by(GoldPopulationComparison.id)
        )
        return self.frame(stmt)

    def population_comparisons_by_timepoint(self, correction: str) -> pd.DataFrame:
        """Return the statistics at each timepoint for one correction. One row per timepoint and
        population.
        """
        stmt = (
            select(*_columns(GoldPopulationComparison))
            .where(
                GoldPopulationComparison.timepoint.is_not(None),
                GoldPopulationComparison.correction == correction,
            )
            .order_by(GoldPopulationComparison.timepoint, GoldPopulationComparison.id)
        )
        return self.frame(stmt)

    def mel_pbmc_subset_samples(self, subset: str) -> pd.DataFrame:
        """Return one melanoma PBMC subset's samples, by subset name. One row per sample."""
        stmt = (
            select(*_columns(GoldMelPBMCSubsetSample))
            .where(GoldMelPBMCSubsetSample.subset == subset)
            .order_by(GoldMelPBMCSubsetSample.id)
        )
        return self.frame(stmt)

    def mel_pbmc_subset_counts(
        self, subset: str, breakdown: Optional[Breakdown] = None
    ) -> pd.DataFrame:
        """Return one melanoma PBMC subset's counts, by subset name, optionally for one breakdown.
        Breakdowns are total, project, response and sex.
        """
        stmt = (
            select(*_columns(GoldMelPBMCSubsetCount))
            .where(GoldMelPBMCSubsetCount.subset == subset)
            .order_by(GoldMelPBMCSubsetCount.id)
        )
        if breakdown is not None:
            stmt = stmt.where(GoldMelPBMCSubsetCount.breakdown == Breakdown(breakdown).value)
        return self.frame(stmt)
