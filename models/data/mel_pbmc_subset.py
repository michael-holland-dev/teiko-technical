from dataclasses import dataclass, replace
from typing import ClassVar, Optional, Tuple


@dataclass(frozen=True)
class MelPBMCSubset:
    """A named subset of the melanoma PBMC samples, selected by subject treatment and, optionally,
    by timepoint.

    Every subset is melanoma patients' PBMC samples (CONDITION and SAMPLE_TYPE). name identifies
    the subset in the gold tables, so it must be unique among the subsets the pipeline builds.

    time_from_treatment_start=None means "any timepoint": it does not filter on time, so it
    can't be used to select samples whose timepoint is missing.
    """

    CONDITION: ClassVar[str] = "melanoma"
    SAMPLE_TYPE: ClassVar[str] = "PBMC"

    name: str
    treatment: str
    time_from_treatment_start: Optional[int] = None

    def at_day(self, day: int) -> "MelPBMCSubset":
        """Return the same subset limited to one timepoint, named after it (e.g. "..._day7")."""
        return replace(self, name=f"{self.name}_day{day}", time_from_treatment_start=day)


# The study's named subsets. Define new ones here and add them to SUMMARY_SUBSETS to give them
# gold rows, so every layer uses the same filters.
MIRACLIB_MEL_PBMC_SUBSET = MelPBMCSubset(name="miraclib", treatment="miraclib")
"""Melanoma PBMC samples from miraclib patients, every timepoint. Used for the response analysis."""

BASELINE_MEL_PBMC_SUBSET = MIRACLIB_MEL_PBMC_SUBSET.at_day(0)
"""The same samples at baseline (day 0 from treatment start). Summarized on the Melanoma PBMC tab."""

SUMMARY_SUBSETS: Tuple[MelPBMCSubset, ...] = (BASELINE_MEL_PBMC_SUBSET,)
"""Subsets the pipeline writes sample lists and counts for (gold_mel_pbmc_subset_* tables)."""
