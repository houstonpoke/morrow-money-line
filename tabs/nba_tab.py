
import streamlit as st
import requests
import math
import numpy as np

# Define the Claude Instant API key and URL
CLAUDE_API_URL = "https://api.openrouter.ai/v1/completions"
CLAUDE_API_KEY = st.secrets["CLAUDE_API_KEY"]

# Kelly Criterion for optimal stake sizing
def kelly_criterion(edge, bankroll_percentage=0.05):
    return edge * bankroll_percentage

# Monte Carlo Simulation for probabilistic outcomes (Simulate 10,000 games)
def monte_carlo_simulation(edge, simulations=10000):
    results = np.random.binomial(1, edge, simulations)
    win_probability = np.mean(results)
    return win_probability

# Calculate Expected Value (EV)
def calculate_ev(odds, probability):
    return (probability * odds) - (1 - probability)

# Morrow's Edge Calculation (custom metric)
def morrow_edge(spread, true_line):
    return abs(true_line - spread)

# Display function for metrics and explanations
def render():
    st.title("🏀 NBA Betting Edge (With Analysis)")

    row = {
        "team1": "Texas",
        "team2": "Oklahoma",
        "spread": -3.5,
        "book": "DraftKings",
        "total": 147.5,
        "true_line": 2.0,
        "implied_edge": 0.55,  # Example edge (55%)
    }

    st.subheader(f"{row['team1']} vs {row['team2']}")
    st.markdown(f"**Spread:** {row['spread']} @ {row['book']}")
    st.markdown(f"**Total:** {row['total']}")
    st.markdown(f"**Model Line:** {row['true_line']}")
    st.markdown(f"**EV (Expected Value):** {row['implied_edge'] * 100}%")

    # Calculate Kelly Criterion, Morrow's Edge, and Monte Carlo Simulation
    kelly_value = kelly_criterion(row['implied_edge'])
    monte_carlo_win_prob = monte_carlo_simulation(row['implied_edge'])
    morrow_edge_value = morrow_edge(row['spread'], row['true_line'])
    ev_value = calculate_ev(1.5, row['implied_edge'])  # Assuming odds of 1.5 for example

    # Display calculated values and explanations
    st.markdown(f"### 💡 Key Metrics:")
    st.markdown(f"**Kelly Criterion**: {kelly_value:.2f}")
    st.markdown(f"Explanation: The Kelly Criterion is a formula used to determine the optimal size of a bet relative to your bankroll, maximizing long-term growth while minimizing risk.")

    st.markdown(f"**Morrow's Edge**: {morrow_edge_value:.2f}")
    st.markdown(f"Explanation: Morrow’s Edge calculates the difference between the model’s predicted line and the actual betting spread, indicating the betting edge.")

    st.markdown(f"**Monte Carlo Simulation (Win Probability)**: {monte_carlo_win_prob * 100:.2f}%")
    st.markdown(f"Explanation: Monte Carlo simulations are used to model the probability of different outcomes by simulating many possible future scenarios.")

    st.markdown(f"**EV (Expected Value)**: {ev_value:.2f}")
    st.markdown(f"Explanation: EV calculates the potential profitability of a bet. Positive EV indicates a good bet, while negative EV means it's likely to lose value.")

    st.markdown("### Conclusion:")
    st.markdown("These metrics give you different ways of evaluating the bet. A high Kelly Criterion value and positive EV typically indicate a good betting opportunity, while Morrow's Edge and Monte Carlo simulations help confirm the model's accuracy.")
