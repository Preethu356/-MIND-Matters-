import os
import logging
from typing import List, Dict, Any, Optional

import streamlit as st
import toml
from dotenv import load_dotenv

# Try OpenAI import
try:
    import openai
except Exception:
    openai = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mh_consult_app")

# Load env for local development (.env)
load_dotenv()

# --- Load config ---
DEFAULT_CONFIG = {
    "app": {
        "title": "MH Consult — Mental Health Consultation",
        "warning_message": "This app is informational and not a replacement for licensed care.",
        "crisis_hotline": "Replace with national crisis hotline",
        "crisis_text": "Replace with crisis text line"
    },
    "model": {
        "default_model": "gpt-4o-mini",
        "max_tokens": 512,
        "temperature": 0.7
    },
    "style": {
        "background_color": "#FFFFFF"
    }
}

def load_config(path: str = "config.toml"):
    try:
        if os.path.exists(path):
            cfg = toml.load(path)
            # merge shallowly
            merged = DEFAULT_CONFIG.copy()
            for k in DEFAULT_CONFIG:
                if k in cfg and isinstance(cfg[k], dict):
                    merged[k].update(cfg[k])
            return merged
        else:
            return DEFAULT_CONFIG
    except Exception as e:
        logger.exception("Failed loading config, using defaults.")
        return DEFAULT_CONFIG

config = load_config("config.toml")
app_config = config["app"]
model_config = config["model"]
style_config = config["style"]

st.set_page_config(page_title=app_config.get("title"), page_icon="🧠", layout="centered")
st.markdown(f"""<style>.main{{background-color:{style_config.get('background_color')}}}</style>""", unsafe_allow_html=True)

# Session state
def initialize_session_state():
    if "messages" not in st.session_state:
        system_prompt = (
            "You are an empathetic mental health consultation assistant for educational purposes. "
            "You must not provide clinical diagnoses. If the user indicates immediate danger or self-harm, "
            "provide crisis resources and encourage contacting emergency services."
        )
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": f"Hello — I'm here to provide information and support. {app_config.get('warning_message')} How can I help?"}
        ]

CRISIS_KEYWORDS = [
    "kill myself", "suicide", "end it all", "want to die",
    "harm myself", "self harm", "hurt myself", "not want to live",
    "suicidal"
]

def contains_crisis_keywords(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in CRISIS_KEYWORDS)

def crisis_response() -> str:
    return (
        "I am really sorry you are feeling this way. Please contact immediate support:\n"
        f"- Crisis Hotline: {app_config.get('crisis_hotline')}\n"
        f"- Crisis Text: {app_config.get('crisis_text')}\n"
        "- Emergency services if you are in immediate danger.\n"
    )

def get_openai_client():
    if openai is None:
        return None
    # Prefer streamlit secrets (secure on cloud) then env var
    api_key = st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") and st.secrets.get("OPENAI_API_KEY") else os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        os.environ["OPENAI_API_KEY"] = api_key
        client = openai.OpenAI(api_key=api_key) if hasattr(openai, "OpenAI") else openai
        return client
    except Exception as e:
        logger.exception("OpenAI client init failed: %s", e)
        return None

def trim_messages(messages: List[Dict[str, str]], keep: int = 6):
    system = [m for m in messages if m.get("role") == "system"]
    others = [m for m in messages if m.get("role") != "system"]
    return system + others[-keep:]

def get_ai_response(messages: List[Dict[str, str]]):
    client = get_openai_client()
    if client is None:
        return "AI not available: configure OPENAI_API_KEY in Streamlit secrets or the environment."
    try:
        msgs = trim_messages(messages, keep=6)
        resp = client.chat.completions.create(
            model=model_config.get("default_model"),
            messages=msgs,
            max_tokens=model_config.get("max_tokens", 512),
            temperature=model_config.get("temperature", 0.7)
        )
        if hasattr(resp, "choices") and len(resp.choices) > 0:
            c = resp.choices[0]
            if hasattr(c, "message") and getattr(c.message, "content", None):
                return c.message.content
            elif getattr(c, "text", None):
                return c.text
        return str(resp)
    except Exception as e:
        logger.exception("OpenAI call failed: %s", e)
        return "Sorry, I'm having trouble talking to the AI service right now."

# UI
initialize_session_state()

# Sidebar - safety and API
with st.sidebar:
    st.header("Safety & Settings")
    st.markdown(f"**Crisis hotline:** {app_config.get('crisis_hotline')}\n\n**Crisis text:** {app_config.get('crisis_text')}")
    st.markdown(f"**Warning:** {app_config.get('warning_message')}")
    st.markdown("---")
    st.markdown("**OpenAI (for testing)**\nYou can paste an API key here for temporary session use.")
    key = st.text_input("OpenAI API Key", type='password')
    if key:
        os.environ['OPENAI_API_KEY'] = key
        st.success("API key set for this session.")
    if st.button('Clear conversation'):
        sys_msg = next((m for m in st.session_state.messages if m.get('role') == 'system'), None)
        st.session_state.messages = [sys_msg] if sys_msg else []
        st.session_state.messages.append({'role': 'assistant', 'content': f'Conversation cleared. {app_config.get("warning_message")}'})
        st.experimental_rerun()

st.title(app_config.get('title'))
st.caption('This app provides informational support only. Not a replacement for licensed mental health care.')

# Show chat
for m in st.session_state.messages[1:]:
    role = m.get('role','assistant')
    with st.chat_message(role):
        st.markdown(m.get('content',''))

# Input
prompt = st.chat_input('What would you like to talk about?')
if prompt:
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    if contains_crisis_keywords(prompt):
        reply = crisis_response()
    else:
        with st.spinner('Thinking...'):
            reply = get_ai_response(st.session_state.messages)

    st.session_state.messages.append({'role': 'assistant', 'content': reply})
    with st.chat_message('assistant'):
        st.markdown(reply)
    st.experimental_rerun()
