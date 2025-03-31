import streamlit as st
import pandas as pd
from utils.helpers import color_status

# Optional: for GPT functionality
import openai

# SET YOUR OPENAI API KEY HERE or use streamlit secrets
openai.api_key = st.secrets.get("OPENAI_API_KEY", "sk-...replace_me")

def generate_gpt_rationale(bet):
    prompt = f"""
    Analyze the following bet:
    - Matchup: {bet['matchup']}
    - Spread: {bet['spread']}
    - Total: {bet['total']}
    - Book: {bet['book']}
    - EV: {bet['ev']:.2f}%
    - Morrow's Edge: {bet['edge']:.2f}
    
    Give a short betting analysis explaining why this could be a good value bet. Use clear, confident language.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Error generating rationale: {e}"

def render():
    st.title("📊 Research Hub")

    if "bet_history" not in st.session_state or len(st.session_state.bet_history) == 0:
        st.info("No bets added yet.")
        return

    df = pd.DataFrame(st.session_state.bet_history)

    for idx, row in df.iterrows():
        col1, col2, col3 = st.columns([4, 3, 2])
        with col1:
            st.subheader(row["matchup"])
            st.markdown(f"**Spread:** {row['spread']} | **Total:** {row['total']}")
            st.markdown(f"**Book:** {row['book']}")
        with col2:
            st.markdown(f"**EV:** `{row['ev']:.2f}%`")
            st.markdown(f"**Morrow's Edge:** `{row['edge']:.2f}`")
            st.markdown(f"**Status:** {color_status(row['status'])}", unsafe_allow_html=True)
        with col3:
            if st.button("🧠 Explain This Bet", key=f"gpt_{row['id']}"):
                explanation = generate_gpt_rationale(row)
                st.markdown(f"**GPT Analysis:**\n\n{explanation}")

            if st.button("❌ Delete", key=f"delete_{row['id']}"):
                st.session_state.bet_history = [b for b in st.session_state.bet_history if b["id"] != row["id"]]
                st.rerun()

        st.markdown("---")
