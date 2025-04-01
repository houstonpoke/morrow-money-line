
import streamlit as st
import requests

def generate_bet_reasoning(row):
    groq_api_key = st.secrets.get("GROQ_API_KEY", "")

    prompt = f"""
    Analyze this sports bet:
    - Matchup: {row['team1']} vs {row['team2']}
    - Spread: {row['spread']} @ {row['book']}
    - Total: {row['total']}
    - Model Line: {row['true_line']:.2f}
    - EV: {row['implied_edge']:.2f}%
    - Edge: {row['true_line'] - float(row['spread']):.2f}

    Is this a good value bet? Explain briefly.
    """

    st.write("🧠 Sending to Groq:")
    st.code(prompt)

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mixtral-8x7b-32768",
                "messages": [
                    {"role": "system", "content": "You are a sharp sports betting assistant that explains betting value in plain English."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        result = response.json()
        st.write("📦 Groq raw result:")
        st.json(result)

        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"]
        else:
            return "⚠️ No rationale returned from Groq."
    except Exception as e:
        return f"❌ Groq API Error: {e}"

def render():
    st.title("🧪 GROQ TEST — One Fake Bet")

    row = {
        "team1": "Texas",
        "team2": "Oklahoma",
        "spread": "-3.5",
        "book": "DraftKings",
        "total": "147.5",
        "true_line": 2.0,
        "implied_edge": 7.1,
    }

    st.subheader(f"{row['team1']} vs {row['team2']}")
    st.markdown(f"**Spread:** {row['spread']} @ {row['book']}")
    st.markdown(f"**Total:** {row['total']}")
    st.markdown(f"**Model Line:** {row['true_line']}")
    st.markdown(f"**EV:** `{row['implied_edge']}%`")

    if st.button("🧠 Why this bet?"):
        with st.spinner("Asking Groq..."):
            explanation = generate_bet_reasoning(row)
        st.markdown("### ✅ GPT Output:")
        st.markdown(explanation)
