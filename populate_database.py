from check_monday_changelog import get_monday_changelog
from check_asana_changelog import get_asana_changelog
from check_notion_changelog import get_notion_changelog
from check_all_news import get_all_news
from database import save_event

monday_entries = get_monday_changelog()

for entry in monday_entries:
    save_event(
        "monday.com",
        entry["date"],
        entry["title"],
        entry["description"],
        "changelog"
    )

asana_entries=get_asana_changelog()

for entry in asana_entries:
    save_event(
        "Asana",
        entry["date"],
        entry["title"],
        entry["description"],
        "changelog",
        entry["link"]
    )

notion_entries = get_notion_changelog()

for entry in notion_entries:
    save_event(
        "Notion",
        entry["date"],
        entry["title"],
        None,
        "changelog",
        entry["link"]
    )

news = get_all_news()
for company, entries in news.items():
    for entry in entries:
        save_event(
            company,
            entry["date"],
            entry["title"],
            None,
            "news",
            entry["link"]
        )
                