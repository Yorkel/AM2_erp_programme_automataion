# Datasets

All data files are gitignored and stored locally.

**Data pipeline:** raw HTML → extracted items → cleaned items → full articles

---

## Stage 0 — Raw newsletters (HTML)

**Location:** `data/raw/newsletters_html/` (originally `data00_html_15.10.2025/`)

HTML exports of every ERP Weekly Newsletter issue, saved from email via Power Automate → OneDrive. Each file is one newsletter issue.

**Coverage:** Issues 3–102 (issues 1, 2, and a handful of others are missing). Filenames are inconsistent — mix of `ERP Newsletter ##.html`, `ESRC Education Research Programme Newsletter ##.html`, and some prefixed with `FW-`.

**Volume:** 102 files. Snapshot taken 15 October 2025; most recent issue at that point: newsletter_87 dated 10 October 2025.

**Status:** Processed through issue 87. Issues 88–102 need to be run through the extraction script.

---

## Stage 1 — Extracted newsletter items (CSV)

**Location:** `data/processed/newsletter_items_nov.csv` (also `data01_newsletter_items/newsletter_items.csv`)

Structured extraction of all news items from the HTML newsletters. Each row is one article included in one newsletter issue. Produced by `src/extract00_newsletters.py` using BeautifulSoup.

**Coverage:** Issues 1–87, October 2023 – May 2025

**Volume:** ~1,668 rows before deduplication

**Columns:**

| Column | Description |
|---|---|
| `id` | Row identifier |
| `newsletter_number` | Issue number |
| `issue_date` | Date of that newsletter issue |
| `theme` | Section heading the article was placed under (curator-assigned label) |
| `subtheme` | Sub-section heading where used (often empty in later issues) |
| `title` | Article title |
| `description` | Curator-written short description of the article |
| `link` | URL of the source article |

**Known issues:**
- **68 unique `theme` values** — many are label variants of the same section (e.g. "Political environment and key organisations" vs "Political landscape & key organisations"), PI names parsed as section headers, and some rows where the unsubscribe footer was extracted as a theme
- Label normalisation needed before use as training data — see map below
- Issues 88–102 not yet extracted (~180 additional rows estimated)

**Label normalisation map:**

| Raw label(s) | Normalised label | Keep for training? |
|---|---|---|
| What matters in education? / What Matters in Education? | `what_matters` | Yes |
| Political environment and key organisations / Political landscape & key organisations / Political landscape - the election / Political landscape across Four Nations & key organisations | `political_environment` | Yes |
| Teacher recruitment, retention & development | `teacher_workforce` | Yes |
| EdTech | `edtech` | Yes |
| Research – Practice – Policy / Education, Policy & Practice | `research_practice_policy` | Yes |
| Four Nations / Four Nations Landscape / Four Nations landscape / 4 Nations / 4 Nations & key organisations | `four_nations` | Yes |
| Updates from the programme / Updates from the Programme / Programme news / Programme Update / Programme update / Update from the ESRC Education Research Programme / Update from UKRI / Updates from the ESRC / Updates from UKRI | `internal_programme` | No — always manual |
| Updates from the projects / Update from the ERP projects / Updates from the ERP projects / Project news / News from the Projects / News from the projects / Update from the projects / Peer reviewed articles from the ERP projects / Peer reviewed publications from the ERP projects | `internal_projects` | No — always manual |
| PI name strings (e.g. "Towards equity focused approaches to EdTech: a socio-technical perspective PI: Rebecca Eynon") | parsing noise / PI update | No — parsing artefact |
| Unsubscribe footer text | parsing noise | No — parsing artefact |
| Thematic roundup / Thematic Roundup / Relevant Research / Research / Other Research / Reports / Other Reports / DfE / EEF / ESRC / Calls for evidence / Opportunities / Opportunities for funding / Events / Relevant Events / Conferences / Seminar series topics / Seminar topics / Opportunities to blog | early-format labels | Review individually — some map to core sections |

**Estimated clean training set after normalisation:** ~1,200–1,400 rows across 6 sections.

---

## Stage 2 — Cleaning intermediates

**Location:** `data02_cleaning/`

Intermediate files from the cleaning and theme-mapping process (notebooks 0 and 1):

- `theme_subtheme_counts.csv` — frequency table of raw theme/subtheme strings
- `unique_domains_programme_updates.csv` — unique domains from ERP project update items
- `organisation_category_mapping.csv` — manual mapping of domains to organisation names and sector categories

---

## Stage 3 — Cleaned newsletter items

**Location:** `data03_newsletter_items_clean/`

- **`items_all_themes.csv`** — All newsletter items with standardised themes. ~1,192 rows after deduplication and cleaning.
  Columns: `id`, `newsletter_number`, `issue_date`, `theme`, `subtheme`, `title`, `description`, `link`, `organisation`, `org_category`, `org_broad_category`, `text`, `text_character_count`, `text_word_count`

- **`items_final_themes.csv`** — Final cleaned dataset with organisations and sector categories assigned, combined text field, ready for analysis. ~903 rows.

- **`programme_updates.csv`** — Subset filtered to ERP Project / Programme Updates theme only. Includes all enriched metadata and text fields.

---

## Stage 4 — Full articles (scraped)

**Location:** `data04_full_articles_scraped/`

Full article text scraped by following links from newsletter items. Produced by `src/extract01_full_article.py`.

- **`newsletter_full_articles.csv`** — One row per unique article URL. 741 successfully scraped, 160 failed.
  Columns: `article_id`, `link_canonical`, `domain`, `article_title`, `article_text`, `status`, `failure_reason`

- **`newsletter_full_articles_with_items.csv`** — Merged: newsletter item metadata + full article text.

- **`successfully_scraped.csv`** — Articles with `status == "ok"` only.

- **`uk_government_links.csv`** — Extracted government URLs for reference.

---

## Outstanding work

**Issues 88–102 not yet extracted.** Files are present in `data/raw/newsletters_html/` but have not been run through the extraction script. Estimated ~15 issues × ~12 items = ~180 additional labelled examples, extending coverage to approximately February 2026.

To process: run `src/extract00_newsletters.py` on the remaining files and append to or create a new version of the items CSV.
