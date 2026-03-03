#This script automatically parses all newsletter HTML files, extracts each item's theme, subtheme, title, description, and link (with full cleaning, URL normalisation, and deduplication), and saves the structured dataset as newsletter_items.csv for downstream analysis.

import os
import re
import uuid
from glob import glob
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

from bs4 import BeautifulSoup
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
FOLDER = "/workspaces/ERP_Newsletter/data/data00_html_15.10.2025"
OUTPUT_CSV = "/workspaces/ERP_Newsletter/data/data01_newsletter_items/newsletter_items.csv"

# Theme & subtheme bars (add shades seen across issues)
DARK_BLUE_BG = {c.upper() for c in [
    "#002060", "#1F3864", "#203864", "#00205B", "#042854", "#001F60"
]}
GREY_BG = {c.upper() for c in [
    "#DEEAF6", "#E7E6E6", "#D9D9D9", "#A5DAE9", "#D9E2F3", "#DAE3F3"
]}

# Titles that are just callouts
CALLOUT_PREFIXES = re.compile(
    r'^(Full\s+(story|report|paper|article)|Read\s+more|Helpful\s+infographic|More|See\s+more|Watch|Recording)\b',
    re.I
)

# Anchor-only tokens that are not real titles
ANCHOR_ONLY_TOKENS = {
    "more", "read more", "report", "paper", "full report", "full story",
    "youtube", "tes", "gov.uk", "schoolsweek", "bera", "book now", "book on this link"
}

SAFE_HOSTS = {
    "eur01.safelinks.protection.outlook.com",
    "safelinks.protection.outlook.com",
    "nam01.safelinks.protection.outlook.com",
    "emea01.safelinks.protection.outlook.com",
}

TRACK_PARAMS = {
    "utm_source","utm_medium","utm_campaign","utm_term","utm_content",
    "mkt_tok","mc_cid","mc_eid","gclid","fbclid","igshid","utm_name"
}

# -----------------------------
# URL NORMALISATION / DEDUPE HELPERS
# -----------------------------
def is_safelink(u: str) -> bool:
    try:
        return urlparse(u).netloc.lower() in SAFE_HOSTS
    except Exception:
        return False

def strip_tracking(u: str) -> str:
    try:
        p = urlparse(u)
        q = parse_qs(p.query, keep_blank_values=True)
        q2 = {k: v for k, v in q.items() if k.lower() not in TRACK_PARAMS}
        return urlunparse(p._replace(query=urlencode(q2, doseq=True)))
    except Exception:
        return u

def canonical_url(u: str) -> str:
    """Prefer original src already applied; also unwrap SafeLinks and strip trackers."""
    if not u:
        return ""
    u = u.strip()
    # unwrap Office SafeLinks if no 'originalsrc' was captured
    if is_safelink(u):
        try:
            q = parse_qs(urlparse(u).query)
            inner = q.get("url", []) or q.get("URL", [])
            if inner:
                u = inner[0]
        except Exception:
            pass
    u = strip_tracking(u)
    # normalise scheme/host/path
    try:
        p = urlparse(u)
        path = p.path.rstrip("/") or "/"
        u = urlunparse((p.scheme.lower() or "https", p.netloc.lower(), path, "", p.query, ""))
    except Exception:
        pass
    return u

def slug_title(t: str) -> str:
    t = (t or "").strip().lower()
    t = re.sub(r'\s+', ' ', t)
    # trim common addenda
    t = re.sub(r'\s*\(paid subscription required\)\s*$', '', t)
    return t

# -----------------------------
# COLOUR / STYLE HELPERS
# -----------------------------
def _rgb_to_hex(raw: str):
    """Convert 'rgb(r,g,b)' to '#RRGGBB'."""
    if not raw:
        return None
    m = re.search(r'rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)', raw, re.I)
    if not m:
        return None
    r, g, b = (int(m.group(i)) for i in (1, 2, 3))
    return f"#{r:02X}{g:02X}{b:02X}"

def _extract_bg_from_style(style: str):
    """Pull background/background-color from style; normalise rgb->hex."""
    style = style or ""
    m = re.search(r'background(?:-color)?:\s*([^;]+)', style, re.I)
    if not m:
        return None
    raw = m.group(1).strip()
    return _rgb_to_hex(raw) or raw

def get_bg_color(tag):
    """
    Return normalised background colour (#RRGGBB or named) for a table-like block.
    Checks the element's style/bgcolor, then first <td>'s style/bgcolor.
    """
    if not tag:
        return None

    # Element style
    c = _extract_bg_from_style(tag.get("style"))
    if not c:
        # Element bgcolor attr
        c = (tag.get("bgcolor") or "").strip()

    # First cell style/bgcolor for tables
    if not c and tag.name == "table":
        td = tag.find("td")
        if td:
            c = _extract_bg_from_style(td.get("style")) or (td.get("bgcolor") or "").strip()

    c = _rgb_to_hex(c) or c
    return c.upper() if c else None

# -----------------------------
# HTML TEXT HELPERS
# -----------------------------
def first_text(el):
    """Inner text collapsed and trimmed."""
    return " ".join(el.get_text(" ", strip=True).split())

def prefer_original_href(a):
    """Prefer Outlook ‘originalsrc’ if present; else href."""
    return a.get("originalsrc") or a.get("href")

def find_newsletter_number_and_date(soup):
    # e.g. "ERP Newsletter #24" or "Newsletter – #1" / number may appear in subject / body
    full_text = soup.get_text(" ", strip=True)
    num = None
    m = re.search(r'\bERP?\s*Newsletter\s*[–—-]?\s*#?\s*(\d+)\b', full_text, re.I)
    if m:
        num = int(m.group(1))
    else:
        m2 = re.search(r'\bNewsletter\s*[–—-]?\s*#?\s*(\d+)\b', full_text, re.I)
        if m2:
            num = int(m2.group(1))

    # Date: e.g. "11 July 2023" (avoid times like "17:30")
    d = None
    md = re.search(r'\b(\d{1,2}\s+[A-Za-z]+\s+\d{4})\b', full_text)
    if md:
        d = md.group(1)

    return num, d

def _is_visually_bold(el):
    """Return True if element is visually bold."""
    if el.find(["b", "strong"]):
        return True
    style = (el.get("style") or "").lower()
    if "font-weight" in style and ("bold" in style or re.search(r'font-weight\s*:\s*(6|7|8|9)\d{2}', style)):
        return True
    # Headings are bold-ish semantically
    if el.name in ("h1","h2","h3","h4","h5","h6"):
        return True
    return False

def _mostly_link_text(el):
    """Heuristic: is the paragraph mostly just a link?"""
    text = first_text(el)
    if not text:
        return False
    links = el.find_all("a")
    if not links:
        return False
    link_text = " ".join(a.get_text(" ", strip=True) for a in links)
    return len(link_text) >= 0.8 * len(text)

def _is_anchor_only(el):
    """True if paragraph is essentially a single short anchor token."""
    txt = first_text(el).strip().lower()
    only_a = (len(el.find_all()) == 1 and el.find("a") is not None)
    return (txt in ANCHOR_ONLY_TOKENS) or (only_a and txt in ANCHOR_ONLY_TOKENS)

def is_title_candidate(el):
    """
    Stricter test for titles:
    - visually bold or is a heading
    - short-ish (<= 28 words)
    - not callout like 'Full story', 'Read more', etc.
    - not mostly link-only
    - not a short anchor token
    """
    if not _is_visually_bold(el):
        return False

    text = first_text(el)
    if not text:
        return False

    if len(text.split()) > 28:
        return False

    if CALLOUT_PREFIXES.search(text):
        return False

    if _mostly_link_text(el):
        return False

    if _is_anchor_only(el):
        return False

    return True

def iter_blocks(soup):
    """
    Yield the document's main flow as a sequence of <table>, <p>, and headings in visual order.
    Robust for Word/Outlook HTML.
    """
    body = soup.body or soup
    queue = []

    def collect(node):
        for child in getattr(node, "children", []):
            name = getattr(child, "name", None)
            if name in ("table", "p", "h1", "h2", "h3", "h4", "h5", "h6"):
                queue.append(child)
            elif name in ("div", "section"):
                collect(child)
            # ignore others

    collect(body)
    return queue

# -----------------------------
# FALLBACK PARSER (for issues like #86 / soft titles)
# -----------------------------
def fallback_parse_by_link(soup, newsletter_no, issue_date):
    """
    Fallback for issues where item titles aren't clearly bold.
    Walk the blocks; when inside a theme (dark-blue table), collect <p> lines into items.
    First non-empty <p> becomes the title; close item when a link appears or a new bar appears.
    """
    rows = []
    blocks = iter_blocks(soup)

    current_theme = None
    current_subtheme = None

    title = None
    desc_parts = []
    link = None

    def flush_item():
        nonlocal title, desc_parts, link
        t = " ".join((title or "").split())
        if t and (desc_parts or link):
            rows.append({
                "id": str(uuid.uuid4()),
                "newsletter_number": newsletter_no,
                "issue_date": issue_date,
                "theme": current_theme,
                "subtheme": current_subtheme,
                "title": t,
                "description": " ".join(" ".join(desc_parts).split()) or None,
                "link": canonical_url(link) if link else ""
            })
        title, desc_parts, link = None, [], None

    for el in blocks:
        if el.name == "table":
            bg = get_bg_color(el)

            # New theme/subtheme boundaries break the current item
            if bg and (bg in DARK_BLUE_BG or bg in GREY_BG):
                flush_item()

            if bg and bg in DARK_BLUE_BG:
                current_theme = first_text(el)
                current_subtheme = None
                continue
            elif bg and bg in GREY_BG:
                current_subtheme = first_text(el)
                continue

        if el.name == "p" and (current_theme or current_subtheme):
            txt = first_text(el)
            a = el.find("a")
            href = canonical_url(prefer_original_href(a) or "") if a else ""

            if not title and txt and not CALLOUT_PREFIXES.search(txt) and not _is_anchor_only(el):
                title = txt
            elif txt and not CALLOUT_PREFIXES.search(txt):
                desc_parts.append(txt)

            if href and not link:
                link = href
                flush_item()

    flush_item()
    return rows

# -----------------------------
# MAIN PARSER
# -----------------------------
def parse_file(path):
    html = open(path, "r", encoding="utf-8", errors="ignore").read()
    soup = BeautifulSoup(html, "html.parser")

    newsletter_no, issue_date = find_newsletter_number_and_date(soup)
    current_theme = None
    current_subtheme = None

    rows = []
    blocks = iter_blocks(soup)
    i = 0
    while i < len(blocks):
        el = blocks[i]

        # THEME / SUBTHEME via coloured tables
        if el.name == "table":
            bg = get_bg_color(el)
            if bg and bg in DARK_BLUE_BG:
                current_theme = first_text(el)
                current_subtheme = None
                i += 1
                continue
            elif bg and bg in GREY_BG:
                current_subtheme = first_text(el)
                i += 1
                continue

        # NEWS ITEM: title (strict candidate), then description/link paragraphs
        if el.name in ("p", "h1", "h2", "h3", "h4", "h5", "h6") and is_title_candidate(el) and (current_theme or current_subtheme):
            title = first_text(el)

            # Link from the title paragraph if present
            link = ""
            a_in_title = el.find("a")
            if a_in_title:
                href = (prefer_original_href(a_in_title) or "").strip()
                if href:
                    link = canonical_url(href)

            desc_parts = []
            j = i + 1
            while j < len(blocks):
                nxt = blocks[j]

                if nxt.name == "table":
                    bg = get_bg_color(nxt)
                    if bg and (bg in DARK_BLUE_BG or bg in GREY_BG):
                        break

                # Stop at next title-like paragraph
                if nxt.name in ("p", "h1", "h2", "h3", "h4", "h5", "h6") and is_title_candidate(nxt):
                    break

                if nxt.name == "p":
                    txt = first_text(nxt)
                    if txt and not CALLOUT_PREFIXES.search(txt) and not _is_anchor_only(nxt):
                        desc_parts.append(txt)

                    if not link:
                        a = nxt.find("a")
                        if a:
                            href = (prefer_original_href(a) or "").strip()
                            if href:
                                link = canonical_url(href)
                j += 1

            description = " ".join(desc_parts).strip() or None
            rows.append({
                "id": str(uuid.uuid4()),
                "newsletter_number": newsletter_no,
                "issue_date": issue_date,
                "theme": current_theme,
                "subtheme": current_subtheme,
                "title": title,
                "description": description,
                "link": link
            })
            i = j
            continue

        i += 1

    # Fallback for issues with non-bold titles (e.g., #50, #86)
    extra = fallback_parse_by_link(soup, newsletter_no, issue_date)

    # -----------------------------
    # ROBUST MERGE & DEDUPE
    # -----------------------------
    def score_row(r):
        # prefer non-safelink + has link + longer description
        link = r.get("link") or ""
        desc = r.get("description") or ""
        return (
            0 if is_safelink(link) else 1,
            1 if link else 0,
            len(desc)
        )

    def row_key(r):
        t = slug_title(r.get("title"))
        l = canonical_url(r.get("link") or "")
        if l:
            return ("t+l", t, l)
        # No link: fall back to theme to reduce dupes within same section
        return ("t+theme", t, (r.get("theme") or "").strip().lower())

    bucket = {}
    for r in rows + extra:
        # normalise fields used in keys
        r["title"] = (r.get("title") or "").strip()
        r["link"] = canonical_url(r.get("link") or "")
        k = row_key(r)
        if k not in bucket or score_row(r) > score_row(bucket[k]):
            if k in bucket:
                existing = bucket[k]
                # merge description if missing on the kept one
                if not existing.get("description"):
                    existing["description"] = r.get("description")
                # prefer better row’s other fields
                for fld in ("id","newsletter_number","issue_date","theme","subtheme","title","link"):
                    existing[fld] = r.get(fld, existing.get(fld))
            else:
                bucket[k] = r

    rows = list(bucket.values())
    return rows

# -----------------------------
# DRIVER
# -----------------------------
def main():
    all_rows = []
    files = sorted(glob(os.path.join(FOLDER, "newsletter_*.html")))
    if not files:
        print("No newsletter_*.html files found. Check FOLDER path.")
        return

    for fp in files:
        try:
            rows = parse_file(fp)
            if not rows:
                print(f"⚠️  No rows parsed from {os.path.basename(fp)}")
            all_rows.extend(rows)
        except Exception as e:
            print(f"❌ Error parsing {os.path.basename(fp)}: {e}")

    df = pd.DataFrame(all_rows, columns=[
        "id", "newsletter_number", "issue_date",
        "theme", "subtheme", "title", "description", "link"
    ])
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Wrote {len(df)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
