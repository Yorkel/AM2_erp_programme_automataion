import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
BASE_URL = "https://ifs.org.uk/topics/education-and-skills"
PAGE_URL = "https://ifs.org.uk/topics/education-and-skills?page={}"

OUTPUT = "/workspaces/ERP_Newsletter/data/data05_full_articles_selected/ifs_education_skills_2023_2025.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; IFSScraper/1.0)"
}

# ---------------------------------------------------------
# Extract article links from listing page
# ---------------------------------------------------------
def extract_links(html):
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]

        # Only IFS publications
        if href.startswith("/publications/"):
            links.append("https://ifs.org.uk" + href)

    return list(set(links))


# ---------------------------------------------------------
# Extract full article
# ---------------------------------------------------------
def scrape_article(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    # ---------------------------
    # TITLE
    # ---------------------------
    title_tag = soup.select_one("h1.c-single-header__heading")
    title = title_tag.get_text(strip=True) if title_tag else ""

    if not title:
        print(f"⚠️ Missing title: {url}")

    # ---------------------------
    # DATE
    # ---------------------------
    date_tag = soup.select_one("p.c-single-header__date")
    if not date_tag:
        print(f"⚠️ Missing date: {url}")
        return None

    raw_date = (
        date_tag.get_text(strip=True)
        .replace("Published on", "")
        .strip()
    )

    try:
        pub_date = datetime.strptime(raw_date, "%d %B %Y")
    except ValueError:
        print(f"⚠️ Failed to parse date: '{raw_date}' ({url})")
        return None

    # Stop when older than 2023
    if pub_date.year < 2023:
        return "STOP"

    # ---------------------------
    # ARTICLE CONTENT
    # ---------------------------
    content = soup.select_one("section.c-text-block")
    if not content:
        print(f"⚠️ Missing content: {url}")
        return None

    for tag in content.find_all(["script", "style", "aside", "footer"]):
        tag.decompose()

    text = "\n".join(
        p.get_text(strip=True)
        for p in content.find_all("p")
        if p.get_text(strip=True)
    )

    return {
        "url": url,
        "title": title,
        "date": pub_date.strftime("%Y-%m-%d"),
        "text": text,
    }


# ---------------------------------------------------------
# Main scraper
# ---------------------------------------------------------
def scrape_ifs():
    all_articles = []
    seen = set()
    page = 0

    print("🚀 Starting IFS Education & Skills scrape…")

    while True:
        page_url = BASE_URL if page == 0 else PAGE_URL.format(page)
        print(f"\n📄 Scraping page {page}: {page_url}")

        r = requests.get(page_url, headers=HEADERS)
        links = extract_links(r.text)

        print(f"🔗 Found {len(links)} article links")

        if not links:
            print("❌ No links found — stopping.")
            break

        for link in links:
            if link in seen:
                continue

            seen.add(link)
            print(f"   📰 Scraping: {link}")

            result = scrape_article(link)

            if result == "STOP":
                print("⛔ Reached pre-2023 article — stopping scraper.")
                pd.DataFrame(all_articles).to_csv(OUTPUT, index=False)
                print(f"💾 Saved {len(all_articles)} articles.")
                return

            if result:
                all_articles.append(result)

            time.sleep(1)

        page += 1
        time.sleep(1)

    pd.DataFrame(all_articles).to_csv(OUTPUT, index=False)
    print(f"\n💾 Saved {len(all_articles)} articles to: {OUTPUT}")


# ---------------------------------------------------------
# Run scraper
# ---------------------------------------------------------
if __name__ == "__main__":
    scrape_ifs()
