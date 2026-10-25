import sqlite3


def initialise_review_history():
    connection = sqlite3.connect("competitor_watch.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS review_events (
            review_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            PRIMARY KEY (review_id, event_id),
            FOREIGN KEY (review_id) REFERENCES reviews(id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    connection.commit()
    connection.close()

def get_unreviewed_events():
    connection = sqlite3.connect("competitor_watch.db")
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT
            e.id,
            e.company,
            e.normalised_date,
            e.title,
            e.description,
            e.significance_score,
            e.significance_reason,
            e.source_url
        FROM events e
        WHERE NOT EXISTS (
            SELECT 1
            FROM review_events re
            WHERE re.event_id = e.id
        )
        ORDER BY e.normalised_date DESC, e.id DESC
    """).fetchall()

    connection.close()
    return [dict(row) for row in rows]

def save_review(event_ids):
    if not event_ids:
        raise ValueError("Cannot save a review without events.")

    connection = sqlite3.connect("competitor_watch.db")

    try:
        cursor = connection.execute(
            "INSERT INTO reviews DEFAULT VALUES"
        )
        review_id = cursor.lastrowid

        connection.executemany(
            """
            INSERT INTO review_events (review_id, event_id)
            VALUES (?, ?)
            """,
            [(review_id, event_id) for event_id in set(event_ids)]
        )

        connection.commit()
        return review_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def get_events_since_last_review():
    connection = sqlite3.connect("competitor_watch.db")
    connection.row_factory = sqlite3.Row

    last_review = connection.execute("""
        SELECT id
        FROM reviews
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    if last_review is None:
        connection.close()
        return None

    rows = connection.execute("""
        SELECT
            e.id,
            e.company,
            e.normalised_date,
            e.title,
            e.description,
            e.significance_score,
            e.significance_reason,
            e.source_url
        FROM events e
        WHERE NOT EXISTS (
            SELECT 1
            FROM review_events re
            WHERE re.review_id = ?
              AND re.event_id = e.id
        )
        ORDER BY e.normalised_date DESC, e.id DESC
    """, (last_review["id"],)).fetchall()

    connection.close()
    return [dict(row) for row in rows]

def save_current_review():
    connection = sqlite3.connect("competitor_watch.db")

    try:
        event_ids = [
            row[0]
            for row in connection.execute(
                "SELECT id FROM events"
            ).fetchall()
        ]

        cursor = connection.execute(
            "INSERT INTO reviews DEFAULT VALUES"
        )
        review_id = cursor.lastrowid

        connection.executemany(
            """
            INSERT INTO review_events (review_id, event_id)
            VALUES (?, ?)
            """,
            [(review_id, event_id) for event_id in event_ids]
        )

        connection.commit()
        return review_id, len(event_ids)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
        
if __name__ == "__main__":
    initialise_review_history()
    print("Review history tables ready.")