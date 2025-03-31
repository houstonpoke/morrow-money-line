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
            try:
                team1 = game.get("home_team", "Team A")
                all_teams = game.get("teams", [])
                team2 = game.get("away_team", "Team B")  # fallback to away_team if available

                if not team2 or team2 == team1:
                    # last resort fallback if teams list is available
                    if all_teams and team1 in all_teams:
                        team2 = next((t for t in all_teams if t != team1), "Team B")

                book = game["bookmakers"][0] if game["bookmakers"] else None
                if not book:
                    continue

                markets = {m["key"]: m for m in book.get("markets", [])}
                spread_outcomes = markets.get("spreads", {}).get("outcomes", [])
                total_outcomes = markets.get("totals", {}).get("outcomes", [])

                spread = spread_outcomes[0].get("point") if spread_outcomes else "N/A"
                total = total_outcomes[0].get("point") if total_outcomes else "N/A"

                data.append({
                    "id": str(uuid.uuid4()),
                    "team1": team1,
                    "team2": team2,
                    "spread": spread,
                    "total": total,
                    "book": book["title"],
                    "true_line": float(spread) + (0.5 - 1.0) if spread not in ["N/A", None] else 0.0,
                    "implied_edge": round((1.5 - abs(float(spread))) * 2, 2) if spread not in ["N/A", None] else 0.0,
                    "win_prob": 0.5
                })

            except Exception as inner_error:
                print(f"Skipping game due to error: {inner_error}")
                continue

        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"Error fetching odds: {e}")
        return pd.DataFrame()

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
