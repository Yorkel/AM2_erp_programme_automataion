import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

BASE_URL = "https://chartered.college/news-blogs/"
PAGE_URL = "https://chartered.college/news-blogs/page/{}/"

OUTPUT = "/workspaces/ERP_Newsletter/data/data05_full_articles_selected/cct_news_blogs.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CCTScraper/1.0)"
}

STOP_YEAR = 2023

# ---------------------------------------------------------
# Extract article links from listing page
# ---------------------------------------------------------
def extract_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    # Extracting all links within the h4 tags, specifically
    for a in soup.select("h4.elementor-heading-title a[href]"):
        href = a["href"]
        
        # Only add articles, not pagination or irrelevant links
        if href.startswith("https://chartered.college/news-blogs/") and "/page/" not in href:
            links.append(href)

    return list(dict.fromkeys(links))

# ---------------------------------------------------------
# Extract full article content
# ---------------------------------------------------------
def scrape_article(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    # TITLE
    title_tag = soup.select_one("h2.elementor-heading-title")
    if not title_tag:
        print(f"⚠️ Missing title: {url}")
        return None

    title = title_tag.get_text(strip=True)

    # DATE
    date_tag = soup.select_one("time")
    if not date_tag:
        print(f"⚠️ Missing date: {url}")
        return None

    try:
        pub_date = datetime.strptime(date_tag.get_text(strip=True), "%B %d, %Y")
    except ValueError:
        print(f"⚠️ Date parse failed: {url}")
        return None

    # STOP when older than target year
    if pub_date.year < STOP_YEAR:
        return "STOP"

    # CONTENT
    content = soup.select_one("div.elementor-widget-theme-post-content")
    if not content:
        print(f"⚠️ Missing content: {url}")
        return None

    paragraphs = [
        p.get_text(strip=True)
        for p in content.find_all("p")
        if p.get_text(strip=True)
    ]

    return {
        "url": url,
        "title": title,
        "date": pub_date.strftime("%Y-%m-%d"),
        "text": "\n".join(paragraphs),
    }

# ---------------------------------------------------------
# Main scraper function
# ---------------------------------------------------------
def scrape_cct():
    all_articles = []
    page = 1

    print("🚀 Starting Chartered College of Teaching scrape…")

    while True:
        page_url = BASE_URL if page == 1 else PAGE_URL.format(page)
        print(f"\n📄 Scraping page {page}: {page_url}")

        r = requests.get(page_url, headers=HEADERS)
        links = extract_links(r.text)

        print(f"🔗 Found {len(links)} article links")

        if not links:
            print("⛔ No more pages — stopping.")
            break

        for link in links:
            print(f"   📰 Scraping: {link}")
            article = scrape_article(link)

            if article == "STOP":
                print(f"⛔ Reached articles before {STOP_YEAR} — stopping.")
                pd.DataFrame(all_articles).to_csv(OUTPUT, index=False)
                print(f"💾 Saved {len(all_articles)} articles.")
                return

            if article:
                all_articles.append(article)

            time.sleep(1)

        page += 1
        time.sleep(1)

    pd.DataFrame(all_articles).to_csv(OUTPUT, index=False)
    print(f"\n💾 Saved {len(all_articles)} articles to {OUTPUT}")

# ---------------------------------------------------------
# Run scraper
# ---------------------------------------------------------
if __name__ == "__main__":
    scrape_cct()
