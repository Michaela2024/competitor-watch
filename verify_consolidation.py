import sqlite3

connection = sqlite3.connect("competitor_watch.db")
cursor = connection.cursor()

cursor.execute("""
    SELECT
        se.title,
        se.significance_score,
        e.title,
        e.source_url
    FROM strategic_events se
    JOIN strategic_event_sources ses
        ON se.id = ses.strategic_event_id
    JOIN events e
        ON ses.source_event_id = e.id
    WHERE se.id = ?
""", (1,))

for event_title, score, source_title, url in cursor.fetchall():
    print(f"Strategic event: {event_title} [{score}]")
    print(f"Source: {source_title}")
    print(f"URL: {url}\n")

connection.close()