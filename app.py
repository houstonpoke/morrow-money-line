import streamlit as st
from tabs import nba_tab, ncaab_tab, nfl_tab, cfb_tab, research_hub
import openai

# ✅ MUST be the first Streamlit call
st.set_page_config(page_title="Morrow's Moneyline", layout="wide")

# ✅ Updated for openai>=1.0.0
client = openai.OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))

# 🧪 TEMPORARY GPT TEST BUTTON
if st.button("🧪 Test GPT"):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "What's the spread of a sharp bet?"}],
            max_tokens=50
        )
        st.success("✅ GPT test successful!")
        st.write(response.choices[0].message.content.strip())
    except Exception as e:
        st.error(f"GPT Test Error: {e}")

# ✅ Custom styling
st.markdown("<style>@import url('https://fonts.googleapis.com/css2?family=Rubik&display=swap'); html, body, [class*='css'] { font-family: 'Rubik', sans-serif; }</style>", unsafe_allow_html=True)

# ✅ Sidebar Navigation
tabs = {
    "NBA": nba_tab.render,
    "NFL": nfl_tab.render,
    "NCAA Basketball": ncaab_tab.render,
    "College Football": cfb_tab.render,
    "Research Hub": research_hub.render
}

selection = st.sidebar.radio("📊 Select a Sport", list(tabs.keys()))
tabs[selection]()
