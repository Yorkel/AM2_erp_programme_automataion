# Current Newsletter Curation Process

> Documented from observation and existing materials. Items marked **[CHECK]** need verification with the curators (director and research assistant).

---

## Overview

The ERP Weekly Newsletter has run since July 2023. It is curated weekly by two members of the ERP team: the programme director and a research assistant. Each issue contains approximately 12 articles organised under fixed section headings.

**[CHECK] Approximate time cost per week — is ~7 hours accurate? How is it split between the two curators?**

---

## Step 1: Monitoring sources

The team subscribes to a mix of external email newsletters and manually checks websites that do not send newsletters.

**How sources arrive:**

| Type | How monitored | Examples |
|---|---|---|
| Email newsletter | Direct inbox | Schools Week, EPI, Nuffield, EEF, BERA, HEPI, NFER |
| Manual website check | Curator browses site | Children's Commissioner, Ofsted, Education Select Committee, ASCL |
| Internal email | Forwarded by colleague | Institute for Government (forwarded by Gemma), UCL IOE bulletin |

**[CHECK] Who monitors which sources — is it divided between the director and RA, or do both review everything?**

**[CHECK] Is there a fixed day/time of week when monitoring happens, or is it ad hoc across the week?**

**[CHECK] Roughly how many articles/items do they encounter across all sources in a typical week before filtering?**

---

## Step 2: Initial filtering (include / exclude)

As curators read/scan each source, they decide whether an article is relevant enough to consider for the newsletter.

**Criteria for inclusion (inferred — [CHECK] these with curators):**

- Relevant to UK education policy, research, or practice
- From the current week (or very recent)
- Adds something new — not a repeat of something already covered recently
- Fits at least one of the newsletter sections

**Criteria for exclusion (inferred):**

- Too narrow/specialist (e.g. single-school news, highly technical methodology papers)
- Already covered in a recent issue
- Duplicates another article already shortlisted this week
- Doesn't fit any section

**[CHECK] Do curators keep a shortlist somewhere during the week (e.g. a running doc, starred emails, bookmarks), or do they compile everything in one sitting?**

---

## Step 3: Section assignment

Each shortlisted article is assigned to one of the newsletter's section headings.

**Current fixed sections (as of early 2026):**

| Section | Content type |
|---|---|
| Update from Programme | Internal ERP events, announcements — always manual |
| Update from PI [Name] | Named PI research updates — always manual |
| Teacher recruitment, retention & development | Policy, research and practice on the teaching workforce |
| EdTech | Technology in education, digital tools, AI in schools |
| Political environment and key organisations | Government policy, parliamentary activity, sector organisations |
| Four Nations | Education news from Scotland, Wales, Northern Ireland |
| Research – Practice – Policy | Research outputs with clear policy or practice implications |
| What matters in education? | Broader context — inequality, poverty, mental health, social issues affecting education |

**[CHECK] Are these the definitive current sections? Are there any that appear only occasionally vs always?**

**[CHECK] How do curators decide when an article could fit two sections? Is there a priority order?**

**[CHECK] Is there a target number of articles per section per week, or a minimum/maximum?**

---

## Step 4: Deduplication

When multiple sources cover the same story, curators select one version to include.

**[CHECK] How often does this happen in a typical week?**

**[CHECK] What makes one version preferable over another — source authority, description quality, link?**

**[CHECK] Is deduplication done within the current week only, or do curators also check against recent past issues?**

---

## Step 5: Writing descriptions

For each included article, a short editorial description is written (typically 2–5 sentences).

**[CHECK] Who writes these — one person, or shared? Is it the same person who selected the article?**

**[CHECK] Are descriptions written from memory/skim reading, or does the curator re-read the article at this point?**

**[CHECK] Do descriptions sometimes draw on the source's own abstract/summary, or are they always written from scratch?**

---

## Step 6: Compiling and sending

**[CHECK] What format is the newsletter drafted in — Word, email client, HTML template, something else?**

**[CHECK] How is it sent — MailChimp, direct email, another platform?**

**[CHECK] Is there a review/sign-off step before it goes out?**

---

## What stays manual regardless of automation

Some parts of the newsletter cannot and should not be automated:

- **Update from Programme** — internal ERP news, events, and announcements
- **Update from PI [Name]** — direct from named researchers; requires personal contact
- **Editorial judgement calls** — deciding whether an article is actually good enough, even if it fits a section
- **Writing descriptions** — these carry the programme's voice; automation would produce drafts, not final copy
- **Final sign-off** — a human always reviews before distribution

---

## Summary of key unknowns for system design

| Question | Why it matters |
|---|---|
| How many articles are reviewed vs included per week? | Sets the scale of the gathering/filtering tool |
| When is section assigned — before or after description? | Determines whether classifier uses title-only or title+description |
| Do curators use any existing tool to manage the shortlist? | Determines where classifier output is surfaced |
| How often do cross-source duplicates occur? | Determines priority of deduplication vs classification |
| What counts as "too similar to a recent issue"? | Defines scope of deduplication (within-week vs cross-week) |
