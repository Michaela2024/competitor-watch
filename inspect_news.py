import sqlite3

connection = sqlite3.connect("competitor_watch.db")
cursor = connection.cursor()

cursor.execute("""
    SELECT id, company, normalised_date, title, significance_score
    FROM events
    WHERE source_type = 'news'
      AND normalised_date BETWEEN '2026-05-01' AND '2026-05-31'
    ORDER BY company, normalised_date
""")

for event in cursor.fetchall():
    print(event)

connection.close()