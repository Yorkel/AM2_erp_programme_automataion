# Current Newsletter Curation Process

> Compiled from curator input (NC and Gemma Moss). Items still marked **[CHECK]** need further verification.

---

## Overview

The ERP Weekly Newsletter has run since July 2023. It is curated weekly by two members of the ERP team: the programme director and a researcher. Each issue contains approximately 12 articles organised under fixed section headings.

**Purpose of the automation system:** Not full automation — the goal is to reduce time required by:

- **Section suggestion** — when a relevant article comes in, the system predicts which newsletter section it fits (e.g. EdTech, Four Nations, Research–Practice–Policy), so curators don't have to start from scratch each time.
- **Duplicate flagging** — if two or three sources cover the same story in the same week, the system groups them so the curator can pick the best one rather than read each separately.

To do this, a model will be trained on past newsletter issues.

**Time cost per week (NC):** Up to 7.5 hrs/week total:
- ~3.5–4.5 hrs tangible work: recording items, setting up the newsletter, editing, preparing for dissemination, checking for new subscribers.
- ~3/4 hrs browsing for items and reading them to understand them (~30–45 mins/day across the week).

This could potentially be reduced to ~5 hrs total, but the time saving would come from reading articles less thoroughly — which risks including weaker sources or sharing something unsuitable.

---

## Step 1: Monitoring Sources

The team subscribes to a mix of external email newsletters and manually checks websites that do not send newsletters.

**How sources arrive:**

| Type | How monitored | Examples |
|---|---|---|
| Email newsletter | Direct inbox | Schools Week, EPI, Nuffield, EEF, BERA, HEPI, NFER |
| Manual website check | Curator browses site | Children's Commissioner, Ofsted, Education Select Committee, ASCL |
| Internal email | Email from colleague | — |

**Who monitors sources:** Mostly Gemma and NC, but RF and SK also contribute if something crops up.

**Timing:** Ad hoc across the week — NC monitors most days, usually first thing in the morning or in the evening.

**Volume before filtering:** Roughly 15–20 articles/items encountered per week across all sources.

---

## Step 2: Initial Filtering (Include / Exclude)

As curators read/scan each source, they decide whether an article is relevant enough to consider for the newsletter.

**Criteria for inclusion:**
- Relevant to UK education policy, research, or practice
- From the current week (or very recent)
- Adds something new — not a repeat of something already covered recently
- Fits at least one of the newsletter sections

**Criteria for exclusion (NC):**
- Poor quality or not sufficiently reputable
- Inaccessible to a wide audience (e.g. subscription required — TES is used occasionally but marked as behind a paywall)
- Too narrow/specialist (e.g. single-school news, highly technical methodology papers)
- Already covered in a recent issue
- Duplicates another article already shortlisted this week
- Doesn't fit any section

**Shortlist management:** Curators submit items to a Microsoft Form as they find them during the week. Submissions land in a spreadsheet that acts as the compilation list. This means monitoring and compiling happen continuously across the week, not in one sitting.

---

## Step 3: Section Assignment

Each shortlisted article is assigned to one of the newsletter's fixed section headings.

**Current sections (as of March 2026):**

| Section | Content type |
|---|---|
| Update from Programme | Internal ERP events, announcements — always manual; omitted if no news that week |
| Update from PI | Named PI research and other updates — always manual; omitted if no news that week |
| Teacher recruitment, retention & development | Policy, research and practice on the teaching workforce |
| EdTech | Technology in education, digital tools, AI in schools |
| Political environment and key organisations (PEKO) | Government policy, parliamentary activity, sector organisations |
| Four Nations | Education news from Scotland, Wales, Northern Ireland |
| Research – Practice – Policy (RPP) | Research outputs with clear policy or practice implications |
| What matters in education? | Broader context — inequality, poverty, mental health, social issues affecting education |

**Hardest section to fill:** RPP is consistently the hardest to find articles for. Articles sometimes move between RPP and PEKO.

**When an article fits two sections (NC):** Go by best fit first, but consider which sections have enough items that week. Example: if an article could go in either EdTech or RPP, but RPP has nothing else and EdTech already has something, it goes in RPP.

**Target articles per section:** Minimum 2 if possible (occasionally 1 if there really is nothing else). Maximum 4.

**Section allocation tracking:** Since switching to Microsoft Forms, section allocation and inclusion/exclusion/delayed decisions are tracked in the newsletter spreadsheet. Colour coding has been inconsistently applied.

---

## Step 4: Deduplication

When multiple sources cover the same story, curators select the best version to include. However, multiple sources covering **different angles** on the same topic are not treated as duplicates — these may both be included (e.g. different takes on the Schools White Paper or SEND).

**How often true deduplication is needed (NC):** Roughly once a week, but not every week. When a topic is highly active (e.g. White Paper), different sources may take sufficiently different approaches to both be worth including.

**What makes one version preferable (NC):**
1. Quality of the item (clarity, usefulness to readers)
2. Reputability/authority of the source
3. Avoiding repeating the same source in the same newsletter issue (so selection depends partly on what else is already included that week)

Note: Schools Week often gives concise summaries of policy shifts and may be preferable to the original government source, which can hide controversy or be less readable.

**Checking against past issues (NC):** Yes — the spreadsheet has a column where curators manually record whether a source has been used before, allowing cross-week deduplication checks.

**Source authority vs slant:** The relationship between source and slant matters. Government sources may be authoritative but can hide controversy. Some third-sector organisations act as lobby groups; others as research providers. Understanding this is a key part of editorial judgement.

---

## Step 5: Writing Descriptions

For each included article, a short description is written.

**Who writes it (NC):** Whoever entered the article into the Microsoft Form.

**Title:** Use the title as given by the source. Only substitute a subtitle if the main title is unclear.

**Body:** A summary aimed at interesting readers — this may include a direct quote from the source's own text. Curators try not to rewrite the story in their own words. Finding the right sentence sometimes means reading quite far into an article.

---

## Step 6: Compiling and Sending

**Format (NC):** Drafted directly in email — drafting in Word or another format risks introducing formatting issues.

**How sent (NC):** Direct email, BCC'ing all recipients.

**Review and sign-off process (NC):**
1. NC puts together the draft.
2. GM (Gemma) reviews for editorial purposes and gives colour-coded feedback (deleted / edited / move section).
3. NC makes those changes.
4. RF proofreads.
5. NC makes any final changes and sets up a scheduled send.

---

## What Stays Manual Regardless of Automation

- **Update from Programme** — internal ERP news, events, and announcements
- **Update from PI** — direct from named researchers; requires personal contact
- **Editorial judgement on quality and slant** — deciding whether an article is good enough, and understanding the source–slant relationship (government sources can hide controversy; third-sector sources range from research providers to lobby groups)
- **Writing descriptions** — curators draw on the source's own language; this is a deliberate editorial discipline, not just a style preference
- **Final control over what gets published** — curators want to retain oversight at every stage; automation supports but does not replace their judgement
- **Final sign-off and send** — GM edits, RF proofreads, NC sends

---

## Summary of Key Unknowns for System Design

| Question | Why it matters | Status |
|---|---|---|
| When is section assigned — before or after writing the description? | Determines whether the classifier should use title only or title + description | **[CHECK]** |
| How is the source–slant relationship applied in practice? | Critical for any AI-assisted filtering; examples would help | **[CHECK] examples needed** |
| Are the current sections fully stable, or do new ones appear occasionally? | Affects whether the classifier needs to handle unseen classes | **[CHECK]** |
