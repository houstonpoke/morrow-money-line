
import streamlit as st
from utils.helpers import get_live_odds, calculate_ev, color_status, add_bet_to_history
import requests

def generate_bet_reasoning(row):
    groq_api_key = st.secrets.get("GROQ_API_KEY", "")

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

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mixtral-8x7b-32768",
                "messages": [
                    {"role": "system", "content": "You are a sharp sports betting assistant that explains betting value in plain English."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        result = response.json()

        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"]
        else:
            return "⚠️ No rationale returned from Groq."

    except Exception as e:
        return f"❌ Groq API Error: {e}"

def render():
    st.title("🏀 NBA Betting Edge")

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
                    with st.spinner("Asking Mistral via Groq..."):
                        explanation = generate_bet_reasoning(row)
                    st.session_state.shown_explanations[row["id"]] = explanation

                if add:
                    add_bet_to_history(row, row["ev"], row["edge"], row["status"])

            if row["id"] in st.session_state.shown_explanations:
                st.markdown("### ✅ Rationale:")
                st.markdown(st.session_state.shown_explanations[row["id"]])
