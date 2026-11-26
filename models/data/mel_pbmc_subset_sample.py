from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MelPBMCSubsetSample:
    """One sample in a melanoma PBMC subset, with its subject and project details.

    Condition, treatment, sample type and timepoint are left out: the subset fixes them, so they
    would be the same on every row.
    """

    sample: str
    subject: str
    project: str
    response: Optional[str]
    sex: Optional[str]
    age: Optional[int]
