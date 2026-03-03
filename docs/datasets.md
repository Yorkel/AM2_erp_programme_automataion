# Datasets

All datasets for the AM2 newsletter classification project.

---

## 1. Raw newsletters — HTML files

**Location:** `data/raw/newsletters_html/`

**What it is:** HTML exports of every ERP Weekly Newsletter issue, exported from the original Word/email format. Each file is one newsletter issue.

**Coverage:** Issues 3–102 (some gaps — issues 1, 2, and a handful of others are missing). Filenames are inconsistent — mix of `ERP Newsletter ##.html`, `ESRC Education Research Programme Newsletter ##.html`, and some prefixed with `FW-`.

**Volume:** 102 files

**Status:** Raw, not yet processed beyond issue 87. Issues 88–102 need to be run through the extraction script.

**How it was collected:** Exported from the team's email archive by the curators.

---

## 2. Processed newsletter items — CSV

**Location:** `data/processed/newsletter_items_nov.csv`

**What it is:** Structured extraction of all news items from the HTML newsletters. Each row is one article included in one newsletter issue. This is the primary training dataset for the classifier.

**Coverage:** Issues 1–87, October 2023 – May 2025

**Volume:** 1,668 rows

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

**How it was produced:** BeautifulSoup parser (`x_ERP_newsletter_automation/src/extract00_newsletters.py`) run on the HTML files, October 2025.

**Known issues:**
- **68 unique `theme` values** — many are label variants of the same section (e.g. "Political environment and key organisations" and "Political landscape & key organisations"), PI names parsed as section headers, and a few rows where the unsubscribe footer text was extracted as a theme
- **Label normalisation needed** before use as training data — see table below
- Issues 88–102 not yet extracted

**Label normalisation map (draft):**

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

## 3. External sources list

**Location:** `x_ERP_newsletter_automation/docs/external_sources.md`

**What it is:** The list of ~55 external sources the curators monitor weekly. Includes external organisations (think tanks, government bodies, unions, research orgs) and internal UCL/IOE sources.

**Structure:** Name, website URL, whether they send an email newsletter, whether the curator manually checks the site.

**Status:** Maintained manually. Some entries are outdated (CAPE and IPPO are noted as closed).

**Use in the pipeline:** This list defines the sources the gathering tool needs to monitor. Some can be scraped via RSS or website crawl; others deliver content via email newsletter (harder to automate).

---

## 4. Newsletters not yet processed (issues 88–102)

**Location:** `data/raw/newsletters_html/` — files for issues 88–102 are present but not extracted

**What is needed:** Run `x_ERP_newsletter_automation/src/extract00_newsletters.py` on the remaining files and append to `newsletter_items_nov.csv` (or create a new version).

**Estimated additional rows:** ~15 issues × ~12 items = ~180 more labelled examples, extending coverage to approximately February 2026.
