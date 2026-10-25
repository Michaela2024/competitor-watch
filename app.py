
from datetime import date

import streamlit as st

from demo_queries import get_significant_events
from review_history import (
    get_events_since_last_review,
    save_current_review,
)

st.set_page_config(page_title="Competitor Watch", layout="wide")

st.title("Competitor Watch")
st.caption("Evidence-led competitor intelligence")

tab1, tab2 = st.tabs([
    "Significant developments",
    "Since my last review",
])

# TAB 1: SIGNIFICANT DEVELOPMENTS

with tab1:
    st.subheader("Significant competitor developments")

    company = st.selectbox(
        "Company",
        ["All companies", "Asana", "Notion", "monday.com"],
    )

    start_date = st.date_input("From", value=date(2026, 3, 1))
    end_date = st.date_input("To", value=date(2026, 5, 31))

    min_score = st.slider(
        "Minimum significance score",
        min_value=1,
        max_value=10,
        value=8,
    )

    if start_date > end_date:
        st.error("The start date must be before the end date.")
    else:
        events = get_significant_events(
            start_date.isoformat(),
            end_date.isoformat(),
            min_score,
        )

        if company != "All companies":
            events = [
                event for event in events
                if event["company"] == company
            ]

        st.write(f"**{len(events)} matching developments**")

        for event in events:
            st.markdown(
                f"### {event['company']}: {event['title']}"
            )

            st.write(
                f"**Date:** {event['normalised_date']} "
                f"| **Significance:** {event['significance_score']}/10"
            )

            description = event["description"] or ""

            st.write("**Source extract:**")
            st.write(
                description[:350]
                + ("…" if len(description) > 350 else "")
            )

            if len(description) > 350:
                with st.expander("Read full source extract"):
                    st.write(description)

            st.write("**AI significance assessment (provisional):**")
            st.write(
                event["significance_reason"] or "Not assessed"
            )

            if event["source_url"]:
                st.markdown(
                    f"[View source]({event['source_url']})"
                )

            st.divider()


# TAB 2: SINCE MY LAST REVIEW

with tab2:
    st.subheader("What has changed since my last review?")

    new_events = get_events_since_last_review()

    if new_events is None:
        st.info(
            "No previous review has been saved. "
            "Save your first review to establish a baseline."
        )

    elif not new_events:
        st.success(
            "No new competitor events since your last review."
        )

    else:
        st.write(f"**{len(new_events)} new developments**")

        for event in new_events:
            with st.expander(
                f"{event['company']} | {event['title']}"
            ):
                st.write("**Date:**", event["normalised_date"])

                st.write(
                    "**Significance:**",
                    event["significance_score"],
                )

                description = event["description"] or ""
                st.write(
                    "**Source extract:**",
                    description[:350]
                    + ("…" if len(description) > 350 else ""),
                )

                if len(description) > 350:
                    st.write("**Full source extract:**")
                    st.write(description)

                st.write(
                    "**AI assessment (provisional):**",
                    event["significance_reason"] or "Not assessed",
                )

                if event["source_url"]:
                    st.markdown(
                        f"[View source]({event['source_url']})"
                    )

    st.divider()

    if st.button("Save current review", type="primary"):
        review_id, count = save_current_review()

        st.success(
            f"Review #{review_id} saved. "
            f"Snapshot includes {count} competitor events."
        )

        st.rerun()
