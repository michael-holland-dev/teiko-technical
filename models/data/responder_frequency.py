from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ResponderFrequency:
    """One population's relative frequency for one sample (or one subject)."""

    sample: Optional[str]
    subject: str
    response: str
    time_from_treatment_start: Optional[int]
    population: str
    percentage: Optional[float]
