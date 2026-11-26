# Teiko Technical Assessment
By Michael Holland

## Description

This is my project for the Teiko technical assessment. It builds a data processing pipeline and analyzes how the a drug affects immune cell populations in a clinical trial: a Python pipeline loads `cell-count.csv` into SQLite (`cell_counts.db`), and a Streamlit dashboard shows the results in three tabs:

- **Cell Populations:** each immune cell population's relative frequency in every sample.
- **Treatment Response:** responders vs non-responders (melanoma, miraclib, PBMC), with Mann-Whitney U tests.
- **Melanoma PBMC:** melanoma PBMC samples from miraclib patients at baseline (day 0), broken down by project, response and sex.

Tables are layered as `bronze_*` (raw CSV), `silver_*` (cleaned schema) and `gold_*` (precomputed results for the dashboard). This is a collapsed / simplified version of having a bronze / silver / gold data engineering pattern. Service results are turned into gold rows by the `serializers/` layer, and melanoma PBMC subset tables (`gold_mel_pbmc_subset_*`) are keyed by subset name.

Results and further analysis is presented using a StreamLit dashboard which when ran with the `make dashboard` command will be on this link: <http://localhost:8501>

Code has also been tested and verified to work in Github Codespaces. 

## Quick Setup to see Pipeline

```bash
make setup
make pipeline
make dashboard
```

## Dev Instructions (Python)

Requires Python 3.10 or newer. On macOS, create and activate a virtual environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Create & Process Database

Load `cell-count.csv` into `cell_counts.db` (bronze and silver tables):

```bash
python load_data.py
```

Compute the results from silver into the gold tables:

```bash
python process_data.py
```

### Run Data Pipeline

Run both steps in order, from the CSV to the dashboard-ready tables:

```bash
python load_data.py && python process_data.py
```

### Run Dashboard

```bash
python -m streamlit run dashboard/app.py --server.port 8501
```

## Dashboard

<http://localhost:8501> (in Codespaces, open forwarded port 8501 from the **Ports** tab)
