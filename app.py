import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import random
import io

# --- CONFIG ---
PAGE_LOGO = "535a00a0-0968-491d-92db-30c32ced7ac6.webp" 
SPELL_BEE_WORDS = ["Enthusiastic", "Serendipity", "Magnanimous", "Quintessential", "Pharaoh", "Onomatopoeia", "Bourgeois", "Mischievous", "Phenomenon", "Hierarchy"]
NICKNAMES = ["Collector Achumol", "Spelling Rani", "Einstein Achu", "Budhirakshasi", "Achu-Panda", "Chakkara-Bee", "Professor Achu"]

MALAYALAM_LINKS = [
    "https://www.youtube.com/watch?v=9two30yb62Q",
    "https://www.youtube.com/watch?v=h3ka9dCpN0I",
    "https://www.youtube.com/watch?v=yS3F3gq_0zM"
]
FRIENDS_LINKS = [
    "https://www.youtube.com/watch?v=xT5zt93BbAg",
    "https://www.youtube.com/watch?v=JZ0AGtN_Uao",
    "https://www.youtube.com/watch?v=ojTdYiBRtdU"
]

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing API Key!")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def main():
    image_exists = os.path.exists(PAGE_LOGO)
    st.set_page_config(page_title="Achumol is...", page_icon=PAGE_LOGO if image_exists else "🐘")
    
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .big-title { font-size: 50px !important; font-weight: 700; color: #FF4B4B; margin: 0; line-height: 1.2; }
        .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
        .watch-btn {
            background-color: #FF4B4B; color: white; padding: 12px 24px; text-align: center;
            text-decoration: none; display: block; font-size: 16px; font-weight: bold;
            border-radius: 10px; margin-top: 10px;
        }
        .nickname-box {
            padding: 15px; background-color: #fce4ec; border-radius: 10px; border: 2px solid #FF4B4B;
            text-align: center; font-size: 22px; font-weight: bold; color: #FF4B4B; margin: 15px 0;
        }
        .badge { color: #FFD700; font-size: 24px; font-weight: bold; text-shadow: 1px 1px 2px black; }
        </style>
        """, unsafe_allow_html=True)

    head_col1, head_col2 = st.columns([1, 4])
    with head_col1:
        if image_exists: st.image(PAGE_LOGO, width=90)
    with head_col2:
        st.markdown('<p class="big-title">Achumol is...</p>', unsafe_allow_html=True)

    # State initialization
    for key in ["mood", "note", "show_choices", "final_res", "play_spell_bee", "current_word", "nickname", "streak"]:
        if key not in st.session_state: 
            st.session_state[key] = 0 if key == "streak" else None

    # --- 1. MOOD SELECTION ---
    st.write("Enthokke ind Visesham?") 
    
    cols = st.columns(4)
    moods, icons = ["Happy", "Neutral", "Sad", "Angry"], ["😃", "😐", "😢", "😡"]
    
    for i, col in enumerate(cols):
        if col.button(f"{icons[i]} {moods[i]}", key=f"mood_{i}"):
            st.session_state.mood = moods[i]
            st.session_state.note, st.session_state.final_res, st.session_state.nickname = None, None, None
            st.session_state.show_choices, st.session_state.play_spell_bee = False, False

    if st.session_state.mood:
        st.divider()
        user_text = st.text_area("Enthenkilum extra parayan undo?", placeholder="Para...") 
        if st.button("🚀 Paraa"):
            with st.spinner(""):
                prompt = f"""
                Write a message to Achumol (partner). Mood: {st.session_state.mood}. Context: {user_text}.
                
                RULES:
                - Tone: 60% Funny, 30% Teasing, 10% Romantic.
                - Language: 60% Manglish, 40% Simple English.
                - ROMANCE RULE: Romantic or caring sentences MUST be in English only. No Manglish for romance.
                - Banter/Teasing must be in Manglish.
                - No drama or cringe. Use 'Edo' or
