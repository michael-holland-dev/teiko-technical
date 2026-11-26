from typing import Iterable, List, Optional

from models.data import PopulationComparison
from models.gold import GoldPopulationComparison
from repos import Unit

from .base_serializer import to_row


def population_comparison_rows(
    comparisons: Iterable[PopulationComparison],
    timepoint: Optional[int],
    unit: Unit,
    correction: str,
    alpha: float,
) -> List[dict]:
    """Turn one run of population comparisons into gold_population_comparisons rows, tagged with
    the settings it ran with. timepoint None means across all timepoints.
    """
    return [
        to_row(
            GoldPopulationComparison,
            c,
            timepoint=timepoint,
            unit=unit,
            correction=correction,
            alpha=alpha,
        )
        for c in comparisons
    ]
