"""Serializers: turn service results (models.data dataclasses) into gold table rows.

This keeps the gold models to table definitions only, and keeps row-building out of the pipeline
script.
"""

from .base_serializer import gold_columns, to_row
from .comparison_serializer import population_comparison_rows
from .frequency_serializer import cell_frequency_rows, responder_frequency_rows
from .mel_pbmc_subset_serializer import mel_pbmc_subset_count_rows, mel_pbmc_subset_sample_rows

__all__ = [
    "cell_frequency_rows",
    "gold_columns",
    "mel_pbmc_subset_count_rows",
    "mel_pbmc_subset_sample_rows",
    "population_comparison_rows",
    "responder_frequency_rows",
    "to_row",
]
