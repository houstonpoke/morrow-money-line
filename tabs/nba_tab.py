import streamlit as st
from utils.helpers import get_live_odds, calculate_ev, color_status, add_bet_to_history
import openai

# Optional: set OpenAI key (if not using secrets)
openai.api_key = st.secrets.get("OPENAI_API_KEY", "sk-...replace_me")

def generate_bet_reasoning(row):
    prompt = f"""
    Analyze this NBA bet for value:
    - Matchup: {row['team1']} vs {row['team2']}
    - Spread: {row['spread']} @ {row['book']}
    - Total: {row['total']}
    - True Line (model): {row['true_line']:.2f}
    - EV: {row['implied_edge']:.2f}%
    - Morrow's Edge: {row['true_line'] - float(row['spread']):.2f}

    Should this bet be considered a strong value? Give a short betting analysis.
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
    st.title("🏀 NBA Betting Edge")
    odds_data = get_live_odds("NBA")

    if odds_data.empty:
        st.warning("No odds available right now.")
        return

    # Sort by EV descending
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
            st.markdown(f"**Morrow's Edge:** `{row['edge']:.2f}`")
        with col3:
            st.markdown(color_status(row["status"]), unsafe_allow_html=True)

            if st.button("🧠 Why this bet?", key=f"why_{row['id']}"):
                explanation = generate_bet_reasoning(row)
                st.markdown(f"**GPT Analysis:** {explanation}")

            if st.button("➕ Add to History", key=f"add_{row['id']}"):
                add_bet_to_history(row, row["ev"], row["edge"], row["status"])

        st.markdown("---")
