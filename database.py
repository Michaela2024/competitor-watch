import sqlite3
from date_utils import normalise_date

connection = sqlite3.connect("competitor_watch.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        event_date TEXT,
        title TEXT NOT NULL,
        description TEXT,
        source_type TEXT NOT NULL,
        source_url TEXT,
        significance_score INTEGER,
        significance_reason TEXT,
        first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        normalised_date TEXT,
        date_precision TEXT,
         UNIQUE(company, event_date, title)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS strategic_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        title TEXT NOT NULL,
        event_date TEXT,
        significance_score INTEGER,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS strategic_event_sources (
        strategic_event_id INTEGER NOT NULL,
        source_event_id INTEGER NOT NULL,

        PRIMARY KEY (strategic_event_id, source_event_id),

        FOREIGN KEY (strategic_event_id)
            REFERENCES strategic_events(id),

        FOREIGN KEY (source_event_id)
            REFERENCES events(id)
    )
""")




connection.commit()
connection.close()

print("Database ready.")

def save_event(company, event_date, title, description, source_type, source_url=None):

    normalised, precision = normalise_date(event_date)

    connection = sqlite3.connect("competitor_watch.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO events (
            company,
            event_date,
            title,
            description,
            source_type,
            source_url,
            normalised_date,
            date_precision
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company,
        event_date,
        title,
        description,
        source_type,
        source_url,
        normalised,
        precision
    ))

    inserted=cursor.rowcount== 1
    updated=False

    inserted = cursor.rowcount == 1
    updated = False

    # Fill in a missing source URL for an existing event
    if not inserted and source_url:
        cursor.execute("""
            UPDATE events
            SET source_url = ?
            WHERE company = ?
              AND event_date = ?
              AND title = ?
              AND source_url IS NULL
        """, (
            source_url,
            company,
            event_date,
            title
        ))

        updated = cursor.rowcount > 0

    if inserted:
        print(f"Saved: {title}")
    elif updated:
        print(f"Source URL updated: {title}")
    else:
        print(f"Already exists: {title}")

    connection.commit()
    connection.close()