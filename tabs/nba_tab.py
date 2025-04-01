import streamlit as st
import requests

# Define the Claude Instant API key and URL (fixed URL)
CLAUDE_API_URL = "https://api.openrouter.ai/v1/completions"
CLAUDE_API_KEY = st.secrets["CLAUDE_API_KEY"]

def generate_bet_reasoning(row):
    spread = row['spread'] if row['spread'] not in ["N/A", None] else "unknown"
    total = row['total'] if row['total'] not in ["N/A", None] else "unknown"
    edge = row['true_line'] - float(row['spread']) if row['spread'] not in ["N/A", None] else 0.0

    prompt = f"""
    Analyze this sports bet:
    - Matchup: {row['team1']} vs {row['team2']}
    - Spread: {spread} @ {row['book']}
    - Total: {total}
    - Model Line: {row['true_line']:.2f}
    - EV: {row['implied_edge']:.2f}%
    - Edge: {edge:.2f}

    Is this a good value bet? Explain briefly.
    """

    headers = {
        "Authorization": f"Bearer {CLAUDE_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            CLAUDE_API_URL,
            headers=headers,
            json={
                "model": "claude-instant-v1",  # Claude Instant
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        result = response.json()

        if "text" in result:
            return result["text"]
        else:
            return "⚠️ No rationale returned from Claude Instant."
    except Exception as e:
        return f"❌ Claude API Error: {e}"

def render():
    st.title("🏀 NBA Betting Edge (Claude Instant)")

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

    if st.button("🧠 Why this bet?"):
        with st.spinner("Asking Claude Instant..."):
            explanation = generate_bet_reasoning(row)
        st.markdown("### ✅ GPT Output:")
        st.markdown(explanation)
