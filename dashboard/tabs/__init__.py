from . import cell_populations, mel_pbmc_subset, treatment_response

TABS = {
    "Cell Populations": cell_populations.render,
    "Treatment Response": treatment_response.render,
    "Melanoma PBMC": mel_pbmc_subset.render,
}

__all__ = ["TABS"]
