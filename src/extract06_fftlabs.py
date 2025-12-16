import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from urllib.parse import urlparse

BASE_URL = "https://ffteducationdatalab.org.uk/blog/"
PAGE_URL = "https://ffteducationdatalab.org.uk/blog/page/{}/"

OUTPUT = "/workspaces/ERP_Newsletter/data/data05_full_articles_selected/fft_education_datalab_blog.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FFTDatalabScraper/1.0)"
}

CUTOFF_YEAR = 2023

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# ---------------------------------------------------------
# Extract article links (exclude archive pages)
# ---------------------------------------------------------
def extract_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith("https://ffteducationdatalab.org.uk/20"):
            path_parts = urlparse(href).path.strip("/").split("/")

            # Expect: YYYY / MM / slug
            if len(path_parts) >= 3:
                links.append(href)

    # preserve order, remove duplicates
    return list(dict.fromkeys(links))


# ---------------------------------------------------------
# Extract full article
# ---------------------------------------------------------
def scrape_article(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    # ---------------------------
    # TITLE
    # ---------------------------
    title_tag = soup.select_one("h2.entry-title")
    if not title_tag:
        print(f"⚠️ Missing title: {url}")
        return None

    title = title_tag.get_text(strip=True)

    # ---------------------------
    # DATE
    # ---------------------------
    meta = soup.select_one("div.fusion-meta-info-wrapper")
    if not meta:
        print(f"⚠️ Missing meta block: {url}")
        return None

    pub_date = None
    for span in meta.find_all("span"):
        text = span.get_text(strip=True)

        if any(month in text for month in MONTHS):
            for fmt in (
                "%dth %B %Y",
                "%dst %B %Y",
                "%dnd %B %Y",
                "%drd %B %Y",
                "%d %B %Y",
            ):
                try:
                    pub_date = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    continue

        if pub_date:
            break

    if not pub_date:
        print(f"⚠️ Failed to parse date: {url}")
        return None

    # ---------------------------
    # STOP CONDITION (YEAR CUTOFF)
    # ---------------------------
    if pub_date.year < CUTOFF_YEAR:
        return "STOP"

    # ---------------------------
    # CONTENT (STOP AT NOTES)
    # ---------------------------
    content = soup.select_one("div.post-content")
    if not content:
        print(f"⚠️ Missing content: {url}")
        return None

    # Remove Notes / footnotes section
    footnotes = content.find("div", id="footnotes_section")
    if footnotes:
        footnotes.decompose()

    for tag in content.find_all(["script", "style", "aside"]):
        tag.decompose()

    paragraphs = [
        p.get_text(strip=True)
        for p in content.find_all("p")
        if p.get_text(strip=True)
    ]

    text = "\n".join(paragraphs)

    return {
        "url": url,
        "title": title,
        "date": pub_date.strftime("%Y-%m-%d"),
        "text": text,
    }


# ---------------------------------------------------------
# Main scraper (BACKFILL WITH CUTOFF)
# ---------------------------------------------------------
def scrape_fft_datalab():
    all_articles = []
    page = 1

    print("🚀 Starting FFT Education Datalab scrape…")

    while True:
        page_url = BASE_URL if page == 1 else PAGE_URL.format(page)
        print(f"\n📄 Scraping page {page}: {page_url}")

        r = requests.get(page_url, headers=HEADERS)
        links = extract_links(r.text)

        print(f"🔗 Found {len(links)} article links")

        if not links:
            break

        for link in links:
            print(f"   📰 Scraping: {link}")
            result = scrape_article(link)

            if result == "STOP":
                print(f"⛔ Reached pre-{CUTOFF_YEAR} article — stopping scraper.")
                df = pd.DataFrame(all_articles, columns=["url", "title", "date", "text"])
                df.to_csv(OUTPUT, index=False)
                print(f"\n💾 Saved {len(df)} articles to {OUTPUT}")
                return

            if result:
                all_articles.append(result)

            time.sleep(1)

        page += 1
        time.sleep(1)

    df = pd.DataFrame(all_articles, columns=["url", "title", "date", "text"])
    df.to_csv(OUTPUT, index=False)

    print(f"\n💾 Saved {len(df)} articles to {OUTPUT}")


# ---------------------------------------------------------
# Run scraper
# ---------------------------------------------------------
if __name__ == "__main__":
    scrape_fft_datalab()
