import streamlit as st
from tabs import nba_tab, ncaab_tab, nfl_tab, cfb_tab, research_hub
from utils.helpers import load_logo, display_ticker

st.set_page_config(page_title="Morrow's Moneyline", layout="wide")

st.markdown("<style>@import url('https://fonts.googleapis.com/css2?family=Rubik&display=swap'); html, body, [class*='css'] { font-family: 'Rubik', sans-serif; }</style>", unsafe_allow_html=True)
load_logo()

tabs = {
    "🏠 Dashboard": nba_tab.render,
    "🏀 NCAA Basketball": ncaab_tab.render,
    "🏈 NFL": nfl_tab.render,
    "🎓 College Football": cfb_tab.render,
    "📊 Research Hub": research_hub.render
}

selected_tab = st.sidebar.radio("Navigate", list(tabs.keys()))
tabs[selected_tab]()
