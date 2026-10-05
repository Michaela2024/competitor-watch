import re
from playwright.sync_api import sync_playwright

def get_monday_changelog():
    url = "https://monday.com/whats-new"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)
        text = page.inner_text("body")
        browser.close()

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    MONTHS = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    month_number = {name: i + 1 for i, name in enumerate(MONTHS)}

    date_pattern = re.compile(r"^(" + "|".join(MONTHS) + r") (\d{1,2})$")

    KNOWN_TAGS = {
        "monday platform", "monday work management", "monday CRM", "monday dev",
        "monday service", "WorkCanvas", "WorkForms",
        "Company wide", "Admin only", "Enterprise", "Pro", "Free", "SMB",
    }

    date_positions = [i for i, line in enumerate(lines) if date_pattern.match(line)]

    entries = []
    year = 2026
    previous_month = None

    for n, start in enumerate(date_positions):
        if n + 1 < len(date_positions):
            end = date_positions[n + 1]
        else:
            end = len(lines)
        end = min(end, start + 10)

        month_name, day = date_pattern.match(lines[start]).groups()

        if previous_month is not None and month_number[month_name] > previous_month:
            year -= 1
        previous_month = month_number[month_name]

        block = [line for line in lines[start + 1:end] if line != "Read more"]
        if len(block) < 2:
            continue

        title, description = block[0], block[1]
        tags = [line for line in block[2:] if line in KNOWN_TAGS]

        entries.append({
            "date": f"{month_name} {day}, {year}",
            "title": title,
            "description": description,
            "tags": tags,
        })

    return entries


if __name__ == "__main__":
    entries = get_monday_changelog()
    print(f"Extracted {len(entries)} entries")
    for entry in entries[:3]:
        print(entry)