###Tool interface, defines what Claude can request, what parameters each tool accepts, and what results it returns
import os
import sqlite3
from pathlib import Path

from claude_agent_sdk import tool

DATABASE_PATH = Path(__file__).parent / "competitor_watch.db"


@tool(
    "search_competitor_events",
    "Search stored competitor events by company and date range. "
    "Returns event titles, dates, significance scores and source IDs.",
    {
        "company": str,
        "start_date": str,
        "end_date": str,
        "min_score": int,
    },
)
async def search_competitor_events(args):
    company = args["company"]
    start_date = args["start_date"]
    end_date = args["end_date"]
    min_score=args["min_score"]
    limit = min(max(int(args.get("limit", 30)), 1), 100)

    connection = sqlite3.connect(
        f"file:{DATABASE_PATH.as_posix()}?mode=ro",
        uri=True,
    )

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                normalised_date,
                title,
                description,
                significance_score,
                source_url
            FROM events
            WHERE company = ?
                AND normalised_date BETWEEN ? AND ?
                AND significance_score >= ?
            ORDER BY significance_score DESC, normalised_date DESC
            LIMIT ?
        """, (company, start_date, end_date, min_score, limit))

        records = cursor.fetchall()

        results = [
            {
                "id": record[0],
                "date": record[1],
                "title": record[2],
                "description": record[3],
                 "significance_score": record[4],
                "source_url": record[5],
            }
            for record in records
        ]

        import json

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(results, indent=2),
                }
            ]
        }
    finally:
            connection.close()
    
@tool(
    "get_strategic_events",
    "Retrieve consolidated strategic events for a competitor, "
    "including the underlying source records.",
    {"company": str},
)
async def get_strategic_events(args):
    company = args["company"]

    connection = sqlite3.connect(
        f"file:{DATABASE_PATH.as_posix()}?mode=ro",
        uri=True,
    )

    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                company,
                title,
                event_date,
                significance_score,
                summary
            FROM strategic_events
            WHERE company = ? COLLATE NOCASE
            ORDER BY event_date DESC
            LIMIT 30
        """, (company,))

        strategic_events = []

        for event in cursor.fetchall():
            cursor.execute("""
                SELECT
                    e.id,
                    e.title,
                    e.event_date,
                    e.source_type,
                    e.source_url
                FROM strategic_event_sources AS ses
                JOIN events AS e
                  ON e.id = ses.source_event_id
                WHERE ses.strategic_event_id = ?
                ORDER BY e.event_date
            """, (event["id"],))

            sources = [
                dict(source)
                for source in cursor.fetchall()
            ]

            strategic_events.append({
                **dict(event),
                "sources": sources,
            })

        import json

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(
                    strategic_events,
                    indent=2,
                ),
            }]
        }

    finally:
        connection.close()

