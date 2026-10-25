import sqlite3


def get_significant_events(start_date, end_date, min_score):
    connection = sqlite3.connect("competitor_watch.db")
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT
            id,
            company,
            normalised_date,
            title,
            description,
            significance_score,
            significance_reason,
            source_url
        FROM events
        WHERE normalised_date BETWEEN ? AND ?
          AND significance_score >= ?
        ORDER BY significance_score DESC, normalised_date DESC
    """, (start_date, end_date, min_score)).fetchall()

    connection.close()

    return [dict(row) for row in rows]