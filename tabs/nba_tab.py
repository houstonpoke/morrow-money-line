
import streamlit as st
from utils.helpers import get_live_odds, calculate_ev, color_status, add_bet_to_history
import requests

def generate_bet_reasoning(row):
    hf_token = st.secrets.get("HUGGINGFACE_API_KEY", "")

    prompt = f"""
    Analyze this sports bet:
    - Matchup: {row['team1']} vs {row['team2']}
    - Spread: {row['spread']} @ {row['book']}
    - Total: {row['total']}
    - Model Line: {row['true_line']:.2f}
    - EV: {row['implied_edge']:.2f}%
    - Edge: {row['true_line'] - float(row['spread']):.2f}

    Is this a good value bet? Explain briefly.
    """

    headers = {
        "Authorization": f"Bearer {hf_token}" if hf_token else None
    }

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
            headers=headers,
            json={"inputs": prompt}
        )
        response.raise_for_status()
        result = response.json()

        st.write("Hugging Face raw result:", result)

        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"]
        else:
            return "⚠️ No rationale returned. Try again later."
    except Exception as e:
        return f"❌ Hugging Face Error: {e}"

def render():
    st.title("🏀 NBA Betting Edge")
    odds_data = get_live_odds("NBA")

    if odds_data.empty:
        st.warning("No NBA odds available right now.")
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
