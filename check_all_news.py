import feedparser
from urllib.parse import quote_plus

companies = {
    "Asana": "Asana acquisition OR funding OR partnership",
    "Notion": "Notion acquisition OR funding OR partnership",
    "monday.com": "\"monday.com\" acquisition OR funding OR partnership",
}

KEYWORDS = ["acqui", "fund", "raise", "invest", "partner", "deal"]
EXCLUDE_PHRASES = ["notion capital"]

def get_news(query):
    encoded_query = quote_plus(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    return feed.entries

def is_relevant(title, company_name):
    headline = title.rsplit(" - ", 1)[0]
    headline_lower = headline.lower()

    if any(phrase in headline_lower for phrase in EXCLUDE_PHRASES):
        return False
    if company_name.lower() not in headline_lower:
        return False
    if not any(keyword in headline_lower for keyword in KEYWORDS):
        return False
    return True

def get_all_news():
    results = {}
    for company, query in companies.items():
        entries = get_news(query)
        relevant = [e for e in entries if is_relevant(e.title, company)]
        results[company] = [
            {"date": e.published, "title": e.title, "link": e.link}
            for e in relevant
        ]
    return results


if __name__ == "__main__":
    all_news = get_all_news()
    for company, entries in all_news.items():
        print(f"\n=== {company}: {len(entries)} relevant ===")
        for entry in entries[:5]:
            print(entry)

