
import streamlit as st
import pandas as pd
import requests
import uuid

SPORT_MAPPING = {
    "NBA": "nba",
    "NFL": "nfl",
    "NCAAB": "mens-college-basketball",
    "CFB": "college-football"
}

ESPN_SCHEDULE_BASE = "https://site.api.espn.com/apis/site/v2/sports/basketball/{league}/scoreboard"

def get_live_odds(sport):
    sport_key = SPORT_MAPPING.get(sport)
    if not sport_key:
        st.warning(f"No odds source available for {sport}")
        return pd.DataFrame()

    url = ESPN_SCHEDULE_BASE.replace("{league}", sport_key)

    try:
        res = requests.get(url)
        res.raise_for_status()
        events = res.json().get("events", [])
        data = []

        for game in events:
            try:
                competitions = game.get("competitions", [])
                if not competitions:
                    continue

                comp = competitions[0]
                competitors = comp.get("competitors", [])
                if len(competitors) < 2:
                    continue

                team1 = competitors[0]["team"]["displayName"]
                team2 = competitors[1]["team"]["displayName"]

                odds = comp.get("odds", [])
                if not odds:
                    continue

                spread = odds[0].get("spread", "N/A")
                total = odds[0].get("overUnder", "N/A")
                book = odds[0].get("provider", {}).get("name", "ESPN")

                data.append({
                    "id": str(uuid.uuid4()),
                    "team1": team1,
                    "team2": team2,
                    "spread": spread,
                    "total": total,
                    "book": book,
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
