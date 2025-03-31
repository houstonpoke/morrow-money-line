import streamlit as st
import pandas as pd
import requests
import uuid

# Real Odds API (TheOddsAPI)
API_KEY = st.secrets["ODDS_API_KEY"]
BASE_URL = "https://api.the-odds-api.com/v4/sports"

SPORT_MAPPING = {
    "NBA": "basketball_nba",
    "NFL": "americanfootball_nfl",
    "NCAAB": "basketball_ncaab",
    "CFB": "americanfootball_ncaaf"
}

def get_live_odds(sport):
    sport_key = SPORT_MAPPING.get(sport)
    if not sport_key:
        return pd.DataFrame()

    url = f"{BASE_URL}/{sport_key}/odds/?regions=us&markets=spreads,totals&oddsFormat=american&apiKey={API_KEY}"

    try:
        res = requests.get(url)
        res.raise_for_status()
        games = res.json()
        data = []

        for game in games:
            team1, team2 = game["home_team"], [t for t in game["teams"] if t != game["home_team"]][0]
            book = game["bookmakers"][0] if game["bookmakers"] else None
            if not book:
                continue

            markets = {m["key"]: m for m in book["markets"]}
            spread = markets.get("spreads", {}).get("outcomes", [{}])[0].get("point", "N/A")
            total = markets.get("totals", {}).get("outcomes", [{}])[0].get("point", "N/A")

            data.append({
                "id": str(uuid.uuid4()),
                "team1": team1,
                "team2": team2,
                "spread": spread,
                "total": total,
                "book": book["title"],
                "true_line": float(spread) + (0.5 - 1.0),  # fake model for now
                "implied_edge": round((1.5 - abs(float(spread))) * 2, 2),  # placeholder EV logic
                "win_prob": 0.5  # placeholder for now
            })

        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"Error fetching odds: {e}")
        return pd.DataFrame()

# Existing logic stays the same below:

def calculate_ev(row):
    try:
        true_line = row["true_line"]
        market_spread = float(row["spread"])
        edge = true_line - market_spread
        ev = row["implied_edge"]
        status = "green" if ev > 3 else "yellow" if ev > 0 else "red"
        return ev, edge, status
    except:
        return 0, 0, "red"

def color_status(status):
    color_map = {
        "green": "#00C851",
        "yellow": "#ffbb33",
        "red": "#ff4444"
    }
    return f"<div style='background-color:{color_map[status]};padding:5px 10px;border-radius:10px;width:fit-content;color:white;font-weight:bold'>{status.upper()}</div>"

def load_logo():
    st.markdown("<h1 style='font-size:2.5em'>🤠 Morrow’s Moneyline</h1>", unsafe_allow_html=True)

def display_ticker():
    with st.container():
        st.markdown(\"""
        <marquee behavior='scroll' direction='left' scrollamount='4' style='color:white;background:black;padding:6px;font-weight:bold;font-size:14px;border-radius:8px;margin-bottom:10px'>
        📈 WTI Crude: $82.17 | 🏀 Celtics -3.5 | 🧠 Thunder +2.5 (EV +5.2%) | 💰 Henry Hub Gas: $2.19
        </marquee>
        \""", unsafe_allow_html=True)

def add_bet_to_history(row, ev, edge, status):
    if "bet_history" not in st.session_state:
        st.session_state.bet_history = []

    st.session_state.bet_history.append({
        "id": row["id"],
        "matchup": f"{row['team1']} vs {row['team2']}",
        "spread": row["spread"],
        "total": row["total"],
        "ev": ev,
        "edge": edge,
        "status": status,
        "book": row["book"]
    })
    st.success("Bet added to history ✅")
