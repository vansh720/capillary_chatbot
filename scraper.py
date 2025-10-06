# scraper.py
import requests, time, json, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

base_url = "https://docs.capillarytech.com/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def collect_links(start_url, domain_only=True, max_links=200):
    res = requests.get(start_url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full = urljoin(start_url, href)
        parsed = urlparse(full)
        if domain_only:
            if parsed.netloc.endswith("capillarytech.com"):
                links.add(full.split("#")[0])  # remove fragment
        else:
            links.add(full.split("#")[0])
        if len(links) >= max_links:
            break
    return links

def extract_text_from(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        page = BeautifulSoup(r.text, "html.parser")
        # collect headings and paragraphs and list items
        parts = []
        for tag in page.find_all(["h1","h2","h3","h4","p","li"]):
            txt = tag.get_text(separator=" ", strip=True)
            if txt:
                parts.append(txt)
        text = "\n".join(parts)
        return text
    except Exception as e:
        print("Error fetching", url, e)
        return ""

if __name__ == "__main__":
    print("Collecting links from homepage...")
    links = collect_links(base_url, domain_only=True, max_links=80)
    # ensure homepage is included
    links.add(base_url)

    pages = []
    for i, link in enumerate(sorted(links)):
        print(f"[{i+1}/{len(links)}] Scraping:", link)
        txt = extract_text_from(link)
        if txt.strip():
            pages.append({"url": link, "text": txt})
        time.sleep(0.6)  # be polite

    with open("capillary_docs.json", "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    print("✅ Saved capillary_docs.json with", len(pages), "pages")
