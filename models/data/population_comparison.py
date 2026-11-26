from dataclasses import dataclass


@dataclass(frozen=True)
class PopulationComparison:
    """Responders vs non-responders for one cell population."""

    population: str
    n_responders: int
    n_non_responders: int
    responder_median: float
    non_responder_median: float
    responder_mean: float
    non_responder_mean: float
    median_difference: float
    u_statistic: float
    effect_size: float
    p_value: float
    adjusted_p_value: float
    significant: bool
