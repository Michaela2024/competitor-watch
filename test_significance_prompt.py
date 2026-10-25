import ast
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

source = Path("check_significance.py").read_text(encoding="utf-8")
tree = ast.parse(source)

rubric = next(
    node.value.value
    for node in tree.body
    if isinstance(node, ast.Assign)
    and any(
        isinstance(target, ast.Name) and target.id == "CHANGELOG_RUBRIC"
        for target in node.targets
    )
    and isinstance(node.value, ast.Constant)
    and isinstance(node.value.value, str)
)

import sqlite3
import anthropic

connection = sqlite3.connect("competitor_watch.db")

event = connection.execute("""
    SELECT title, description
    FROM events
    WHERE id = 204
""").fetchone()

connection.close()

prompt = rubric.format(
    title=event[0],
    description=event[1]
)

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=300,
    messages=[{"role": "user", "content": prompt}]
)

print("\nREVISED ASSESSMENT — ASANA AI TEAMMATES\n")
print(response.content[0].text)