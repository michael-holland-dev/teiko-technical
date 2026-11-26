from typing import Iterable, List

from models.data import MelPBMCSubset, MelPBMCSubsetSample, MelPBMCSubsetSummary
from models.gold import Breakdown, Counted, GoldMelPBMCSubsetCount, GoldMelPBMCSubsetSample

from .base_serializer import to_row


def mel_pbmc_subset_sample_rows(
    subset: MelPBMCSubset, samples: Iterable[MelPBMCSubsetSample]
) -> List[dict]:
    """Turn a subset's samples into gold_mel_pbmc_subset_samples rows, tagged with the subset
    name.
    """
    return [to_row(GoldMelPBMCSubsetSample, s, subset=subset.name) for s in samples]


def mel_pbmc_subset_count_rows(summary: MelPBMCSubsetSummary) -> List[dict]:
    """Flatten a subset summary into gold_mel_pbmc_subset_counts rows. Totals come first, then one
    row per project, response and sex.
    """

    def row(breakdown: Breakdown, counted: Counted, category, count: int) -> dict:
        return to_row(
            GoldMelPBMCSubsetCount,
            subset=summary.subset.name,
            breakdown=breakdown.value,
            counted=counted.value,
            category=category,
            count=count,
        )

    rows = [
        row(Breakdown.TOTAL, Counted.SAMPLES, None, summary.n_samples),
        row(Breakdown.TOTAL, Counted.SUBJECTS, None, summary.n_subjects),
    ]
    for breakdown, counted, counts in [
        (Breakdown.PROJECT, Counted.SAMPLES, summary.samples_per_project),
        (Breakdown.RESPONSE, Counted.SUBJECTS, summary.subjects_per_response),
        (Breakdown.SEX, Counted.SUBJECTS, summary.subjects_per_sex),
    ]:
        rows += [row(breakdown, counted, c.category, c.count) for c in counts]
    return rows
