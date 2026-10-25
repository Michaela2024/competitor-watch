"""Local tests for strategic-event persistence. No Claude API calls."""

import sqlite3
import tempfile
from pathlib import Path

import strategic_event_store


with tempfile.TemporaryDirectory() as temporary_folder:
    test_database = Path(temporary_folder) / "test_competitor_watch.db"
    print("Temporary database created:", test_database)

    connection = sqlite3.connect(test_database)
    try:
        connection.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE events (
                id INTEGER PRIMARY KEY,
                company TEXT NOT NULL,
                title TEXT NOT NULL
            );

            CREATE TABLE strategic_events (
                id INTEGER PRIMARY KEY,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                event_date TEXT NOT NULL,
                significance_score INTEGER NOT NULL,
                summary TEXT NOT NULL
            );

            CREATE TABLE strategic_event_sources (
                strategic_event_id INTEGER NOT NULL,
                source_event_id INTEGER NOT NULL,
                PRIMARY KEY (strategic_event_id, source_event_id),
                FOREIGN KEY (strategic_event_id) REFERENCES strategic_events(id),
                FOREIGN KEY (source_event_id) REFERENCES events(id)
            );

            CREATE UNIQUE INDEX idx_strategic_event_unique
                ON strategic_events(company, title, event_date);
            """
        )
        connection.executemany(
            "INSERT INTO events (id, company, title) VALUES (?, ?, ?)",
            [
                (190, "Asana", "Test acquisition announcement"),
                (195, "Asana", "Additional acquisition coverage"),
            ],
        )
        connection.commit()
    finally:
        connection.close()

    print("Test tables and two source events created.")

    # Change the module variable in this process only; the production database
    # and the strategic_event_store.py source file remain untouched.
    original_database_path = strategic_event_store.DATABASE_PATH
    strategic_event_store.DATABASE_PATH = test_database

    try:
        finding = {
            "company": "Asana",
            "title": "Test strategic acquisition",
            "event_date": "2026-05-28",
            "significance_score": 7,
            "summary": "A fictional acquisition used to test persistence.",
            "source_ids": [190],
        }

        first_id = strategic_event_store.save_strategic_event(finding)
        second_id = strategic_event_store.save_strategic_event(finding)
        assert first_id == second_id, "Duplicate save returned a different ID"
        print("First save ID:", first_id)
        print("Second save ID:", second_id)

        enriched_finding = {**finding, "source_ids": [190, 195]}
        enriched_id = strategic_event_store.save_strategic_event(enriched_finding)
        assert enriched_id == first_id, "Evidence enrichment created another event"

        connection = sqlite3.connect(test_database)
        try:
            events = connection.execute(
                "SELECT id, company, title FROM strategic_events"
            ).fetchall()
            links = connection.execute(
                "SELECT strategic_event_id, source_event_id "
                "FROM strategic_event_sources ORDER BY source_event_id"
            ).fetchall()
        finally:
            connection.close()

        print("Strategic events:", events)
        print("Evidence links:", links)

    finally:
        strategic_event_store.DATABASE_PATH = original_database_path
