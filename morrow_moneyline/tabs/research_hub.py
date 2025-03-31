import streamlit as st
import pandas as pd
from utils.helpers import color_status

def render():
    st.title("📊 Research Hub")

    st.markdown("""
    Use this tab for deep dive analysis and rationale. Below are your saved bets with live status indicators.
    """)

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
        with col3:
            st.markdown(color_status(row["status"]), unsafe_allow_html=True)
            if st.button("❌ Delete Bet", key=f"delete_{row['id']}"):
                st.session_state.bet_history = [b for b in st.session_state.bet_history if b["id"] != row["id"]]
                st.rerun()

        st.markdown("---")
