# EduAtlas Scraping — Datasets Description

All data files are gitignored and stored locally. These datasets are outputs of the 6 source scrapers (SchoolsWeek, GOV.UK, EPI, Nuffield, FFT, FED).

---

## data05_full_articles_selected/
Individual CSV files, one per source. Each contains articles scraped 2023–2025.

- **schoolsweek_articles_2023_2025.csv** — Schools Week news articles. ~12MB.
  Columns: `url`, `title`, `date` (YYYY-MM-DD), `text`

- **govuk_education_articles_2023_2025.csv** — UK Government education news and policy, filtered to core education bodies (DfE, Ofsted, Ofqual, ESFA, Office for Students, etc.).
  Columns: `url`, `title`, `from`, `date`, `text`, `core_education`, `primary_org`

- **epi_articles_2023_2025.csv** — Education Policy Institute publications.
  Columns: `url`, `title`, `date`, `text`

- **nuffield_articles_2023_2025.csv** — Nuffield Foundation news and events.
  Columns: `url`, `title`, `date`, `text`

- **fft_education_datalab_blog.csv** — FFT Education Datalab blog posts.
  Columns: `url`, `title`, `date`, `text`

- **fed_news_resources.csv** — Foundation for Educational Development news.
  Columns: `url`, `title`, `date`, `text`

## data06_full_retrospective/
**full_retro.csv** — All 6 sources merged into a single dataset. ~17MB.

Columns: `url`, `title`, `date`, `text`, `source`, `type`, `institution_name`

Source values: `schoolsweek`, `gov`, `epi`, `nuffield`, `fft`, `fed`

Type values: `ed_journalism`, `government`, `think_tank`, `ed_res_org`, `prof_body` 
