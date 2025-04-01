
import streamlit as st
import openai

# Set up OpenAI client (v1+ compatible with project keys)
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Test OpenAI directly with a known simple example
def test_openai():
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use GPT-3.5 or GPT-4
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ]
        )
        st.write("✅ GPT Response:")
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"❌ OpenAI Error: {e}")

# Render the test button in the Streamlit UI
def render():
    st.title("🧪 OpenAI Test")

    if st.button("🧪 Test OpenAI"):
        test_openai()
