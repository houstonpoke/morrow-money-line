import streamlit as st
from utils.helpers import get_live_odds, calculate_ev, color_status, add_bet_to_history
import openai

openai.api_key = st.secrets.get("OPENAI_API_KEY", "sk-...replace_me")

def generate_bet_reasoning(row):
    prompt = f"""
    Analyze this NFL bet:
    - Matchup: {row['team1']} vs {row['team2']}
    - Spread: {row['spread']} @ {row['book']}
    - Total: {row['total']}
    - Model Line: {row['true_line']:.2f}
    - EV: {row['implied_edge']:.2f}%
    - Edge: {row['true_line'] - float(row['spread']):.2f}

    Give a short betting explanation.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Error: {e}"

def render():
    st.title("🏈 NFL Betting Edge")
    odds_data = get_live_odds("NFL")

    if odds_data.empty:
        st.warning("No NFL odds available right now.")
        return

    odds_data["ev"], odds_data["edge"], odds_data["status"] = zip(*odds_data.apply(calculate_ev, axis=1))
    odds_data = odds_data.sort_values(by="ev", ascending=False)

    for _, row in odds_data.iterrows():
        st.subheader(f"{row['team1']} vs {row['team2']}")

        col1, col2, col3 = st.columns([4, 3, 2])
        with col1:
            st.markdown(f"**Spread:** {row['spread']} @ {row['book']}")
            st.markdown(f"**Total:** {row['total']}")
        with col2:
            st.markdown(f"**EV:** `{row['ev']:.2f}%`")
            st.markdown(f"**Edge:** `{row['edge']:.2f}`")
        with col3:
            st.markdown(color_status(row["status"]), unsafe_allow_html=True)

            if st.button("🧠 Why this bet?", key=f"why_{row['id']}"):
                st.markdown(generate_bet_reasoning(row))

            if st.button("➕ Add to History", key=f"add_{row['id']}"):
                add_bet_to_history(row, row["ev"], row["edge"], row["status"])

        st.markdown("---")
