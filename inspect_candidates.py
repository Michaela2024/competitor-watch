import sqlite3

connection = sqlite3.connect("competitor_watch.db")
cursor = connection.cursor()

cursor.execute("""
    SELECT
        company,
        COUNT(*) AS article_count,
        MIN(normalised_date),
        MAX(normalised_date)
    FROM events
    WHERE source_type = 'news'
      AND normalised_date BETWEEN '2026-05-01' AND '2026-05-31'
    GROUP BY company
    ORDER BY company
""")

for company, count, first_date, last_date in cursor.fetchall():
    print(
        f"{company}: {count} articles "
        f"({first_date} to {last_date})"
    )

connection.close()