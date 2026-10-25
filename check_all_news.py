
import feedparser
import re
from urllib.parse import quote_plus

companies = {
    "Asana": "Asana acquisition OR funding OR partnership",
    "Notion": "Notion acquisition OR funding OR partnership",
    "monday.com": "\"monday.com\" acquisition OR funding OR partnership",
}

KEYWORDS = ["acqui", "fund", "raise", "invest", "partner", "deal"]

EXCLUDE_PHRASES = [
    "notion capital",
    "asana partners",
    "asana rebel",
    "lydia asana",
    "great notion",
    "notion consulting",
    "notion systems",
    "notion vtec",
    "the notion of",
    "notion of ",
    "the notion that"
]


def get_news(query):
    encoded_query = quote_plus(query)
    url = (
        f"https://news.google.com/rss/search?q={encoded_query}"
        "&hl=en-US&gl=US&ceid=US:en"
    )
    feed = feedparser.parse(url)
    return [
        entry for entry in feed.entries
        if "2026" in entry.get("published", "")
    ]


def is_relevant(title, company_name):
    headline = title.rsplit(" - ", 1)[0]
    headline_lower = headline.lower()

    if company_name == "Notion" and re.search(
        r"\bthe\s+notion\b", headline_lower
    ):
        return False

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

        relevant = [
            entry for entry in entries
            if is_relevant(entry.title, company)
        ]

        results[company] = [
            {
                "date": entry.published,
                "title": entry.title,
                "link": entry.link
            }
            for entry in relevant
        ]

    return results


if __name__ == "__main__":
    all_news = get_all_news()

    for company, entries in all_news.items():
        print(f"\n=== {company}: {len(entries)} relevant ===")

        for entry in entries[:5]:
            print(entry)
