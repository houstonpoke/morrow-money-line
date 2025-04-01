
import streamlit as st
import requests

# Define the Claude Instant API key and URL
CLAUDE_API_URL = "https://api.openrouter.ai/v1/completions"
CLAUDE_API_KEY = st.secrets["CLAUDE_API_KEY"]

def render():
    st.title("🏀 NBA Betting Edge")

    # Simplified for testing purposes, removing rationale/why this bet logic
    row = {
        "team1": "Texas",
        "team2": "Oklahoma",
        "spread": "-3.5",
        "book": "DraftKings",
        "total": "147.5",
        "true_line": 2.0,
        "implied_edge": 7.1,
    }

    st.subheader(f"{row['team1']} vs {row['team2']}")
    st.markdown(f"**Spread:** {row['spread']} @ {row['book']}")
    st.markdown(f"**Total:** {row['total']}")
    st.markdown(f"**Model Line:** {row['true_line']}")
    st.markdown(f"**EV:** `{row['implied_edge']}%`")

    st.write("Test complete! No rationale, no logic. Just displaying game data.")
