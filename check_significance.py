import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
from check_monday_changelog import get_monday_changelog

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

entries=get_monday_changelog()
print(f"Classifying {len(entries)} entries...\n")


RUBRIC = """You are rating product changelog entries for how significant they are to a product leader tracking a competitor.

Rate each entry's significance from 1 to 10, using this guide:
- 8-10: A genuinely new capability, or an open/standardised protocol-level shift — specifically: adopting a published external standard (e.g. MCP) so other systems can integrate without custom code, or a capability the product categorically could not do before
- 6-7: A new way of accomplishing something that already existed, using the product's OWN existing mechanisms (e.g. a proprietary new UI flow, natural language instead of manual setup within the product itself)
- 4-5: A direct enhancement to an existing feature's existing workflow (more options, better performance, wider limits)
- 1-3: Cosmetic, housekeeping, or a minor fix

Respond with ONLY a JSON object in this exact format, no other text:
{{"score": <number>, "reasoning": "<one sentence explaining the score>"}}

Entry title: {title}
Entry description: {description}
"""

results=[]

for entry in entries:
    prompt = RUBRIC.format(title=entry["title"], description=entry["description"])

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text
    cleaned = result_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]        # drop the ```json line
        cleaned = cleaned.rsplit("```", 1)[0]       # drop the trailing ```

    result = json.loads(cleaned)

    results.append({
        "title": entry["title"],
        "score": result["score"],
        "reasoning": result["reasoning"],
    })

# Sort highest-scoring first, so the most significant entries are easiest to see
results.sort(key=lambda r: r["score"], reverse=True)

print("=== All entries, highest significance first ===\n")
for r in results:
    print(f"[{r['score']}] {r['title']}")
    print(f"    {r['reasoning']}\n")

    