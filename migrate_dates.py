import sqlite3
from date_utils import normalise_date

connection = sqlite3.connect("competitor_watch.db")
cursor = connection.cursor()

cursor.execute("""
    SELECT id, event_date
    FROM events
    WHERE normalised_date IS NULL
""")

events = cursor.fetchall()
updated = 0

for event_id, original_date in events:
    try:
        normalised, precision = normalise_date(original_date)

        cursor.execute("""
            UPDATE events
            SET normalised_date = ?, date_precision = ?
            WHERE id = ?
        """, (normalised, precision, event_id))

        updated += 1

    except (ValueError, TypeError):
        print(f"Could not normalise event {event_id}: {original_date}")

connection.commit()
connection.close()

print(f"Normalised {updated} of {len(events)} events.")