# ERP Newsletter Automation — Datasets Description

All data files are gitignored and stored locally. Data pipeline: raw HTML → parsed items → cleaned items → full articles.

---

## data00_html_15.10.2025/
Raw ERP newsletter HTML files (newsletter_01.html through newsletter_87.html), saved from email via Power Automate → OneDrive. Snapshot taken 15 October 2025. Most recent issue: newsletter_87 dated 10 October 2025.

## data01_newsletter_items/
**newsletter_items.csv** — Raw output of `extract00_newsletters.py`. One row per news item extracted from the HTML newsletters. ~1,668 rows before deduplication.

Columns: `id`, `newsletter_number`, `issue_date`, `theme`, `subtheme`, `title`, `description`, `link`

## data02_cleaning/
Intermediate files produced during the cleaning and theme-mapping process (notebooks 0 and 1).

- `theme_subtheme_counts.csv` — frequency table of raw theme/subtheme strings
- `unique_domains_programme_updates.csv` — unique domains from ERP project update items
- `organisation_category_mapping.csv` — manual mapping of domains to organisation names and sector categories

## data03_newsletter_items_clean/
Fully cleaned and processed newsletter items.

- **items_all_themes.csv** — All newsletter items with standardised themes. ~1,192 rows after deduplication and cleaning.
  Columns: `id`, `newsletter_number`, `issue_date`, `theme`, `subtheme`, `title`, `description`, `link`, `organisation`, `org_category`, `org_broad_category`, `text`, `text_character_count`, `text_word_count`

- **items_final_themes.csv** — Final cleaned dataset with organisations and sector categories assigned, combined text field, ready for analysis. ~903 rows.

- **programme_updates.csv** — Subset filtered to ERP Project / Programme Updates theme only. Includes all enriched metadata and text fields.

## data04_full_articles_scraped/
Output of `extract01_full_article.py`. Full article text scraped by following links from newsletter items.

- **newsletter_full_articles.csv** — One row per unique article URL. 741 successfully scraped, 160 failed.
  Columns: `article_id`, `link_canonical`, `domain`, `article_title`, `article_text`, `status`, `failure_reason`

- **newsletter_full_articles_with_items.csv** — Merged: newsletter item metadata + full article text.

- **successfully_scraped.csv** — Articles with `status == "ok"` only.

- **uk_government_links.csv** — Extracted government URLs for reference.
