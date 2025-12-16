import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from dateutil import parser
import time

# ----------------------------------------------------------
# Config
# ----------------------------------------------------------
BASE = "https://www.nuffieldfoundation.org"
START_URL = "https://www.nuffieldfoundation.org/news-and-events"
OUTPUT = "/workspaces/ERP_Newsletter/data/data05_full_articles_selected/nuffield_articles_2023_2025.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

START_YEAR = 2023
REQUEST_DELAY = 0.4
PAGE_DELAY = 1.0


# ----------------------------------------------------------
# Extract listing cards (Latest feed only)
# ----------------------------------------------------------
def extract_latest_cards(html):
    soup = BeautifulSoup(html, "html.parser")

    results = soup.select_one("div#article-results")
    if not results:
        return []

    cards = results.select("a.card-item__container")
    print(f"🧪 Found {len(cards)} cards")

    items = []

    for card in cards:
        href = card.get("href")
        if not href:
            continue

        url = href if href.startswith("http") else BASE + href

        title = ""
        title_tag = card.select_one("h3.card-item__heading")
        if title_tag:
            title = title_tag.get_text(strip=True)

        items.append({
            "url": url,
            "title": title,
            "date_obj": None
        })

    return items


# ----------------------------------------------------------
# Scrape full article page
# ----------------------------------------------------------
def scrape_article(item):
    try:
        r = requests.get(item["url"], headers=HEADERS, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"⚠️ Request failed: {item['url']} ({e})")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # --------------------------------------------------
    # DATE extraction (article + event pages)
    # --------------------------------------------------
    if not item["date_obj"]:
        meta = soup.select_one("p.article-meta")
        if meta:
            try:
                item["date_obj"] = parser.parse(
                    meta.get_text(strip=True), fuzzy=True
                )
            except Exception:
                pass

    if not item["date_obj"]:
        li = soup.select_one("ul.list-items li")
        if li:
            try:
                item["date_obj"] = parser.parse(
                    li.get_text(strip=True), fuzzy=True
                )
            except Exception:
                pass

    if not item["date_obj"]:
        print(f"⚠️ Missing date: {item['url']}")
        return None

    if item["date_obj"].year < START_YEAR:
        return None

    # --------------------------------------------------
    # TITLE fallback (article page)
    # --------------------------------------------------
    if not item["title"]:
        h1 = soup.select_one("h1.medium-heading")
        if h1:
            item["title"] = h1.get_text(strip=True)

    # --------------------------------------------------
    # MAIN CONTENT (include subheadings)
    # --------------------------------------------------
    content_div = soup.select_one("div.article-area")
    if not content_div:
        return None

    for tag in content_div.find_all(["script", "style", "figure", "aside"]):
        tag.decompose()

    chunks = []
    for el in content_div.find_all(["h2", "h3", "p"]):
        txt = el.get_text(" ", strip=True)
        if txt:
            chunks.append(txt)

    text = "\n\n".join(chunks)

    return {
        "url": item["url"],
        "title": item["title"],
        "date": item["date_obj"].strftime("%Y-%m-%d"),
        "text": text
    }


# ----------------------------------------------------------
# Main scraper
# ----------------------------------------------------------
def scrape_nuffield():
    all_articles = []
    seen = set()
    page = 1

    print("🚀 Starting Nuffield Foundation scrape…")

    while True:
        url = START_URL if page == 1 else f"{START_URL}/page/{page}"
        print(f"\n📄 Scraping page {page}: {url}")

        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
        except Exception as e:
            print(f"⛔ Page request failed ({e})")
            break

        items = extract_latest_cards(r.text)
        if not items:
            print("⛔ No cards found — stopping.")
            break

        new_items = 0

        for item in items:
            if item["url"] in seen:
                continue

            seen.add(item["url"])
            new_items += 1

            result = scrape_article(item)
            if result:
                print(f"   📰 {result['date']} | {result['title']}")
                all_articles.append(result)

            time.sleep(REQUEST_DELAY)

        if new_items == 0:
            print("⛔ No new articles — reached end.")
            break

        page += 1
        time.sleep(PAGE_DELAY)

    df = pd.DataFrame(all_articles)
    df.to_csv(OUTPUT, index=False)
    print(f"\n💾 Saved {len(df)} articles → {OUTPUT}")


# ----------------------------------------------------------
# Run
# ----------------------------------------------------------
if __name__ == "__main__":
    scrape_nuffield()
