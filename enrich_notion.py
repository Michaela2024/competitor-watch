import sqlite3
import time
import requests
from bs4 import BeautifulSoup

DATABASE = "competitor_watch.db"

connection = sqlite3.connect(DATABASE)

try:
    rows = connection.execute("""
        SELECT id, title, source_url
        FROM events
        WHERE company = 'Notion'
          AND normalised_date BETWEEN '2026-03-01' AND '2026-05-31'
          AND (description IS NULL OR TRIM(description) = '')
          AND source_url IS NOT NULL
        ORDER BY normalised_date
    """).fetchall()

    print(f"Found {len(rows)} Notion events to enrich")

    updated = 0
    failed = 0

    for event_id, title, url in rows:
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            main = soup.find("main")

            if main is None:
                raise ValueError("No main content found")

            description = main.get_text(" ", strip=True)

            if len(description) < 100:
                raise ValueError("Description unexpectedly short")

            cursor = connection.execute("""
                UPDATE events
                SET description = ?
                WHERE id = ?
                  AND company = 'Notion'
                  AND (description IS NULL OR TRIM(description) = '')
            """, (description, event_id))

            connection.commit()
            updated += cursor.rowcount

            print(f"Updated {event_id}: {title}")

        except (requests.RequestException, ValueError) as error:
            failed += 1
            print(f"Failed {event_id}: {error}")

        time.sleep(1)

    print(f"\nUpdated: {updated}")
    print(f"Failed: {failed}")

finally:
    connection.close()