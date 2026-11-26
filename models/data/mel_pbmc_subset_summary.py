from dataclasses import dataclass
from typing import List

from .category_count import CategoryCount
from .mel_pbmc_subset import MelPBMCSubset


@dataclass(frozen=True)
class MelPBMCSubsetSummary:
    """Counts describing a melanoma PBMC subset: samples per project, subjects per response and
    sex, and the totals.
    """

    subset: MelPBMCSubset
    n_samples: int
    n_subjects: int
    samples_per_project: List[CategoryCount]
    subjects_per_response: List[CategoryCount]
    subjects_per_sex: List[CategoryCount]
