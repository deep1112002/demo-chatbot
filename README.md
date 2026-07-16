# Genie — Streamlit voice + text assistant POC

A 3D avatar named **Genie** you can talk to by voice or text, replying in both
voice and text. UI and all LLM/backend logic are Python (Streamlit); the 3D
avatar rendering and browser-only voice APIs are JS, wrapped as a small custom
Streamlit component.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Add your Anthropic API key:
   ```
   cp .env.example .env
   ```
   Then open `.env` and paste your key from https://console.anthropic.com/settings/keys

3. Run the app:
   ```
   streamlit run app.py
   ```

4. Open the URL Streamlit prints (usually http://localhost:8501) in **Google Chrome**
   (best support for voice input/output).

## How it works

- **`app.py`** (Python) — all app logic: chat history in `st.session_state`,
  the Claude API call via the official `anthropic` Python SDK, and the layout.
  This is where you'd add any Python-side processing (logging, RAG, tool use, etc).
- **`genie_component/`** — a custom Streamlit component, the bridge between
  Python and the browser:
  - `__init__.py` wraps `st.components.v1.declare_component`, exposing a
    `genie_avatar()` function you call like any Streamlit widget.
  - `frontend/index.html` is plain HTML/JS (Three.js for the avatar, Web
    Speech API for voice in/out). No npm/build step — it talks to Python
    using Streamlit's native component protocol directly
    (`window.parent.postMessage`).
- **Data flow**:
  - Typed input → `st.chat_input` → Python calls `ask_genie()` → Claude reply
    is stored in session state → passed back into the component as a prop →
    JS speaks it and animates Genie's mouth.
  - Spoken input → browser's `SpeechRecognition` transcribes → JS calls
    `setComponentValue()` → Python receives it as the component's return
    value → same `ask_genie()` path as typed input.

## Notes / known limitations (by design, for speed)

- Genie's mouth animates while audio plays (talking-style animation), not
  phoneme-accurate lip sync.
- Voice output uses the browser's built-in voice. A more natural voice
  (e.g. ElevenLabs) would mean generating audio in Python and sending the
  audio bytes to the component instead of calling browser `SpeechSynthesis`.
- Voice input requires Chrome (Web Speech API support is inconsistent
  elsewhere).

## Next steps

- Swap the primitive avatar for a real 3D model (Ready Player Me `.glb` +
  Three.js `GLTFLoader`) inside `genie_component/frontend/index.html`.
- Move TTS/STT server-side in Python (e.g. Whisper for STT, ElevenLabs for
  TTS) if you want it to work outside Chrome or want a more natural voice.
- Deploy: Streamlit Community Cloud, or any host that runs Python, with
  `ANTHROPIC_API_KEY` set as a server-side environment variable.
