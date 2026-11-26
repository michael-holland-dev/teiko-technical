from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PopulationFrequency:
    """One population in one sample."""

    sample: str
    total_count: int
    population: str
    count: int
    percentage: Optional[float]
