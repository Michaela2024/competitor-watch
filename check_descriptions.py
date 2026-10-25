import sqlite3

connection = sqlite3.connect("competitor_watch.db")

rows = connection.execute("""
    SELECT
        company,
        COUNT(*) AS total,
        COUNT(NULLIF(TRIM(description), '')) AS described
    FROM events
    WHERE normalised_date BETWEEN '2026-03-01' AND '2026-05-31'
    GROUP BY company
""").fetchall()

for company, total, described in rows:
    print(f"{company}: {described} of {total} events have descriptions")

connection.close()