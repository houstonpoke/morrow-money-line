import streamlit as st
from utils.helpers import color_status
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
    st.title("🏀 NBA Betting Edge (Test Mode)")

    # Fake data row
    row = {
        "team1": "Kansas",
        "team2": "Duke",
        "spread": "-4.5",
        "book": "FanDuel",
        "total": "145.0",
        "true_line": 2.0,
        "implied_edge": 7.2,
        "status": "green",
        "id": "test_001"
    }

    st.subheader(f"{row['team1']} vs {row['team2']}")
    st.markdown(f"**Spread:** {row['spread']} @ {row['book']}")
    st.markdown(f"**Total:** {row['total']}")
    st.markdown(f"**EV:** `{row['implied_edge']:.2f}%`")
    st.markdown(f"**Edge:** `{row['true_line'] - float(row['spread']):.2f}`")
    st.markdown(color_status(row["status"]), unsafe_allow_html=True)

    if st.button("🧠 Why this bet?"):
        st.write("🧠 Button was clicked!")
        explanation = generate_bet_reasoning(row)
        st.markdown(explanation)
