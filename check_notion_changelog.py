import feedparser

def get_notion_changelog():
    url = "https://www.notion.com/releases/rss.xml"
    feed = feedparser.parse(url)

    entries = []
    for entry in feed.entries:
        entries.append({
            "date": entry.published,
            "title": entry.title,
            "link": entry.link,
        })

    return entries


if __name__ == "__main__":
    entries = get_notion_changelog()
    print(f"Found {len(entries)} entries")
    for entry in entries[:5]:
        print(entry)