import feedparser

def get_notion_changelog():
    url = "https://www.notion.com/releases/rss.xml"
    feed = feedparser.parse(url)
    print("Available RSS fields:", list(feed.entries[0].keys()))

    entries = []
    for entry in feed.entries:
        entries.append({
            "date": entry.published,
            "title": entry.title,
            "description": entry.get("summary", ""),
            "link": entry.link,
        })

    return entries

import requests

url = "https://www.notion.so/releases/2026-05-13"
response = requests.get(url, timeout=15)

print("HTTP status:", response.status_code)
print("Page size:", len(response.text))
print("Contains Developer Platform:", "Developer Platform" in response.text)

from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")

main = soup.find("main")

if main:
    text = main.get_text(" ", strip=True)
    print("Main content preview:", text[:1000])
else:
    print("No main element found")

if __name__ == "__main__":
    entries = get_notion_changelog()
    print(f"Found {len(entries)} entries")
    for entry in entries[:5]:
        print("Title:", entry["title"])
        print("URL:", entry["link"])
        print("Description:", entry.get("description", "Not available"))