import os
import argparse
import json
from dotenv import load_dotenv
from anthropic import Anthropic
import sqlite3

load_dotenv()
parser = argparse.ArgumentParser()
parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Show events to be classified without calling Claude"
)
args = parser.parse_args()

prompt += """

HISTORICAL CONTEXT FROM EARLIER ASANA CHANGELOG ENTRIES

September 2025:
- AI Teammate custom MCP integrations: AI Teammates could
  connect to external tools through MCP servers.
- AI Teammates access to work widget: Users could inspect
  which work items an AI Teammate could access.
- Dash/AI Teammates build rules: AI Teammates could help
  create and save automation rules.

Use this historical context when evaluating the March 2026
announcement. Distinguish an existing capability from a
genuinely new development. If the precise change cannot
be established, say so explicitly.
"""
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

connection = sqlite3.connect("competitor_watch.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()


cursor.execute("""
    SELECT *
    FROM events
    WHERE significance_score IS NULL
      AND normalised_date BETWEEN ? AND ?
    ORDER BY normalised_date, id
""", (args.start, args.end))

entries = cursor.fetchall()

if args.dry_run:
    for entry in entries:
        print(f"{entry['normalised_date']} | {entry['company']} | {entry['title']}")

    print(f"\nTotal events to classify: {len(entries)}")
    connection.close()
    raise SystemExit(0)

print(f"Classifying {len(entries)} unclassified events...\n")

CHANGELOG_RUBRIC = """You are rating product changelog entries for how significant they are to a product leader tracking a competitor.
Rate the potential competitive significance of this product
development from 1 to 10.

8-10: Potentially major competitive development.
A substantial new capability, major expansion of an existing
capability, important platform or ecosystem shift, or a
development that could materially change customer value,
competitive differentiation, or market positioning.

6-7: Meaningful product development.
A new workflow, integration, capability expansion, or
significant improvement that strengthens the product's
value proposition, but whose broader competitive impact
is less clear.

4-5: Incremental product improvement.
An enhancement to an existing feature or workflow that
offers useful additional functionality or improved usability,
without evidence of a substantial competitive shift.

1-3: Minor development.
Cosmetic changes, routine maintenance, small usability
improvements, or minor fixes.

SCORING PRINCIPLES
- Score the significance of the announced development,
  not merely its technical novelty.
- Do not assume that technical novelty implies commercial
  significance.
- Do not automatically downgrade a development because
  it builds on an existing capability.
- Distinguish demonstrated impact from potential impact.
- Do not invent adoption, revenue, customer outcomes,
  or historical context.
- When evidence is limited, explain the uncertainty rather
  than inventing facts to justify a score.

Respond with ONLY a JSON object in this exact format, no other text:
{{"score": <number>, "reasoning": "<one sentence explaining the score>"}}

Entry title: {title}
Entry description: {description}
"""

NEWS_RUBRIC = """You are rating a news event for how strategically significant it is to a product leader tracking a competitor.

Rate the event from 0 to 10, using this guide:
- 0: Irrelevant or not actually about the competitor being tracked
- 1-3: Minor company news with little strategic significance
- 4-5: A modest partnership, commercial development, funding event, or other development with limited competitive impact
- 6-7: An important partnership, investment, acquisition, or strategic development that could materially strengthen the company
- 8-10: A major acquisition, strategic repositioning, capability-changing deal, or development that could materially change the competitive landscape

Consider whether the event changes the company's capabilities, market position, strategy, distribution, technology, or competitive strength.

Respond with ONLY a JSON object in this exact format, no other text:
{{"score": <number>, "reasoning": "<one sentence explaining the score>"}}

Company being tracked: {company}
Event title: {title}
"""
results = []

for entry in entries:
    if entry["source_type"] == "changelog":
        prompt = CHANGELOG_RUBRIC.format(
            title=entry["title"],
            description=entry["description"]
        )
    else:
        prompt = NEWS_RUBRIC.format(
            company=entry["company"],
            title=entry["title"]
        )
        if entry["title"] == "AI Teammates" and entry["company"] == "Asana":
            print("\nREVISED ASSESSMENT TEST")
            print("Prompt:\n", prompt)

        test_response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        print("\nClaude's response:\n", test_response.content[0].text)
        break

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text
    cleaned = result_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        cleaned = cleaned.rsplit("```", 1)[0]

    result = json.loads(cleaned)

    cursor.execute("""
        UPDATE events
        SET significance_score = ?, significance_reason = ?
        WHERE id = ?
    """, (
        result["score"],
        result["reasoning"],
        entry["id"]
    ))

    connection.commit()

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

    