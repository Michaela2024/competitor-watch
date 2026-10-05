import requests
from bs4 import BeautifulSoup
import json

def get_monday_pricing():
    url = "https://monday.com/pricing/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    pricing_data = json.loads(scripts[1].string)

    tiers = []
    for item in pricing_data["@graph"]:
        if item.get("@type") == "Product":
            product_name = item["name"]
            for offer in item["offers"]:
                if offer.get("price") is not None:
                    tiers.append({
                        "product": product_name,
                        "tier": offer["name"],
                        "billing": None,
                        "price": offer["price"],
                        "currency": offer["priceCurrency"],
                        "note": None,
                    })

                elif "priceSpecification" in offer:
                    for spec in offer["priceSpecification"]:
                        billing = "monthly" if spec["unitCode"] == "MON" else "annual"
                        tiers.append({
                            "product": product_name,
                            "tier": offer["name"],
                            "billing": billing,
                            "price": spec["price"],
                            "currency": spec["priceCurrency"],
                            "note": None,
                        })

                else:
                    tiers.append({
                        "product": product_name,
                        "tier": offer["name"],
                        "billing": None,
                        "price": None,
                        "currency": None,
                        "note": "contact sales / no fixed price",
                    })

    return tiers


if __name__ == "__main__":
    tiers = get_monday_pricing()
    print(f"Found {len(tiers)} tiers")
    for tier in tiers[:10]:
        print(tier)