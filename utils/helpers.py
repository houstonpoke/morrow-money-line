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
