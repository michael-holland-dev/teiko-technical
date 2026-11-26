from typing import List, Optional, Sequence

from sqlalchemy import Select, func, select

from models.silver import POPULATIONS, CellCount, CellPopulation, Sample
from models.data import PopulationFrequency

from .base_repo import BaseRepo


class CellFrequencyRepo(BaseRepo):
    def relative_frequencies_query(self, sample_filter: Optional[Select] = None) -> Select:
        """Build the query for each population's share of its sample's total count. The total is a
        window sum over the five populations, and a zero total gives a NULL percentage.
        """
        total_count = func.sum(CellCount.count).over(partition_by=CellCount.sample_id)
        stmt = (
            select(
                CellCount.sample_id,
                CellCount.population_id,
                Sample.uuid.label("sample"),
                total_count.label("total_count"),
                CellPopulation.name.label("population"),
                CellCount.count.label("count"),
                (100.0 * CellCount.count / func.nullif(total_count, 0)).label("percentage"),
            )
            .join(Sample, CellCount.sample_id == Sample.id)
            .join(CellPopulation, CellCount.population_id == CellPopulation.id)
            .where(CellPopulation.name.in_(POPULATIONS))
            .order_by(CellCount.sample_id, CellCount.population_id)
        )
        if sample_filter is not None:
            stmt = stmt.where(CellCount.sample_id.in_(sample_filter))
        return stmt

    def relative_frequencies(
        self, sample_uuids: Optional[Sequence[str]] = None
    ) -> List[PopulationFrequency]:
        """Return relative frequencies for every sample, or for the given sample ids. One row per
        sample and population.
        """
        sample_filter = None
        if sample_uuids is not None:
            sample_filter = select(Sample.id).where(Sample.uuid.in_(sample_uuids))
        return self.fetch(self.relative_frequencies_query(sample_filter), PopulationFrequency)
