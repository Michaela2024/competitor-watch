###This is the agent orchestration file; configures Claude, sets permissions, and submits investigation questions
import asyncio
from dotenv import load_dotenv
import json
from strategic_event_store import save_strategic_event

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage,
    create_sdk_mcp_server,
)

from agent_tools import search_competitor_events

load_dotenv()

def show_fallback_evidence():
    import sqlite3
    from pathlib import Path

    database_path = Path(__file__).parent / "competitor_watch.db"

    connection = sqlite3.connect(
        f"file:{database_path.as_posix()}?mode=ro",
        uri=True,
    )

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT normalised_date, title, description, significance_score, source_url
            FROM events
            WHERE company = ?
              AND normalised_date BETWEEN ? AND ?
            ORDER BY significance_score DESC, normalised_date DESC
            LIMIT 10
        """, ("Asana", "2026-05-01", "2026-05-31"))

        records = cursor.fetchall()

        print("\n--- Fallback: recorded evidence ---")

        if not records:
            print("No matching evidence found in the database.")
            return

        for date, title, description,  score, source in records:
            print(f"\n{date} | Significance: {score}")
            print(title)
            print(f"Description: {description or 'Not available'}")
            print(f"Source: {source}")

        print(
            "\nThis is a database extract, not an AI-generated "
            "strategic analysis."
        )

    finally:
        connection.close()

async def main(investigation_question=None):
    # Register our Python tool with the Agent SDK
    database_server = create_sdk_mcp_server(
        name="competitor-database",
        version="1.0.0",
        tools=[search_competitor_events],
    )

    investigation_prompt = """
    You are an evidence-led competitive intelligence research assistant
    supporting a Product Manager.
    
    Investigate Asana, monday.com and Notion for March–May 2026,
    using the available competitor database tool.
    
    Your task is to produce a reliable comparative evidence report,
    not an autonomous strategic assessment.
    
    Follow these rules:
    
    1. EVIDENCE FIRST
    - Base factual claims on retrieved database records.
    - Include dates and source URLs where available.
    - Distinguish company claims from independently verified facts.
    - Never invent missing evidence or imply that a headline alone
      confirms the details of an announcement.
    
    2. IDENTIFY MEANINGFUL DEVELOPMENTS
    - Identify significant new capabilities, acquisitions,
      integrations, platform changes and commercial changes.
    - Distinguish genuinely new developments from incremental
      enhancements and previously announced capabilities.
    - Consolidate duplicate reports of the same event.
    - Treat stored significance scores as provisional, not factual.
    
    3. COMPARE WITHOUT FORCING A CONCLUSION
    - Compare the competitors across product capabilities,
      interoperability, AI agents, governance and monetisation.
    - Identify observable similarities and differences.
    - Distinguish convergence in capabilities from divergence
      in implementation or commercial approach.
    - Do not assume that shared terminology means equivalent
      functionality.
    - Do not force a conclusion of convergence or divergence.
    
    4. MAKE UNCERTAINTY EXPLICIT
    - Identify missing descriptions, incomplete coverage,
      ambiguous dates and uncorroborated announcements.
    - Distinguish absence of evidence from evidence of absence.
    - Clearly label any hypothesis as an interpretation.
    - Do not infer corporate intent, investment rationale,
      market impact or customer adoption without evidence.
    
    5. LEAVE STRATEGIC JUDGEMENT TO THE USER
    - Do not recommend strategic actions.
    - Do not present predictions or competitive positioning
      hypotheses as established conclusions.
    - Instead, identify questions a Product Manager should
      investigate before making strategic decisions.
    
    Structure the report as:
    
    A. Executive evidence summary
    B. Significant developments by competitor
    C. Comparison with the March–April baseline
    D. Cross-competitor similarities and differences
    E. Evidence gaps and limitations
    F. Questions for the Product Manager
    
    Use concise, precise language. Prioritise traceability,
    balanced comparisons and factual accuracy over producing
    a compelling strategic narrative.
    """

    options = ClaudeAgentOptions(
        mcp_servers={
            "competitor-database": database_server,
        },
        allowed_tools=[
            "mcp__competitor-database__search_competitor_events",
        ],
        max_turns=12,
        max_budget_usd=0.50,
        permission_mode="default",
        system_prompt=investigation_prompt,

    )

    prompt = investigation_question or (
    "Investigate significant competitor developments at "
    "Asana, monday.com and Notion between March and May 2026. "
    "Compare May developments against the March–April baseline. "
    "Produce an evidence-led comparative report following "
    "the structure and standards in your system instructions."
    )

    response_text = None
    investigation_succeeded=False
    print("Investigation request:", prompt)

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_text = block.text
                    print(block.text)

        elif isinstance(message, ResultMessage):
            if message.subtype == "error_max_budget_usd":
                print("Budget limit reached: investigation stopped.")
            elif message.subtype == "error_max_turns":
                print("Turn limit reached: investigation stopped.")
            else:
                print(f"Investigation finished: {message.subtype}")
                investigation_succeeded = message.subtype == "success"
            print(f"Result subtype: {message.subtype}")
            print(f"Is error: {message.is_error}")
            print("\n--- Investigation cost ---")
            print(f"API cost (USD): ${message.total_cost_usd or 0:.4f}")
            print(f"Duration: {message.duration_ms / 1000:.1f} seconds")
            print(f"Number of turns: {message.num_turns}")
            print(f"Session ID: {message.session_id}")

    # if investigation_succeeded and response_text is not None:
    #     try:
    #         findings = json.loads(response_text)

    #         if not isinstance(findings, list):
    #             raise ValueError("Expected a JSON list of findings.")

    #         for finding in findings:
    #             strategic_event_id = save_strategic_event(finding)
    #             print(f"Saved strategic finding ID: {strategic_event_id}")

    #     except (json.JSONDecodeError, TypeError, ValueError) as error:
    #         print(f"Could not process Claude's response: {error}")
    # else:
    #     print("Claude returned no successful response to process.")


if __name__ == "__main__":
    asyncio.run(main())