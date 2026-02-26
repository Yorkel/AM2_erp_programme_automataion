# education-policy-scraper

A scraping pipeline for UK and Irish education policy documents from public sources. Collects articles from government bodies, think tanks, research organisations and education press across England, Scotland and the Republic of Ireland.

The data produced by this pipeline feeds two downstream projects:

- **Newsletter automation** — weekly digests of education policy coverage for the Education Research Programme (ERP) newsletter
- **EduAtlas** — an AI-assisted text analysis tool examining education policy topics and sentiment across England, Scotland and the Republic of Ireland, with a focus on whose voices shape policy debate and what assumptions are built into AI-assisted analysis

---

## Current sources (England)

| Source | Type | Coverage |
|---|---|---|
| GOV.UK (DfE, Ofsted, Ofqual, ESFA, Office for Students) | Government | News and policy communications |
| Education Policy Institute (EPI) | Think tank | Research publications |
| Nuffield Foundation | Think tank | News and research |
| FFT Education Datalab | Research organisation | Blog posts |
| Foundation for Educational Development (FED) | Professional body | News and resources |
| Schools Week | Education journalism | News articles (scraper in progress) |

Scotland and Republic of Ireland sources are planned — see [docs/decisions.md](docs/decisions.md).

---

## How the pipeline works

```bash
python src/run.py --country eng
```

There are two modes depending on the date flags you pass:

| Mode | Command | Output |
|---|---|---|
| **A — Full retrospective** | `python src/run.py --country eng` | `data/training/england/` per-source CSVs |
| **C — Weekly inference** | `python src/run.py --country eng --since 2026-01-06 --until 2026-01-12` | `data/inference/england/2026-01-06_2026-01-12.csv` |

**Training data** covers Jan 2023 – Dec 2025 (England only). Run Mode A once to build the full corpus, then run `merge.py` to produce the merged dataset.

**Inference data** is weekly from Jan 2026 onwards. Each run produces a single merged CSV in `data/inference/<country>/`. Simulated weekly batches (Jan–Feb 2026) are created by running Mode C with historical date ranges before the automated weekly schedule begins.

After Mode A, regenerate the merged training dataset:

```bash
python src/merge.py
```

This produces `data/training/training_data.csv` — all sources combined, deduplicated, capped at 31 December 2025.

### Scotland and Ireland (Phase 1)

Scotland and Ireland sources always go to `data/inference/` — they are not included in training data until Phase 2. Their retrospective corpus (Jan 2025 onwards) is also created via Mode C:

```bash
python src/run.py --country sco --since 2025-01-01 --until 2025-12-31
python src/run.py --country irl --since 2025-01-01 --until 2025-12-31
```

See [docs/decisions.md](docs/decisions.md) for the rationale.

---

## Project structure

```
src/
├── run.py                  # Pipeline entry point — all modes and countries
├── merge.py                # Merges per-source training CSVs into training_data.csv
├── england/                # England scrapers
│   ├── dfe.py              # GOV.UK education (DfE, Ofsted, Ofqual, ESFA...)
│   ├── epi.py              # Education Policy Institute
│   ├── nuffield.py         # Nuffield Foundation
│   ├── fftlabs.py          # FFT Education Datalab
│   └── fed.py              # Foundation for Educational Development
├── scotland/               # Future: Scottish Government, Education Scotland...
└── ireland/                # Future: Gov.ie, NCCA, Teaching Council...

data/                       # Gitignored — stored locally only
├── training/
│   ├── england/            # Per-source CSVs (2023–2025)
│   ├── scotland/           # Future (Phase 2)
│   ├── ireland/            # Future (Phase 2)
│   └── training_data.csv   # Merged, deduplicated training corpus
└── inference/
    ├── england/            # Weekly merged CSVs from Jan 2026
    ├── scotland/           # Phase 1 test corpus + weekly
    └── ireland/            # Phase 1 test corpus + weekly

docs/
├── decisions.md            # Architectural and data decisions
├── datasets.md             # Dataset schemas and descriptions
└── ethics.md               # Ethical considerations

x_ERP_newsletter_automation/   # Newsletter parsing pipeline (future separate repo)
experiments/                    # Exploratory notebooks
```

---

## Adding a new source

Five steps — always the same pattern regardless of country or source type:

**1.** Write the scraper in `src/<country>/sourcename.py` using the standard interface:
```python
def scrape_sourcename(since_date=None, until_date=None, output_path=None, append=False):
    # scrape articles, return list of dicts with url, title, date, text
    return all_articles
```

**2.** Register in `src/run.py` — add to `SCRAPERS`, `SOURCE_META`, and `TRAINING_FILENAMES`

**3.** Add to `src/merge.py` — add an entry to `SOURCES` (or `load_gov()` equivalent for government sources with extra columns)

**4.** Run the retrospective scrape: `python src/run.py --country eng`

**5.** Regenerate training data: `python src/merge.py`

See [docs/decisions.md](docs/decisions.md) for full detail on the source selection criteria.

---

## Data schema

All output CSVs share the same columns:

| Column | Description |
|---|---|
| `url` | Source article URL |
| `title` | Article title |
| `date` | Publication date (YYYY-MM-DD) |
| `text` | Full article body text |
| `source` | Source key (`gov`, `epi`, `nuffield`, `fft`, `fed`, `schoolsweek`) |
| `country` | Jurisdiction (`eng`, `sco`, `irl`) |
| `type` | Source type (`government`, `think_tank`, `ed_journalism`, `ed_res_org`, `prof_body`) |
| `institution_name` | Publishing institution name |

See [docs/datasets.md](docs/datasets.md) for full dataset descriptions.

---

## Installation

```bash
pip install -r requirements.txt
```

Key dependencies: `requests`, `beautifulsoup4`, `pandas`, `python-dateutil`

---

## Ethical considerations

All data scraped by this pipeline is publicly available. See [docs/ethics.md](docs/ethics.md) for a full discussion of ethical considerations including data provenance, storage, and the politics of AI-assisted policy analysis.

---

## Related projects

- **EduAtlas analysis** — topic modelling and sentiment analysis on this corpus (separate repo)
- **ERP newsletter automation** — `x_ERP_newsletter_automation/` in this repo, future separate repo
