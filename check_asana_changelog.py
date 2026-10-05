import re
from playwright.sync_api import sync_playwright

def get_asana_changelog():
    url = "https://help.asana.com/s/article/release-notes"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)
        text = page.inner_text("body")
        browser.close()

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    month_headings = [
        "August 2026", "July 2026", "June 2026", "May 2026", "April 2026",
        "March 2026", "February 2026", "January 2026", "December 2025",
        "November 2025", "October 2025", "September 2025", "August 2025"
    ]
    entry_pattern = re.compile(r"^\(([^)]+)\)\s*([^:]+):\s*(.*)$")

    current_month = None
    entries = []

    for line in lines:
        if line in month_headings:
            current_month = line
            continue

        match = entry_pattern.match(line)
        if match and current_month:
            tier, feature, description = match.groups()
            entries.append({
                "date": current_month,
                "tier": tier.strip(),
                "title": feature.strip(),
                "description": description.strip()
            })

    return entries


if __name__ == "__main__":
    entries = get_asana_changelog()
    print(f"Extracted {len(entries)} entries")
    for entry in entries[:5]:
        print(entry)
