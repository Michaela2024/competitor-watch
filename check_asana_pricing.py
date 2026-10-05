import requests
from bs4 import BeautifulSoup
import json

def get_asana_pricing():
    url = "https://asana.com/pricing/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    pricing_data = json.loads(scripts[0].string)

    tiers = []
    for item in pricing_data["@graph"]:
        if item.get("@type") == "Product":
            product_name = item["name"]
            for offer in item["offers"]:
                price = offer.get("price")
                tiers.append({
                    "product": product_name,
                    "tier": offer["name"],
                    "billing": None,
                    "price": price,
                    "currency": offer.get("priceCurrency"),
                    "note": offer.get("description") if price is None else None,
                })

    return tiers


if __name__ == "__main__":
    tiers = get_asana_pricing()
    print(f"Found {len(tiers)} tiers")
    for tier in tiers:
        print(tier)