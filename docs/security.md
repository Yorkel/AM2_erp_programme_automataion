# Security Considerations

This document outlines the security practices for the EduAtlas scraping pipeline. This is a research project; the threat model is primarily accidental credential exposure, not adversarial attack.

---

## What this repo does and doesn't handle

This repo is a **data collection pipeline only**. It scrapes publicly available documents, writes CSVs locally, and (via `seed_supabase.py`, not yet built) pushes them to Supabase. It does not handle user authentication, personal data, or payment information.

---

## API Keys and Secrets

| Practice | Status |
|---|---|
| All credentials stored as environment variables | ✅ Implemented |
| `.env` excluded from version control via `.gitignore` | ✅ Implemented |
| No API keys required for current scrapers (all public endpoints) | ✅ Verified |
| Pre-commit secrets scanning hook (`detect-secrets`) | ✅ Installed — blocks commits containing strings that look like API keys |
| GitHub Actions secrets (for `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`) | ⬜ Required when Actions workflow is built (Step 6) |

**Baseline scan result (2026-02-26):** 4 flags found, all confirmed false positives — base64-encoded PNG cell outputs in `x_ERP_newsletter_automation/notebooks/organisations.ipynb`. No real secrets present in the repository.

---

## Database Security

| Practice | Status |
|---|---|
| Row Level Security (RLS) enabled on Supabase `articles` table | ⬜ Required before any data is inserted — see `docs/decisions.md` §15 |
| Public access explicitly disabled; permissions granted on least-privilege basis | ⬜ Required when Supabase is set up |
| `SUPABASE_SERVICE_KEY` used server-side only, never in frontend code | ✅ Policy (key not yet in use) |
| Database policies reviewed when schema changes | ⬜ Ongoing practice to maintain |

---

## AI-Assisted Development

Claude Code is used to assist with code review and generation. All code is reviewed before committing.

---

## Dependency Management

- `requirements.txt` uses pinned versions throughout ✅
- No known vulnerable dependencies at time of last update
- If this repo becomes public, enable GitHub Dependabot alerts in repository Settings → Security

---

## Reporting a Vulnerability

If you identify a security issue in this project, please contact [your email] rather than opening a public issue.

---

## Known Limitations

- This is a research project under active development
- Supabase RLS policies are not yet in place (Supabase not yet set up)
- The project should not be used to process sensitive personal data
