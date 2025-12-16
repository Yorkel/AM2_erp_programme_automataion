import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

BASE_URL = "https://fed.education/news-resources/"
PAGE_URL = "https://fed.education/news-resources/page/{}/"

OUTPUT = "/workspaces/ERP_Newsletter/data/data05_full_articles_selected/fed_news_resources.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FEDScraper/1.0)"
}

STOP_YEAR = 2023  # ⬅️ HARD STOP


# ---------------------------------------------------------
# Extract article links from listing page
# ---------------------------------------------------------
def extract_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.select("a.elementor-post__thumbnail__link[href]"):
        links.append(a["href"])

    for a in soup.select("h3.elementor-post__title a[href]"):
        links.append(a["href"])

    return list(dict.fromkeys(links))


# ---------------------------------------------------------
# Extract full article
# ---------------------------------------------------------
def scrape_article(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    # TITLE
    title_tag = soup.select_one("h1.elementor-heading-title")
    if not title_tag:
        return None
    title = title_tag.get_text(strip=True)

    # DATE
    date_tag = soup.select_one("time")
    if not date_tag:
        return None

    try:
        pub_date = datetime.strptime(date_tag.get_text(strip=True), "%B %d, %Y")
    except ValueError:
        return None

    # ⛔ STOP CONDITION
    if pub_date.year < STOP_YEAR:
        return "STOP"

    # CONTENT
    content = soup.select_one("div.elementor-widget-theme-post-content")
    if not content:
        return None

    paragraphs = []
    for p in content.find_all("p"):
        text = p.get_text(strip=True)

        if "The FED are happy to share blogs" in text:
            break

        if text:
            paragraphs.append(text)

    return {
        "url": url,
        "title": title,
        "date": pub_date.strftime("%Y-%m-%d"),
        "text": "\n".join(paragraphs),
    }


# ---------------------------------------------------------
# Main scraper
# ---------------------------------------------------------
def scrape_fed():
    all_articles = []
    page = 1

    print("🚀 Starting FED News & Resources scrape…")

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
                print("⛔ Reached 2022 — stopping scrape.")
                df = pd.DataFrame(all_articles)
                df.to_csv(OUTPUT, index=False)
                print(f"\n💾 Saved {len(df)} articles to {OUTPUT}")
                return

            if article:
                all_articles.append(article)

            time.sleep(1)

        page += 1
        time.sleep(1)

    df = pd.DataFrame(all_articles)
    df.to_csv(OUTPUT, index=False)
    print(f"\n💾 Saved {len(df)} articles to {OUTPUT}")


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------
if __name__ == "__main__":
    scrape_fed()
