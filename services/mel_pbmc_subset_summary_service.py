from sqlalchemy.orm import Session

from models.data import MelPBMCSubset, MelPBMCSubsetSummary
from repos import MelPBMCSubsetRepo


class MelPBMCSubsetSummaryService:
    """Combines the subset repo's separate counts into one MelPBMCSubsetSummary. For a subset's
    sample list, call MelPBMCSubsetRepo.samples directly.
    """

    def __init__(self, session: Session):
        self.subsets = MelPBMCSubsetRepo(session)

    def summary(self, subset: MelPBMCSubset) -> MelPBMCSubsetSummary:
        """Summarize a subset: totals, samples per project, and subjects per response and sex."""
        n_samples, n_subjects = self.subsets.totals(subset)
        return MelPBMCSubsetSummary(
            subset=subset,
            n_samples=n_samples,
            n_subjects=n_subjects,
            samples_per_project=self.subsets.samples_per_project(subset),
            subjects_per_response=self.subsets.subjects_per_response(subset),
            subjects_per_sex=self.subsets.subjects_per_sex(subset),
        )
