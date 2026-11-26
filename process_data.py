import sys
from typing import Dict, List

from sqlalchemy import insert
from sqlalchemy.orm import Session

from lib.database import DB_PATH, get_engine, has_layer, rebuild_layer
from models.data import SUMMARY_SUBSETS
from models.gold import (
    GoldBase,
    GoldCellFrequency,
    GoldMelPBMCSubsetCount,
    GoldMelPBMCSubsetSample,
    GoldPopulationComparison,
    GoldResponderFrequency,
)
from models.silver import SilverBase
from repos import MelPBMCSubsetRepo
from serializers import (
    cell_frequency_rows,
    mel_pbmc_subset_count_rows,
    mel_pbmc_subset_sample_rows,
    population_comparison_rows,
    responder_frequency_rows,
)
from services import (
    CellFrequencyService,
    MelPBMCSubsetSummaryService,
    ResponderComparisonService,
)

UNITS = ["sample", "subject"]
CORRECTIONS = ["fdr_bh", "bonferroni", "none"]
ALPHA = 0.05


def cell_frequencies(silver: Session) -> List[dict]:
    """Compute the relative frequency of each population in each sample. Returns rows for the gold
    table.
    """
    return cell_frequency_rows(CellFrequencyService(silver).relative_frequencies())


def responder_frequencies(silver: Session) -> List[dict]:
    """Compute responder and non-responder frequencies per sample and per patient. Returns rows for
    the gold table.
    """
    service = ResponderComparisonService(silver)
    return [
        row
        for unit in UNITS
        for row in responder_frequency_rows(unit, service.responder_frequencies(unit=unit))
    ]


def population_comparisons(silver: Session) -> List[dict]:
    """Run the responder vs non-responder statistics for every unit, correction and timepoint.
    Returns rows for the gold table.
    """
    service = ResponderComparisonService(silver)
    rows = []
    for unit in UNITS:
        for correction in CORRECTIONS:
            results = service.compare_populations(unit=unit, correction=correction, alpha=ALPHA)
            rows += population_comparison_rows(results, None, unit, correction, ALPHA)
    for correction in CORRECTIONS:
        for day, results in service.compare_by_timepoint(correction=correction, alpha=ALPHA).items():
            rows += population_comparison_rows(results, day, "subject", correction, ALPHA)
    return rows


def mel_pbmc_subset_samples(silver: Session) -> List[dict]:
    """List every summary melanoma PBMC subset's samples. Returns rows for the gold table."""
    repo = MelPBMCSubsetRepo(silver)
    return [
        row for s in SUMMARY_SUBSETS for row in mel_pbmc_subset_sample_rows(s, repo.samples(s))
    ]


def mel_pbmc_subset_counts(silver: Session) -> List[dict]:
    """Count every summary melanoma PBMC subset by project, response and sex, plus totals. Returns
    rows for the gold table.
    """
    service = MelPBMCSubsetSummaryService(silver)
    return [
        row for s in SUMMARY_SUBSETS for row in mel_pbmc_subset_count_rows(service.summary(s))
    ]


GOLD_TABLES = {
    GoldCellFrequency: cell_frequencies,
    GoldResponderFrequency: responder_frequencies,
    GoldPopulationComparison: population_comparisons,
    GoldMelPBMCSubsetSample: mel_pbmc_subset_samples,
    GoldMelPBMCSubsetCount: mel_pbmc_subset_counts,
}


def build_gold(db_path=DB_PATH) -> Dict[str, int]:
    """Compute every gold table from silver, then rebuild the gold layer. Raises an error if the
    silver tables don't exist yet.
    """
    engine = get_engine(db_path)
    try:
        if not db_path.exists() or not has_layer(engine, SilverBase.metadata):
            raise FileNotFoundError(
                f"Silver tables not found in {db_path.name}. Run `python load_data.py` first."
            )

        with Session(engine) as silver:
            results = {model: compute(silver) for model, compute in GOLD_TABLES.items()}

        rebuild_layer(engine, GoldBase.metadata)
        with Session(engine) as gold, gold.begin():
            for model, rows in results.items():
                if rows:
                    gold.execute(insert(model), rows)
    finally:
        engine.dispose()

    return {model.__tablename__: len(rows) for model, rows in results.items()}


def main():
    """Build the gold layer in cell_counts.db. Prints the row count for each table."""
    try:
        row_counts = build_gold()
    except FileNotFoundError as e:
        sys.exit(str(e))
    print(f"Processed {DB_PATH.name}")
    print("  gold")
    width = max(len(t) for t in row_counts) + 2
    for table, n in row_counts.items():
        print(f"    {table + ':':<{width}}{n}")


if __name__ == "__main__":
    main()
