import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

# ------------------------------------------------------
# CONFIG
# ------------------------------------------------------
BASE = "https://www.gov.uk"
START_URL = (
    "https://www.gov.uk/search/news-and-communications"
    "?level_one_taxon=c58fdadd-7743-46d6-9629-90bb3ccc4ef0"
    "&order=updated-newest"
)

OUTPUT = "/workspaces/ERP_Newsletter/data/data05_full_articles_selected/govuk_dfe_articles_2023_2025.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (GovUK Education Scraper)"
}

MAX_OLD_PAGES = 3   # ⬅️ stop after 3 consecutive pages with no 2023+ content

# ------------------------------------------------------
# LINK EXTRACTION
# ------------------------------------------------------
def extract_links(html):
    soup = BeautifulSoup(html, "html.parser")
    return [
        BASE + a["href"]
        for a in soup.select("li.gem-c-document-list__item a[href]")
    ]


def extract_next_page(html):
    soup = BeautifulSoup(html, "html.parser")
    next_btn = soup.select_one("div.govuk-pagination__next a")
    return BASE + next_btn["href"] if next_btn else None


# ------------------------------------------------------
# ROBUST DATE EXTRACTION
# ------------------------------------------------------
def extract_date_robust(soup, url):
    # 1️⃣ Metadata list
    metadata = soup.select_one("dl.gem-c-metadata__list")
    if metadata:
        for dt in metadata.find_all("dt"):
            label = dt.get_text(strip=True).lower()
            dd = dt.find_next_sibling("dd")
            if not dd:
                continue
            if label in ("published:", "updated:"):
                raw = dd.get_text(" ", strip=True)
                try:
                    return datetime.strptime(raw, "%d %B %Y")
                except ValueError:
                    pass

    # 2️⃣ Published-dates blocks
    for block in soup.select("div.gem-c-published-dates"):
        raw = (
            block.get_text(" ", strip=True)
            .replace("Published", "")
            .replace("Updated", "")
            .strip()
        )
        try:
            return datetime.strptime(raw, "%d %B %Y")
        except ValueError:
            pass

    # 3️⃣ Regex fallback
    text = soup.get_text(" ", strip=True)
    match = re.search(
        r"\b(\d{1,2}\s+"
        r"(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+\d{4})\b",
        text,
    )
    if match:
        try:
            return datetime.strptime(match.group(1), "%d %B %Y")
        except ValueError:
            pass

    print(f"❌ DATE NOT FOUND: {url}")
    return None


# ------------------------------------------------------
# SCRAPE SINGLE ARTICLE
# ------------------------------------------------------
def scrape_article(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    # TITLE
    h1 = soup.select_one("h1.gem-c-heading__text, h1.govuk-heading-l")
    title = h1.get_text(strip=True) if h1 else ""

    # FROM (department / body)
    from_org = ""
    metadata = soup.select_one("dl.gem-c-metadata__list")
    if metadata:
        for dt in metadata.find_all("dt"):
            if dt.get_text(strip=True).lower() == "from:":
                dd = dt.find_next_sibling("dd")
                if dd:
                    orgs = [a.get_text(strip=True) for a in dd.find_all("a")]
                    from_org = "; ".join(orgs)

    # DATE
    pub_date = extract_date_robust(soup, url)
    if not pub_date:
        return None

    # ARTICLE TEXT
    main = soup.select_one("main#content")
    if not main:
        return None

    text_parts = []

    for el in main.find_all(["p", "li", "h2"], recursive=True):
        if el.name == "h2" and "share this page" in el.get_text(strip=True).lower():
            break

        txt = el.get_text(strip=True)
        if txt:
            text_parts.append(txt)

    text = "\n".join(text_parts)

    return {
        "url": url,
        "title": title,
        "from": from_org,
        "date": pub_date.strftime("%Y-%m-%d"),
        "text": text,
    }


# ------------------------------------------------------
# MAIN SCRAPER
# ------------------------------------------------------
def scrape_govuk():
    all_articles = []
    seen = set()
    url = START_URL
    page = 1
    old_page_streak = 0

    print("🚀 Starting GOV.UK Education news scrape…")

    while url:
        print(f"\n📄 Page {page}: {url}")
        r = requests.get(url, headers=HEADERS)
        html = r.text

        links = extract_links(html)
        print(f"🔗 Found {len(links)} links")

        page_has_recent = False

        for link in links:
            if link in seen:
                continue
            seen.add(link)

            print(f"   📰 Scraping: {link}")
            result = scrape_article(link)

            if result:
                all_articles.append(result)
                if result["date"] >= "2023-01-01":
                    page_has_recent = True

            time.sleep(0.8)

        # Update stopping logic
        if page_has_recent:
            old_page_streak = 0
        else:
            old_page_streak += 1
            print(
                f"⚠️ Page {page} contains no 2023+ publications "
                f"({old_page_streak}/{MAX_OLD_PAGES})"
            )

        if old_page_streak >= MAX_OLD_PAGES:
            print("⛔ Reached 3 consecutive pre-2023 pages — stopping scrape.")
            break

        url = extract_next_page(html)
        page += 1
        time.sleep(1)

    # FINAL FILTER
    df = pd.DataFrame(all_articles)
    df = df[df["date"] >= "2023-01-01"]

    df.to_csv(OUTPUT, index=False)
    print(f"\n💾 Saved {len(df)} articles to: {OUTPUT}")


# ------------------------------------------------------
# RUN
# ------------------------------------------------------
if __name__ == "__main__":
    scrape_govuk()
