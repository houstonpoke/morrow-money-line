import streamlit as st
import pandas as pd
import random
import uuid

def get_live_odds(sport):
    if sport not in ["NBA", "NCAAB", "NFL", "CFB"]:
        return pd.DataFrame()

    teams = [("Lakers", "Warriors"), ("Thunder", "Mavericks"), ("Celtics", "Bucks")]
    data = []

    for team1, team2 in teams:
        data.append({
            "id": str(uuid.uuid4()),
            "team1": team1,
            "team2": team2,
            "spread": random.choice(["-3.5", "+2.5", "-1"]),
            "total": random.choice([210.5, 214.0, 218.5]),
            "book": random.choice(["FanDuel", "DraftKings", "Caesars"]),
            "true_line": random.uniform(-2.5, +2.5),
            "implied_edge": random.uniform(-5, 10),
            "win_prob": random.uniform(0.40, 0.60)
        })

    return pd.DataFrame(data)

def calculate_ev(row):
    true_line = row["true_line"]
    market_spread = float(row["spread"])
    edge = true_line - market_spread
    ev = row["implied_edge"]
    status = "green" if ev > 3 else "yellow" if ev > 0 else "red"
    return ev, edge, status

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
        st.markdown("""
        <marquee behavior="scroll" direction="left" scrollamount="4" style="color:white;background:black;padding:6px;font-weight:bold;font-size:14px;border-radius:8px;margin-bottom:10px">
        📈 WTI Crude: $82.17 | 🏀 Celtics -3.5 | 🧠 Edge Alert: Thunder +2.5 (EV +5.2%) | 💰 Henry Hub Gas: $2.19
        </marquee>
        """, unsafe_allow_html=True)

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
