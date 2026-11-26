from typing import Iterable, List, Tuple

from sqlalchemy import ColumnElement, Select, func, select
from sqlalchemy.orm import InstrumentedAttribute

from models.silver import RESPONSES, SEXES, Project, Sample, Subject
from models.data import CategoryCount, MelPBMCSubset, MelPBMCSubsetSample

from .base_repo import BaseRepo


def _subset_select(*columns, subset: MelPBMCSubset) -> Select:
    """Start a query over a subset's samples joined to their subjects and projects, with the
    subset's filters applied. Every subset query is built from this, so the joins its filters
    depend on are always there.
    """
    stmt = (
        select(*columns)
        .select_from(Sample)
        .join(Subject, Sample.subject_id == Subject.id)
        .join(Project, Subject.project_id == Project.id)
        .where(
            Subject.condition == MelPBMCSubset.CONDITION,
            Subject.treatment == subset.treatment,
            Sample.sample_type == MelPBMCSubset.SAMPLE_TYPE,
        )
    )
    if subset.time_from_treatment_start is not None:
        stmt = stmt.where(Sample.time_from_treatment_start == subset.time_from_treatment_start)
    return stmt


def _with_every_category(
    counts: List[CategoryCount], categories: Iterable[str]
) -> List[CategoryCount]:
    """List every known category in the order given, with 0 for the ones that have no rows. Rows
    with no value (category None) come last, and only when there are some.
    """
    found = {c.category: c.count for c in counts}
    known = [CategoryCount(category=c, count=found.pop(c, 0)) for c in categories]
    others = [CategoryCount(category=c, count=n) for c, n in found.items()]
    return known + others


class MelPBMCSubsetRepo(BaseRepo):
    def sample_ids_query(self, subset: MelPBMCSubset) -> Select:
        """Build a query for the sample ids in a subset. Used as a subquery filter by other repos,
        which can add their own conditions on Sample and Subject.
        """
        return _subset_select(Sample.id, subset=subset)

    def samples(self, subset: MelPBMCSubset) -> List[MelPBMCSubsetSample]:
        """Return a subset's samples with subject and project details, ordered by sample id. One
        MelPBMCSubsetSample per sample.
        """
        stmt = _subset_select(
            Sample.uuid.label("sample"),
            Subject.uuid.label("subject"),
            Project.uuid.label("project"),
            Subject.response,
            Subject.sex,
            Subject.age,
            subset=subset,
        ).order_by(Sample.id)
        return self.fetch(stmt, MelPBMCSubsetSample)

    def totals(self, subset: MelPBMCSubset) -> Tuple[int, int]:
        """Count a subset's samples and distinct subjects. Returns both as a tuple."""
        stmt = _subset_select(
            func.count(Sample.id), func.count(Subject.id.distinct()), subset=subset
        )
        n_samples, n_subjects = self.session.execute(stmt).one()
        return n_samples, n_subjects

    def samples_per_project(self, subset: MelPBMCSubset) -> List[CategoryCount]:
        """Return the number of a subset's samples in each project, in project order. Projects with
        no samples count 0.
        """
        projects = self.session.scalars(select(Project.uuid).order_by(Project.id)).all()
        return self._count_per(Project.uuid, func.count(Sample.id), subset, projects)

    def subjects_per_response(self, subset: MelPBMCSubset) -> List[CategoryCount]:
        """Return a subset's distinct subjects by response, listing every response. Subjects with
        no recorded response are category None.
        """
        return self._count_per(Subject.response, _distinct_subjects(), subset, RESPONSES)

    def subjects_per_sex(self, subset: MelPBMCSubset) -> List[CategoryCount]:
        """Return a subset's distinct subjects by sex, listing every sex. Subjects with no
        recorded sex are category None.
        """
        return self._count_per(Subject.sex, _distinct_subjects(), subset, SEXES)

    def _count_per(
        self,
        column: InstrumentedAttribute,
        count: ColumnElement[int],
        subset: MelPBMCSubset,
        categories: Iterable[str],
    ) -> List[CategoryCount]:
        """Count a subset's rows by one column. Every category is listed in the order given (0 if
        absent), and rows with no value come last as category None.
        """
        stmt = _subset_select(
            column.label("category"), count.label("count"), subset=subset
        ).group_by(column)
        return _with_every_category(self.fetch(stmt, CategoryCount), categories)


def _distinct_subjects() -> ColumnElement[int]:
    """Count distinct subjects, so a subject with several samples counts once."""
    return func.count(Subject.id.distinct())
