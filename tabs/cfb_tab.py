import streamlit as st
from utils.helpers import get_live_odds, calculate_ev, color_status, add_bet_to_history

def render():
    st.title("College Football Betting Edge")
    odds_data = get_live_odds("CFB")

    if odds_data.empty:
        st.warning("No odds available right now.")
        return

    for _, row in odds_data.iterrows():
        matchup = f"{row['team1']} vs {row['team2']}"
        st.subheader(matchup)

        ev, edge, status = calculate_ev(row)

        col1, col2, col3 = st.columns([4, 3, 2])
        with col1:
            st.markdown(f"**Spread:** {row['spread']} @ {row['book']}")
            st.markdown(f"**Total:** {row['total']}")
        with col2:
            st.markdown(f"**EV:** `{ev:.2f}%`")
            st.markdown(f"**Morrow's Edge:** `{edge:.2f}`")
        with col3:
            st.markdown(color_status(status), unsafe_allow_html=True)
            if st.button("➕ Add to Bet History", key=f"add_{row['id']}"):
                add_bet_to_history(row, ev, edge, status)
