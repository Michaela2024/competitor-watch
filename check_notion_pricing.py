import re
from playwright.sync_api import sync_playwright

def get_notion_pricing():
    url = "https://www.notion.com/pricing"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)
        text = page.inner_text("body")
        browser.close()

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    plan_names = ["Free", "Plus", "Business", "Enterprise"]
    tiers = []

    for i, line in enumerate(lines):
        if line in plan_names:
            for lookahead in lines[i+1:i+4]:
                price_match = re.match(r"^([£$])(\d+(?:\.\d{2})?)$", lookahead)
                if price_match:
                    symbol, amount = price_match.groups()
                    tiers.append({
                        "product": "Notion",
                        "tier": line,
                        "billing": None,
                        "price": float(amount),
                        "currency": symbol,
                        "note": None,
                    })
                    break
                elif "Custom pricing" in lookahead:
                    tiers.append({
                        "product": "Notion",
                        "tier": line,
                        "billing": None,
                        "price": None,
                        "currency": None,
                        "note": "contact sales / no fixed price",
                    })
                    break

    return tiers


if __name__ == "__main__":
    tiers = get_notion_pricing()
    print(f"Found {len(tiers)} tiers")
    for tier in tiers:
        print(tier)