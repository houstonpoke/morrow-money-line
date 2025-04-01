# Create nba_tab.py using OpenAI SDK v1.0+ compatible with project-based API keys
nba_openai_v1_path = "/mnt/data/nba_tab_openai_v1.py"

nba_openai_v1_code = """
import streamlit as st
from utils.helpers import get_live_odds, calculate_ev, color_status, add_bet_to_history
import openai

# Set up OpenAI client (v1+ compatible with project keys)
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_bet_reasoning(row):
    spread = row['spread'] if row['spread'] not in ["N/A", None] else "unknown"
    total = row['total'] if row['total'] not in ["N/A", None] else "unknown"
    edge = row['true_line'] - float(row['spread']) if row['spread'] not in ["N/A", None] else 0.0

    prompt = f\"\"\"
    Analyze this sports bet:
    - Matchup: {row['team1']} vs {row['team2']}
    - Spread: {spread} @ {row['book']}
    - Total: {total}
    - Model Line: {row['true_line']:.2f}
    - EV: {row['implied_edge']:.2f}%
    - Edge: {edge:.2f}

    Is this a good value bet? Explain briefly.
    \"\"\"

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" if you don’t have GPT-4 access
            messages=[
                {"role": "system", "content": "You are a sharp sports betting assistant that explains betting value in plain English."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ OpenAI API Error: {e}"

def render():
    st.title("🏀 NBA Betting Edge (OpenAI)")

    odds_data = get_live_odds("NBA")
    if odds_data.empty:
        st.warning("No NBA odds available right now.")
        return

    odds_data["ev"], odds_data["edge"], odds_data["status"] = zip(*odds_data.apply(calculate_ev, axis=1))
    odds_data = odds_data.sort_values(by="ev", ascending=False)

    if "shown_explanations" not in st.session_state:
        st.session_state.shown_explanations = {}

    for _, row in odds_data.iterrows():
        with st.expander(f"{row['team1']} vs {row['team2']}"):
            st.markdown(f"**Spread:** {row['spread']} @ {row['book']}")
            st.markdown(f"**Total:** {row['total']}")
            st.markdown(f"**EV:** `{row['ev']:.2f}%` | **Edge:** `{row['edge']:.2f}`")
            st.markdown(color_status(row["status"]), unsafe_allow_html=True)

            with st.form(key=f"form_{row['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    why = st.form_submit_button("🧠 Why this bet?")
                with col2:
                    add = st.form_submit_button("➕ Add to History")

                if why:
                    with st.spinner("Talking to GPT..."):
                        explanation = generate_bet_reasoning(row)
                    st.session_state.shown_explanations[row["id"]] = explanation

                if add:
                    add_bet_to_history(row, row["ev"], row["edge"], row["status"])

            if row["id"] in st.session_state.shown_explanations:
                st.markdown("### ✅ Rationale:")
                st.markdown(st.session_state.shown_explanations[row["id"]])
"""

with open(nba_openai_v1_path, "w") as f:
    f.write(nba_openai_v1_code)

nba_openai_v1_path
