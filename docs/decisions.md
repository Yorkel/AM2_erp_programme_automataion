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

## 10. UK Parliament Education Select Committee — deferred

**Decision:** Not included as a training source at this stage.

**What was explored:** The UK Parliament Committees API (`committees-api.parliament.uk/api/`) is publicly accessible and returns structured metadata for Education Committee publications (reports, correspondence, written evidence). The Education Committee has ID 203 and has published 139 reports and 479 items of correspondence. The API works without authentication.

**Why it was deferred:** Getting the actual text content proved impractical:
- The `committees.parliament.uk` website returns 403 for scraping requests
- Older `publications.parliament.uk` URLs also return 403
- The API returns metadata only — report text is not included
- Full report text is only available as PDFs, which would require PDF parsing (significantly more complex than HTML scraping)

**Scope note:** UK Parliament data covers England education policy (education is devolved, so it is primarily relevant to England). The focus would be on Reports and Special Reports from the Education Select Committee, not written evidence submissions or correspondence, which are higher volume and lower signal.

**If revisited:** The most practical route would be PDF parsing using `pdfplumber` on the report document URLs returned by the API. An alternative would be to check if the [parliament.uk search API](https://developer.parliament.uk/) provides a text extraction endpoint that has since become available.

---

## 11. Training data versioning

**Decision:** The merged training dataset is versioned as `training_data_v1.csv`. Future retraining will produce `training_data_v2.csv` etc.

**What v1 contains:** Articles from Jan 2023 – Dec 2025 across six England sources (GOV.UK, EPI, Nuffield, FFT Education Datalab, FED, Schools Week). The Schools Week data in v1 was scraped using the old HTML scraper (2,742 articles). The current scraper (WP API) produces 4,207 articles — v2 will include the fuller dataset.

**Why versioned:** Allows the deployed model to be clearly tied to the dataset it was trained on. When the training data is updated (new schoolsweek, UK Parliament, etc.) the new merged file gets a new version number, making it easy to track which model was trained on which data.

**Location:** `data/training/training_data_v1.csv`

---

## 12. Weekly inference boundary instability — known methodological consideration

**What it is:** The weekly inference batches are bounded by fixed date ranges (e.g. 9–15 Jan). An article published late on the last day of a window (e.g. Thursday 15 Jan at 23:00) may or may not appear in that week's batch depending on scraper timing, and could potentially appear in the following week's batch instead. There is no deduplication across weekly inference files.

**Why this matters beyond a technical bug:** This is a deliberate methodological observation. The project is partly concerned with the instability of automated pipelines and how that instability propagates into outputs — and ultimately into the policy decisions those outputs inform. A system that surfaces "the top education topics this week" is not neutral: what counts as "this week" is a boundary imposed by the pipeline, and articles near that boundary are unstable. This is worth surfacing explicitly in the analysis rather than treating it as a problem to be silently fixed.

**What is not done:** No deduplication across weekly files. This is intentional — each weekly batch represents a snapshot as the pipeline would have run that week, preserving the instability for analysis.

**If it becomes a practical problem:** Add a seen-URLs log (`data/inference/seen_urls.txt`) that is appended after each weekly run and checked at the start of each scrape. This would eliminate cross-batch duplicates while preserving the within-batch snapshot logic.

---

## 13. Inference evaluation without ground truth

**Decision:** Inference outputs are evaluated qualitatively and through internal metrics — not against labelled ground truth.

**Why no ground truth is needed:** The pipeline uses unsupervised topic modelling (EduAtlas). There are no pre-defined correct labels — the model discovers patterns from the training corpus. Inference means applying those patterns to new weekly data to surface active topics and sentiment. Ground truth is not a prerequisite for this to be valid.

**What small weekly N means methodologically:** Weekly batches of 15–30 articles are realistic for a specialised policy domain. This is signal, not a data quality problem — a slow news week genuinely produces fewer articles, and a pipeline that finds nothing notable in 17 articles is making a valid finding ("quiet week"). The practical implication is that week-level percentage breakdowns are noisy at small N (e.g. 2/17 vs 3/17 for a topic is a large swing), and this should be flagged as a limitation of weekly granularity rather than a model failure.

**How inference outputs are assessed:**

| Method | What it tells you |
|---|---|
| Coherence score (C_v) | Are the words within each topic semantically related? Standard metric for LDA/BERTopic. |
| Qualitative inspection | Do the top words/documents per topic make editorial sense? Expected in any dissertation evaluation. |
| Temporal stability | Do topics persist week-over-week in plausible ways? A topic should not appear once and vanish. |
| Coverage check | What % of articles are assigned to a topic vs. flagged as noise? High noise suggests the model struggles with this content type. |

**Where ground truth would add value:** Manually labelling ~50–100 inference-period articles and comparing to model assignments (held-out human evaluation) would strengthen the evaluation, but is not standard practice in topic modelling research and is treated as optional here.

**The cross-jurisdiction angle:** When the England-trained model is later applied to Scottish and Irish content (Phase 1), the places where it struggles — low coherence, high noise rates — are substantive findings. They reveal which assumptions in the training data are England-specific rather than universal. Evaluation difficulty becomes part of the analysis, not just a technical problem to fix.

---

## 14. Automatic validation after every inference write

**Decision:** `run.py` runs a lightweight validation check immediately after writing each inference CSV, printing warnings to stdout but not halting the pipeline.

**What is checked:**
- All expected columns (`url`, `title`, `date`, `text`, `source`, `country`, `type`, `institution_name`) are present
- No rows have empty or null `text`
- Article count is not zero; a count below 5 triggers a low-volume warning

**Why non-fatal:** A scraper failing silently mid-run (e.g. a source returning 0 articles due to a temporary block) should be visible in the output but should not prevent the other sources' data from being saved. The scrape log and validation output together give enough signal to diagnose problems without making the pipeline brittle.

**Where this is implemented:** `_validate_inference()` in `src/run.py`, called after `_write_scrape_log()` for every inference run.

---

## 15. Supabase architecture

**Decision:** Supabase is the central production database. All downstream consumers (dashboard, sentiment pipeline, newsletter) read from Supabase rather than from local CSV files.

**Why Supabase:** Managed Postgres with a Python client (`supabase-py`), built-in REST API, and Database Webhooks — sufficient for the volume of this project (hundreds of articles per week, not millions) without requiring a custom backend.

**Single articles table** with nullable topic columns. Raw articles are inserted first; topic and sentiment columns are filled in by subsequent pipeline steps. This avoids needing a separate "raw" and "labelled" table at this scale.

**Articles table schema:**

| Column | Type | Source |
|---|---|---|
| `url` | text (primary key) | inference CSV |
| `title` | text | inference CSV |
| `date` | date | inference CSV |
| `text` | text | inference CSV |
| `source` | text | inference CSV |
| `country` | text | inference CSV |
| `type` | text | inference CSV |
| `institution_name` | text | inference CSV |
| `week_number` | integer | seed script |
| `week_start` | date | seed script |
| `week_end` | date | seed script |
| `dominant_topic` | text | FastAPI/joblib model |
| `topic_probabilities` | jsonb | FastAPI/joblib model |
| `sentiment_score` | float | sentiment pipeline |
| `sentiment_label` | text | sentiment pipeline |

**How each pipeline step connects:**

1. `seed_supabase.py` (this repo) — reads weekly inference CSV, inserts raw articles (topic/sentiment columns NULL). Upserts on `url` to avoid duplicates if run twice.
2. FastAPI + joblib model (Docker, separate service) — triggered by Supabase Database Webhook on INSERT, or called directly by `seed_supabase.py`. Receives article text, returns `dominant_topic` + `topic_probabilities`, writes back to the same row.
3. Sentiment pipeline (separate) — reads rows where `sentiment_score IS NULL`, processes, writes back.
4. Dashboard, newsletter DB — read from Supabase directly.

**FastAPI not in this repo.** `seed_supabase.py` only requires `supabase-py`. No FastAPI dependency in the scraping pipeline.

**Webhook vs direct call:** Supabase Database Webhooks (Settings → Webhooks) fire on INSERT and call a specified HTTP URL. This is the preferred long-term pattern (decoupled, works with GitHub Actions automation). While FastAPI is not yet deployed, `seed_supabase.py` can call the FastAPI endpoint directly as a temporary measure.

**Security:** Row Level Security (RLS) was enabled automatically on the `articles` table at creation (Supabase "automatic RLS" project setting was enabled). No public read or insert policies have been created — and none are needed right now. The `SUPABASE_SERVICE_KEY` (service role) bypasses RLS entirely, so `seed_supabase.py` can insert without any policy. A read policy will be added when the dashboard is built and needs to query the table using the publishable key. Do not follow Supabase's suggested "enable read/insert for all users" templates — that would make the table publicly accessible.

**Single-table enrichment pattern:** All pipeline steps write to the same `articles` table. `seed_supabase.py` inserts rows with topic/sentiment columns as NULL. The FastAPI model and sentiment pipeline subsequently UPDATE those columns on existing rows. No separate output tables are needed for topic or sentiment data at this stage.

**Future tables (not yet created):**
- `newsletter_runs` — track which articles were included in each weekly newsletter and when it was sent. To be created when newsletter generation is built.
- `topics` — store the topic taxonomy from the trained model (topic ID, label, keywords, description). To be created when the FastAPI model is connected.

---

## 16. Pre-commit secrets scanning

**Decision:** `detect-secrets` is installed as a pre-commit hook to prevent accidental credential commits.

**What is implemented:**
- `.pre-commit-config.yaml` added to repo root, configured to run `detect-secrets` on every commit
- `.secrets.baseline` created (2026-02-26) — establishes what is already in the repo as known-safe
- Hook installed via `pre-commit install`

**Baseline findings:** 4 flags, all confirmed false positives — base64-encoded PNG outputs in `x_ERP_newsletter_automation/notebooks/organisations.ipynb`. No real secrets in the repo.

**Why this matters now:** `seed_supabase.py` (Step 2) will be the first code to use live credentials. The hook must be in place before that file is written to catch any accidental hardcoding.

**Updating the baseline:** If detect-secrets flags a new false positive, run `detect-secrets audit .secrets.baseline` to review and mark it safe. If the repo schema changes significantly, regenerate with `detect-secrets scan > .secrets.baseline`.

---

## Future decisions not yet made

- **Which Scottish sources to include** — candidates: Scottish Government, Education Scotland, HMIE/HM Inspectorate of Education, Scottish Parliament, SSSC
- **Which Irish sources to include** — candidates: Gov.ie (education), NCCA, Teaching Council, Oireachtas
- **Phase 2 retraining trigger** — when to retrain with all three countries and what the new training cutoff will be
- **GitHub Actions automation** — weekly Mode C run not yet configured; planned for March 2026 onwards
