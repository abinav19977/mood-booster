import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import random
import io
import os
import json

# --- CONFIG ---
PAGE_LOGO = "535a00a0-0968-491d-92db-30c32ced7ac6.webp" 
BADGES = {5: "🥉 Bronze Achu", 10: "🥈 Silver Achu", 15: "🥇 Gold Achu", 20: "💎 Diamond Queen"}

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("Missing API Key!")
    st.stop()

# --- DYNAMIC CONTENT GENERATORS ---
def get_dynamic_friends_q(streak):
    difficulty = "Intermediate" if streak < 5 else "Hard"
    prompt = f"""
    Generate a unique {difficulty} difficulty multiple choice question about the TV show FRIENDS.
    Return ONLY a JSON object with keys: "question", "options" (list of 4), "answer" (string), "hint".
    Ensure the answer is exactly one of the options.
    """
    response = model.generate_content(prompt)
    return json.loads(response.text.replace('```json', '').replace('```', ''))

def get_dynamic_word(streak):
    difficulty = "Tricky but common" if streak < 5 else "Obscure and complex"
    prompt = f"""
    Generate one {difficulty} English word for a spelling bee.
    Return ONLY a JSON object with keys: "word", "meaning".
    """
    response = model.generate_content(prompt)
    return json.loads(response.text.replace('```json', '').replace('```', ''))

def main():
    image_exists = os.path.exists(PAGE_LOGO)
    st.set_page_config(page_title="Achus Game App", page_icon="🎮")

    # Initializing Session States
    for key in ["game_mode", "streak", "max_streak", "current_data", "q_count", "feedback"]:
        if key not in st.session_state:
            st.session_state[key] = 0 if "streak" in key or "count" in key else None

    # --- THEME CSS ---
    # Default Theme
    bg_color = "#0e1117"
    accent_gradient = "linear-gradient(135deg, #FF4B4B 0%, #FF8E8E 100%)"
    card_bg = "rgba(255, 255, 255, 0.05)"

    if st.session_state.game_mode == "friends":
        # Friends Theme (Central Perk Vibes: Purple/Coffee)
        bg_color = "#240b36"
        accent_gradient = "linear-gradient(135deg, #6b2d5c 0%, #f0a202 100%)"
        card_bg = "rgba(107, 45, 92, 0.2)"
    elif st.session_state.game_mode == "spellbee":
        # Spell Bee Theme (Honey Bee Vibes: Yellow/Black)
        bg_color = "#1a1a1a"
        accent_gradient = "linear-gradient(135deg, #fbc02d 0%, #000000 100%)"
        card_bg = "rgba(251, 192, 45, 0.1)"

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg_color}; transition: background 0.5s ease; }}
        .big-title {{ font-size: 50px !important; font-weight: 700; color: #ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }}
        .stButton>button {{ 
            border-radius: 15px; 
            background: {accent_gradient}; 
            color: white !important; 
            height: 3.5em; 
            border: none;
            font-weight: bold;
            transition: transform 0.2s;
        }}
        .stButton>button:hover {{ transform: scale(1.02); }}
        .game-card {{ 
            background: {card_bg}; 
            padding: 25px; 
            border-radius: 20px; 
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }}
        .streak-container {{ 
            background: rgba(0,0,0,0.3); 
            padding: 15px; 
            border-radius: 15px; 
            margin-bottom: 20px; 
            display: flex; 
            justify-content: space-between;
            border: 1px solid rgba(255, 215, 0, 0.3);
        }}
        </style>
        """, unsafe_allow_html=True)

    # --- HEADER ---
    col1, col2 = st.columns([1, 4])
    with col1:
        if image_exists: st.image(PAGE_LOGO, width=100)
    with col2:
        st.markdown('<p class="big-title">Achus Game App</p>', unsafe_allow_html=True)

    if not st.session_state.game_mode:
        st.write("### Choose your journey, Achumol!")
        c1, c2 = st.columns(2)
        if c1.button("☕ Friends Series Quiz"):
            st.session_state.game_mode = "friends"
            st.rerun()
        if c2.button("🐝 Spell Bee Challenge"):
            st.session_state.game_mode = "spellbee"
            st.rerun()
    else:
        # Streak Header
        st.markdown(f'<div class="streak-container"><span style="color:#fbc02d">🔥 Streak: {st.session_state.streak}</span><span style="color:#ffffff">🏆 Best: {st.session_state.max_streak}</span></div>', unsafe_allow_html=True)
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)

        # --- DYNAMIC FRIENDS QUIZ ---
        if st.session_state.game_mode == "friends":
            if not st.session_state.current_data:
                with st.spinner("Generating a 'pivotal' question..."):
                    st.session_state.current_data = get_dynamic_friends_q(st.session_state.streak)
            
            data = st.session_state.current_data
            st.write(f"### Question {st.session_state.q_count + 1}")
            st.write(f"**{data['question']}**")
            
            user_choice = st.radio("Pick your answer:", data['options'], index=None)
            
            h_col, s_col = st.columns([1, 3])
            with h_col:
                if (st.session_state.q_count + 1) % 5 == 0 and st.button("💡 Hint"):
                    st.info(data['hint'])
            
            with s_col:
                if st.button("Submit Answer"):
                    if user_choice == data['answer']:
                        st.session_state.streak += 1
                        st.session_state.max_streak = max(st.session_state.streak, st.session_state.max_streak)
                        st.session_state.q_count += 1
                        st.session_state.feedback = f"✅ Correct! {model.generate_content('Give a one-sentence Friends-themed romantic compliment.').text}"
                    else:
                        st.session_state.streak = 0
                        st.session_state.feedback = f"❌ Wrong! It was {data['answer']}. {model.generate_content('Give a Chandler Bing-style sarcastic joke.').text}"
                    st.session_state.current_data = None
                    st.rerun()

        # --- DYNAMIC SPELL BEE ---
        elif st.session_state.game_mode == "spellbee":
            if not st.session_state.current_data:
                with st.spinner("Preparing the audio..."):
                    st.session_state.current_data = get_dynamic_word(st.session_state.streak)
            
            data = st.session_state.current_data
            
            # Indian English Accent Pronunciation
            tts = gTTS(text=data['word'], lang='en', tld='co.in')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3')

            if st.checkbox("Need the meaning?"): 
                st.write(f"*Dictionary says: {data['meaning']}*")

            guess = st.text_input("Type the spelling here:", placeholder="Spelling goes here...").strip()
            if st.button("Verify"):
                if guess.lower() == data['word'].lower():
                    st.session_state.streak += 1
                    st.session_state.max_streak = max(st.session_state.streak, st.session_state.max_streak)
                    st.session_state.feedback = "✅ Spot on! You're a spelling wizard."
                else:
                    st.session_state.streak = 0
                    st.session_state.feedback = f"❌ Incorrect! The word was '{data['word']}'. Back to school! 😉"
                st.session_state.current_data = None
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.feedback:
            st.divider()
            st.info(st.session_state.feedback)
            # Badge Logic
            current_badge = next((b for s, b in reversed(list(BADGES.items())) if st.session_state.max_streak >= s), "🌱 Rookie")
            st.success(f"🏆 Rank: {current_badge}")

        if st.button("🔙 Back to Main Menu"):
            st.session_state.game_mode = None
            st.session_state.current_data = None
            st.session_state.feedback = None
            st.rerun()

if __name__ == "__main__":
    main()
