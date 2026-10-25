import sqlite3

connection = sqlite3.connect("competitor_watch.db")
cursor = connection.cursor()

cursor.execute("""
    SELECT company, source_type, COUNT(*)
    FROM events
    WHERE normalised_date BETWEEN ? AND ?
    AND significance_score IS NULL
    GROUP BY company, source_type
""", ("2026-05-01", "2026-05-31"))

for company, source_type, count in cursor.fetchall():
    print(f"{company}: {count} {source_type} events")

connection.close()