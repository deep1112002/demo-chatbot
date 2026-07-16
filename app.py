import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

from genie_component import genie_avatar

load_dotenv()

st.set_page_config(page_title="Genie — voice + text assistant", layout="wide")

MODEL = "gemini-3.1-flash-lite"
SYSTEM_PROMPT = (
    "You are Genie, a friendly and concise voice assistant for loan related questions and findings. "
    "Keep replies short (1-3 sentences) since they will be read aloud. "
    "Be warm and helpful, and speak plainly."
)

# Explicitly read GEMINI_API_KEY — avoids SDK auto-picking GOOGLE_API_KEY
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


@st.cache_resource
def get_client(key: str):
    return genai.Client(api_key=key)


# ---------------- Session state ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"|"model", "content": str}]
if "last_reply" not in st.session_state:
    st.session_state.last_reply = ""
if "reply_nonce" not in st.session_state:
    st.session_state.reply_nonce = 0
if "last_voice_nonce" not in st.session_state:
    st.session_state.last_voice_nonce = 0


def build_history():
    """Convert stored messages to Gemini SDK Content list."""
    history = []
    for msg in st.session_state.messages:
        role = msg["role"]  # "user" or "model"
        history.append(
            types.Content(role=role, parts=[types.Part(text=msg["content"])])
        )
    return history


def ask_genie(user_text: str):
    """Call Gemini and update session state with the reply."""
    st.session_state.messages.append({"role": "user", "content": user_text})

    if not api_key:
        reply = "Server is missing GEMINI_API_KEY. Copy .env.example to .env and add your key."
    else:
        try:
            client = get_client(api_key)
            response = client.models.generate_content(
                model=MODEL,
                contents=build_history(),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=500,
                ),
            )
            reply = response.text or "Sorry, I couldn't generate a reply."
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                reply = "⏳ Gemini's free-tier rate limit hit. Please wait ~1 minute and try again."
            else:
                reply = f"I ran into an error: {e}"

    st.session_state.messages.append({"role": "model", "content": reply})
    st.session_state.last_reply = reply
    st.session_state.reply_nonce += 1


# ---------------- Layout ----------------
col_avatar, col_chat = st.columns([1, 1.2], gap="large")

with col_avatar:
    muted = st.checkbox("Mute spoken replies", value=False)

    result = genie_avatar(
        reply_text=st.session_state.last_reply,
        reply_nonce=st.session_state.reply_nonce,
        muted=muted,
        key="genie",
    )

    # Handle a new voice transcript coming back from the browser
    if result and result.get("nonce", 0) != st.session_state.last_voice_nonce:
        st.session_state.last_voice_nonce = result["nonce"]
        transcript = result.get("transcript", "").strip()
        if transcript:
            ask_genie(transcript)
            st.rerun()

    st.caption("Voice input needs Chrome. Voice output uses your browser's built-in speech synthesis.")

with col_chat:
    st.subheader("Genie — voice + text assistant")
    st.caption("Type or tap the mic. Genie replies out loud and in text.")

    chat_container = st.container(height=420)
    with chat_container:
        if not st.session_state.messages:
            st.markdown(":gray[Say or type something to get started.]")
        for msg in st.session_state.messages:
            display_role = "assistant" if msg["role"] == "model" else "user"
            with st.chat_message(display_role):
                st.write(msg["content"])

    typed = st.chat_input("Type a message...")
    if typed:
        ask_genie(typed)
        st.rerun()
