# Architectural and Data Decisions

This document records the key decisions made in designing this pipeline and why they were made. Intended as a reference for future development and as context for anyone reviewing the codebase.

---

## 1. Source selection (England)

**Decision:** Six sources covering government, think tanks, research organisations and education journalism.

**Rationale:** The sources were selected to represent the main institutional voices in English education policy discourse:

- **GOV.UK (DfE and arm's-length bodies)** — primary government voice; filtered post-scrape to core education bodies only (DfE, Ofsted, Ofqual, ESFA, Office for Students, Standards and Testing Agency, Institute for Apprenticeships, Skills England). Approximately 350 articles excluded where education is framed as international relations, economic growth, or operational delivery rather than domestic system governance.
- **EPI and Nuffield Foundation** — the two dominant think tanks in English education policy research
- **FFT Education Datalab** — leading data-driven education research organisation
- **Foundation for Educational Development (FED)** — professional body perspective
- **Schools Week** — primary education journalism source covering policy developments

**What is deliberately excluded:** International education bodies (OECD, UNESCO), higher education-focused outlets, and employer/skills-focused organisations, since the focus is on the domestic schools and education system.

---

## 2. Training cutoff: 31 December 2025

**Decision:** Articles published up to 31 December 2025 form the training corpus. Articles from 1 January 2026 onwards are inference data.

**Rationale:** This gives a clean 3-year training window (Jan 2023 – Dec 2025). Simulated weekly inference batches are then created from Jan 2026 onwards to test the pipeline before automated weekly runs begin in March 2026.

**Where this is enforced:**
- `TRAINING_CUTOFF = date(2025, 12, 31)` in both `src/run.py` and `src/merge.py`
- `run.py` routes output to `data/training/` or `data/inference/` automatically
- `merge.py` applies a hard cap so any stray post-2025 articles in per-source CSVs are excluded from `training_data.csv`

---

## 3. England-only training (Phase 1)

**Decision:** Only England sources are included in the training corpus. Scotland and Ireland sources are inference-only until Phase 2.

**Rationale:** This is a deliberate methodological choice. The research question asks how the same education policy issues are framed differently across jurisdictions. Running Scottish and Irish documents through an England-trained model and examining where the model's categories fit poorly is itself part of the analysis — it surfaces the political assumptions built into the tool.

Phase 2 will involve retraining with all three datasets and comparing the outputs.

**Where this is enforced:**
- `TRAINING_COUNTRIES = {"eng"}` in `src/run.py` — Scotland and Ireland always route to `data/inference/` regardless of date range

---

## 4. Scotland and Ireland retrospective start: January 2025

**Decision:** When Scotland and Ireland scrapers are built, the default retrospective start is January 2025 (not January 2023 as for England).

**Rationale:** A full 3-year retrospective for Scotland and Ireland is not necessary for Phase 1 — approximately 14 months of data (Jan 2025 – Feb 2026) is sufficient for the cross-jurisdiction inference analysis. This also keeps scraping time manageable when the scrapers are first built.

**Where this is set:** `RETROSPECTIVE_START = {"eng": date(2023,1,1), "sco": date(2025,1,1), "irl": date(2025,1,1)}` in `src/run.py`

---

## 5. One merged inference file per weekly run

**Decision:** Inference runs produce a single merged CSV per week (e.g. `2026-01-06_2026-01-12.csv`) rather than separate per-source files.

**Rationale:** The inference output is fed directly into downstream analysis (EduAtlas topic modelling and sentiment analysis) and newsletter automation. A single merged file with consistent columns is simpler to consume than six separate files that need joining.

**Training data** keeps separate per-source CSVs because this preserves the ability to rerun individual scrapers, inspect per-source quality, and update sources independently.

---

## 6. Folder structure by country

**Decision:** Data and source code are organised into country subfolders (`england/`, `scotland/`, `ireland/`) rather than flat files.

**Rationale:** The pipeline is explicitly designed for cross-jurisdiction analysis. Country subfolders make it immediately clear which data belongs to which jurisdiction, prevent accidental mixing, and make the Phase 2 retraining step explicit (adding Scotland/Ireland to `merge.py` becomes a visible deliberate act).

---

## 7. Append vs overwrite (training runs)

**Decision:** When running a training scrape with `--since`, the scraper appends to existing per-source CSVs rather than overwriting.

**Rationale:** Allows a scrape that failed partway through to be resumed without losing already-scraped data. `merge.py` deduplicates on URL before writing `training_data.csv`, so any overlap from a partial re-run is safe.

---

## 8. `merge.py` as a separate step

**Decision:** `merge.py` is run manually after `run.py`, not called automatically.

**Rationale:** Merging all sources into `training_data.csv` is an intentional checkpoint — you want to inspect per-source counts and the date cap before committing to a new training corpus. Running it automatically after every scrape would obscure that checkpoint.

---

## 9. `country` column in all output data

**Decision:** Every row in every output CSV (training and inference) includes a `country` column (`eng`, `sco`, `irl`).

**Rationale:** The downstream EduAtlas analysis needs to filter and compare by country. Having it as a column from the point of collection means it never needs to be inferred from filenames or folder paths later.

---

## Future decisions not yet made

- **Which Scottish sources to include** — candidates: Scottish Government, Education Scotland, HMIE/HM Inspectorate of Education, Scottish Parliament, SSSC
- **Which Irish sources to include** — candidates: Gov.ie (education), NCCA, Teaching Council, Oireachtas
- **Phase 2 retraining trigger** — when to retrain with all three countries and what the new training cutoff will be
- **Supabase integration** — `seed_supabase.py` not yet built; will read from `data/inference/` and push to Supabase
- **GitHub Actions automation** — weekly Mode C run not yet configured; planned for March 2026 onwards
