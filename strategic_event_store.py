
import sqlite3
from pathlib import Path
from datetime import date

DATABASE_PATH = Path(__file__).parent / "competitor_watch.db"


def validate_finding(finding):
    required_fields = [
        "company",
        "title",
        "event_date",
        "significance_score",
        "summary",
        "source_ids",
    ]

    for field in required_fields:
        if field not in finding:
            raise ValueError(f"Missing required field: {field}")

    for field in ["company", "title", "summary"]:
        if not isinstance(finding[field], str) or not finding[field].strip():
            raise ValueError(f"{field} must be a non-empty string.")

    try:
        date.fromisoformat(finding["event_date"])
    except (ValueError, TypeError):
        raise ValueError("Event date must be a valid YYYY-MM-DD date.")

    score = finding["significance_score"]

    if type(score) is not int or not 1 <= score <= 10:
        raise ValueError(
            "Significance score must be an integer between 1 and 10."
        )


def validate_sources(connection, finding):
    source_ids = finding["source_ids"]

    if not isinstance(source_ids, list) or not source_ids:
        raise ValueError("At least one source ID is required.")

    if len(source_ids) != len(set(source_ids)):
        raise ValueError("Duplicate source IDs are not allowed.")

    for source_id in source_ids:
        if type(source_id) is not int:
            raise ValueError("Source IDs must be integers.")

        row = connection.execute(
            "SELECT company FROM events WHERE id = ?",
            (source_id,),
        ).fetchone()

        if row is None:
            raise ValueError(f"Source ID {source_id} does not exist.")

        if row[0] != finding["company"]:
            raise ValueError(
                f"Source ID {source_id} belongs to {row[0]}, "
                f"not {finding['company']}."
            )


def save_strategic_event(finding):
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        validate_finding(finding)
        validate_sources(connection, finding)
        existing = connection.execute(

            """
            SELECT id FROM strategic_events
            WHERE company = ? AND title = ? AND event_date = ?
            """,
            (
                finding["company"],
                finding["title"],
                finding["event_date"],
            ),
        ).fetchone()

                
        if existing is not None:
            strategic_event_id = existing[0]

            for source_id in finding["source_ids"]:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO strategic_event_sources
                        (strategic_event_id, source_event_id)
                    VALUES (?, ?)
                    """,
                    (strategic_event_id, source_id),
                )

            connection.commit()
            return strategic_event_id

        cursor = connection.execute(
            """
            INSERT INTO strategic_events
                (company, title, event_date, significance_score, summary)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                finding["company"],
                finding["title"],
                finding["event_date"],
                finding["significance_score"],
                finding["summary"],
            ),
        )

        strategic_event_id = cursor.lastrowid

        for source_id in finding["source_ids"]:
            connection.execute(
                """
                INSERT INTO strategic_event_sources
                    (strategic_event_id, source_event_id)
                VALUES (?, ?)
                """,
                (strategic_event_id, source_id),
            )

        connection.commit()

        return strategic_event_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
