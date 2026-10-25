import sqlite3

# Connect to the database
connection = sqlite3.connect("competitor_watch.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

# 1. Find all articles about Asana's StackAI acquisition
cursor.execute("""
    SELECT id, title
    FROM events
    WHERE company = 'Asana'
      AND source_type = 'news'
      AND (
          title LIKE '%StackAI%'
          OR title LIKE '%Stack AI%'
      )
      AND normalised_date BETWEEN '2026-05-01' AND '2026-05-31'
""")

sources = cursor.fetchall()

print(f"Found {len(sources)} supporting articles:")

for source_id, title in sources:
    print(f"{source_id}: {title}")

# 2. Check whether the strategic event already exists
cursor.execute("""
    SELECT id
    FROM strategic_events
    WHERE company = ?
      AND title = ?
      AND event_date = ?
""", (
    "Asana",
    "Asana acquires StackAI",
    "2026-05-28"
))

existing_event = cursor.fetchone()

if existing_event:
    strategic_event_id = existing_event[0]
    print(f"\nUsing existing strategic event {strategic_event_id}")

else:
    # 3. Create the strategic event if it doesn't exist
    cursor.execute("""
        INSERT INTO strategic_events (
            company,
            title,
            event_date,
            significance_score,
            summary
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        "Asana",
        "Asana acquires StackAI",
        "2026-05-28",
        7,
        "Asana acquires StackAI to expand its AI agent capabilities and cross-system workflow automation."
    ))

    strategic_event_id = cursor.lastrowid
    print(f"\nCreated strategic event {strategic_event_id}")

# 4. Link all supporting articles to the strategic event
for source_id, title in sources:
    cursor.execute("""
        INSERT OR IGNORE INTO strategic_event_sources (
            strategic_event_id,
            source_event_id
        )
        VALUES (?, ?)
    """, (
        strategic_event_id,
        source_id
    ))

# 5. Save changes
connection.commit()

# 6. Verify the number of linked sources
cursor.execute("""
    SELECT COUNT(*)
    FROM strategic_event_sources
    WHERE strategic_event_id = ?
""", (strategic_event_id,))

source_count = cursor.fetchone()[0]

print(
    f"Strategic event {strategic_event_id} "
    f"has {source_count} supporting sources."
)

connection.close()