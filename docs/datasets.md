# Dataset Descriptions

All data files are gitignored and stored locally only. The pipeline produces two categories of data: **training data** (Jan 2023 – Dec 2025, England only) and **inference data** (Jan 2026 onwards, all countries).

---

## Folder structure

```
data/
├── training/
│   ├── england/            ← per-source CSVs for England
│   │   ├── govuk_education.csv
│   │   ├── epi.csv
│   │   ├── nuffield.csv
│   │   ├── fft_education_datalab.csv
│   │   ├── fed.csv
│   │   └── schoolsweek.csv
│   ├── scotland/           ← future (Phase 2)
│   ├── ireland/            ← future (Phase 2)
│   └── training_data.csv   ← merged corpus (all England sources combined)
└── inference/
    ├── england/            ← weekly merged CSVs from Jan 2026
    │   └── YYYY-MM-DD_YYYY-MM-DD.csv
    ├── scotland/           ← Phase 1 test corpus + weekly (future)
    └── ireland/            ← Phase 1 test corpus + weekly (future)
```

---

## Shared column schema

All CSVs — both training and inference — share the same columns:

| Column | Type | Description |
|---|---|---|
| `url` | string | Source article URL (unique identifier) |
| `title` | string | Article title |
| `date` | YYYY-MM-DD | Publication date |
| `text` | string | Full article body text |
| `source` | string | Source key — see values below |
| `country` | string | Jurisdiction: `eng`, `sco`, `irl` |
| `type` | string | Source type — see values below |
| `institution_name` | string | Publishing institution name |

**`source` values:** `gov`, `epi`, `nuffield`, `fft`, `fed`, `schoolsweek`

**`type` values:** `government`, `think_tank`, `ed_res_org`, `prof_body`, `ed_journalism`

---

## Per-source descriptions (England)

### `govuk_education.csv`
GOV.UK news and communications tagged under the Education taxon, filtered to core domestic education policy bodies.

**Included bodies:** Department for Education, Education and Skills Funding Agency, Ofsted, Ofqual, Office for Students, Standards and Testing Agency, Institute for Apprenticeships, Skills England

**Excluded:** Publications where education is framed primarily as international relations, economic growth, sectoral skills development, or operational/administrative delivery (~350 articles). See `src/england/dfe.py` for the full exclusion rationale.

Extra columns in the raw file (before merging): `from` (publishing organisation string), `core_education` (bool), `primary_org` (string). These are used by `merge.py` for filtering and are not carried into `training_data.csv`.

---

### `epi.csv`
Research publications from the Education Policy Institute.

Source: `https://epi.org.uk/publications-and-research/`

---

### `nuffield.csv`
News and events from the Nuffield Foundation's education programme.

Source: `https://www.nuffieldfoundation.org/news-and-events`

---

### `fft_education_datalab.csv`
Blog posts from FFT Education Datalab.

Source: `https://ffteducationdatalab.org.uk/blog/`

---

### `fed.csv`
News and resources from the Foundation for Educational Development.

Source: `https://fed.education/news-resources/`

---

### `schoolsweek.csv`
News articles from Schools Week. Scraper in progress.

Source: `https://schoolsweek.co.uk/news/`

---

## Merged training dataset

### `training_data.csv`
All England sources combined into a single file. Produced by running `python src/merge.py`.

- **Coverage:** January 2023 – December 2025
- **Country:** England only (`country = eng`)
- **Deduplication:** URLs are deduplicated; any article appearing in multiple source CSVs is kept once
- **Date cap:** Hard cap at 31 December 2025 — any articles scraped beyond this date are excluded
- **GOV.UK filtering:** Only `core_education == True` rows are included; `institution_name` is set from `primary_org`
- **Approximate size:** ~17MB, ~3,000–4,000 articles across all sources

---

## Inference datasets

### `data/inference/england/YYYY-MM-DD_YYYY-MM-DD.csv`
One file per weekly run, covering all England sources for that week.

- **Coverage:** Jan 2026 onwards (weekly)
- **Simulated batches:** Jan–Feb 2026 batches are created retrospectively before automated weekly runs begin
- **Structure:** Same columns as `training_data.csv`

### `data/inference/scotland/` and `data/inference/ireland/`
Future. Will contain:
- A retrospective corpus (Jan 2025 – Dec 2025) as Phase 1 test data
- Weekly files from the point at which Scotland/Ireland scrapers are deployed

These files are used to run the England-trained EduAtlas model on Scottish/Irish content as part of the cross-jurisdiction analysis.
