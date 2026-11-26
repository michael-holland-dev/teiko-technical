import math
from collections import defaultdict
from dataclasses import replace
from statistics import mean, median
from typing import Dict, Iterable, List, Literal, Optional, Tuple

from scipy.stats import false_discovery_control, mannwhitneyu
from sqlalchemy.orm import Session

from models.silver import NON_RESPONDER, POPULATIONS, RESPONDER
from models.data import (
    MIRACLIB_MEL_PBMC_SUBSET,
    MelPBMCSubset,
    PopulationComparison,
    ResponderFrequency,
)
from repos import ResponderFrequencyRepo, Unit

Correction = Literal["fdr_bh", "bonferroni", "none"]

RESPONSE_SUBSET = MIRACLIB_MEL_PBMC_SUBSET
TIMEPOINTS = (0, 7, 14)


class ResponderComparisonService:
    def __init__(self, session: Session):
        self.frequencies = ResponderFrequencyRepo(session)

    def responder_frequencies(
        self, subset: MelPBMCSubset = RESPONSE_SUBSET, unit: Unit = "subject"
    ) -> List[ResponderFrequency]:
        """Return responder and non-responder frequencies for the boxplot. Defaults match
        compare_populations.
        """
        return self.frequencies.responder_frequencies(subset, unit)

    def compare_populations(
        self,
        subset: MelPBMCSubset = RESPONSE_SUBSET,
        unit: Unit = "subject",
        correction: Correction = "fdr_bh",
        alpha: float = 0.05,
    ) -> List[PopulationComparison]:
        """Test every population for a responder vs non-responder difference. Defaults to per-
        patient values and Benjamini-Hochberg correction.
        """
        rows = self.frequencies.responder_frequencies(subset, unit)
        return compare_groups(rows, correction, alpha)

    def compare_by_timepoint(
        self,
        correction: Correction = "fdr_bh",
        alpha: float = 0.05,
        timepoints: Iterable[int] = TIMEPOINTS,
    ) -> Dict[int, List[PopulationComparison]]:
        """Run the comparison at each timepoint on its own. Shows whether baseline differs from
        after treatment starts.
        """
        return {
            day: self.compare_populations(
                RESPONSE_SUBSET.at_day(day), "subject", correction, alpha
            )
            for day in timepoints
        }

    def significant_populations(
        self,
        subset: MelPBMCSubset = RESPONSE_SUBSET,
        unit: Unit = "subject",
        correction: Correction = "fdr_bh",
        alpha: float = 0.05,
    ) -> List[PopulationComparison]:
        """Return only the populations that are significant after correction. Uses the same
        settings as compare_populations.
        """
        return [
            r for r in self.compare_populations(subset, unit, correction, alpha) if r.significant
        ]


def compare_groups(
    rows: Iterable[ResponderFrequency],
    correction: Correction = "fdr_bh",
    alpha: float = 0.05,
) -> List[PopulationComparison]:
    """Compare responders and non-responders for every population with Mann-Whitney U tests.
    Adjusts the p-values and flags significant populations.
    """
    groups: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    for r in rows:
        if _is_number(r.percentage):
            groups[(r.population, r.response)].append(r.percentage)

    populations = [p for p in POPULATIONS if any((p, resp) in groups for resp in (RESPONDER, NON_RESPONDER))]
    results = [
        _compare_population(pop, groups.get((pop, RESPONDER), []), groups.get((pop, NON_RESPONDER), []))
        for pop in populations
    ]
    adjusted = _adjust_p_values([r.p_value for r in results], correction)
    return [
        replace(r, adjusted_p_value=q, significant=q < alpha)
        for r, q in zip(results, adjusted)
    ]


def _compare_population(population: str, yes: List[float], no: List[float]) -> PopulationComparison:
    """Run the Mann-Whitney U test for one population and compute its effect size. Identical or
    untestable inputs give p = 1 and no effect.
    """
    if not yes or not no:
        missing = "responders" if not yes else "non-responders"
        raise ValueError(f"No {missing} for {population}; can't compare groups")
    n1, n2 = len(yes), len(no)
    if len(set(yes) | set(no)) == 1:
        u, p_value = n1 * n2 / 2, 1.0
    else:
        test = mannwhitneyu(yes, no, alternative="two-sided")
        u, p_value = float(test.statistic), float(test.pvalue)
        if math.isnan(p_value):
            u, p_value = n1 * n2 / 2, 1.0
    return PopulationComparison(
        population=population,
        n_responders=n1,
        n_non_responders=n2,
        responder_median=median(yes),
        non_responder_median=median(no),
        responder_mean=mean(yes),
        non_responder_mean=mean(no),
        median_difference=median(yes) - median(no),
        u_statistic=u,
        effect_size=2 * u / (n1 * n2) - 1,
        p_value=p_value,
        adjusted_p_value=float("nan"),
        significant=False,
    )


def _is_number(value: Optional[float]) -> bool:
    """Check that a value is present and not NaN. Used to skip samples with no cells."""
    return value is not None and not math.isnan(value)


def _adjust_p_values(p_values: List[float], correction: Correction) -> List[float]:
    """Adjust p-values for multiple testing. Supports Benjamini-Hochberg, Bonferroni or no
    correction.
    """
    if not p_values or correction == "none":
        return list(p_values)
    if correction == "bonferroni":
        return [min(1.0, p * len(p_values)) for p in p_values]
    if correction == "fdr_bh":
        return [float(q) for q in false_discovery_control(p_values, method="bh")]
    raise ValueError(f"correction must be 'fdr_bh', 'bonferroni' or 'none', got {correction!r}")
