import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import re

# ----------------------------------------------------------
# Config
# ----------------------------------------------------------
BASE = "https://epi.org.uk"
START_URL = "https://epi.org.uk/publications-and-research/"
OUTPUT = "/workspaces/ERP_Newsletter/data/data05_full_articles_selected/epi_articles_2023_2025.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ----------------------------------------------------------
# Utilities
# ----------------------------------------------------------
def clean_ordinal_dates(date_str):
    return re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)


# ----------------------------------------------------------
# Extract article links from listing page
# ----------------------------------------------------------
def extract_links(html):
    soup = BeautifulSoup(html, "html.parser")

    articles = soup.find_all("article")
    print(f"🧪 DEBUG: found {len(articles)} <article> tags")

    links = []
    for art in articles:
        a = art.select_one("div.box-typ1-title a")
        if a and a.get("href"):
            href = a["href"].strip()
            links.append(href if href.startswith("http") else BASE + href)

    return links


# ----------------------------------------------------------
# Extract next page URL (CORRECT for EPI)
# ----------------------------------------------------------
def extract_next_page(html):
    soup = BeautifulSoup(html, "html.parser")

    next_a = soup.select_one("li.next-page a")
    if next_a and next_a.get("href"):
        href = next_a["href"].strip()
        return href if href.startswith("http") else BASE + href

    return None


# ----------------------------------------------------------
# Scrape a single article
# ----------------------------------------------------------
def scrape_article(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    # Title
    title_tag = soup.find("h1", class_="single-title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Date
    date_tag = soup.find("div", class_="single-title-date")
    if not date_tag:
        print(f"⚠️ Missing date: {url}")
        return None

    raw_date = clean_ordinal_dates(date_tag.get_text(strip=True))

    try:
        pub_date = datetime.strptime(raw_date, "%d %B %Y")
    except Exception:
        print(f"⚠️ Could not parse date '{raw_date}' for {url}")
        return None

    if pub_date.year < 2023:
        return "STOP"

    # Main content
    content_div = soup.find("div", class_="detail-page-content")
    if not content_div:
        text = ""
    else:
        for t in content_div.find_all(["script", "style", "figure", "aside"]):
            t.decompose()

        text = "\n".join(
            p.get_text(" ", strip=True)
            for p in content_div.find_all("p")
            if p.get_text(strip=True)
        )

    return {
        "url": url,
        "title": title,
        "date": pub_date.strftime("%Y-%m-%d"),
        "text": text,
    }


# ----------------------------------------------------------
# Main scraper
# ----------------------------------------------------------
def scrape_epi():
    all_articles = []
    seen = set()

    url = START_URL
    page = 1

    print("🚀 Starting EPI scrape…")

    while url:
        print(f"\n📄 Scraping page {page}: {url}")
        r = requests.get(url, headers=HEADERS, timeout=30)

        links = extract_links(r.text)
        print(f"🔗 Extracted {len(links)} article links")

        if not links:
            print("⛔ No links found — stopping.")
            break

        for link in links:
            if link in seen:
                continue

            seen.add(link)
            print(f"   📰 Scraping: {link}")

            result = scrape_article(link)

            if result == "STOP":
                print("⛔ Found pre-2023 article — stopping scrape.")
                pd.DataFrame(all_articles).to_csv(OUTPUT, index=False)
                print(f"💾 Saved {len(all_articles)} articles.")
                return

            if result:
                all_articles.append(result)

            time.sleep(1)

        url = extract_next_page(r.text)
        page += 1
        time.sleep(1)

    pd.DataFrame(all_articles).to_csv(OUTPUT, index=False)
    print(f"\n💾 Completed! Saved {len(all_articles)} articles → {OUTPUT}")


# ----------------------------------------------------------
# Run
# ----------------------------------------------------------
if __name__ == "__main__":
    scrape_epi()
