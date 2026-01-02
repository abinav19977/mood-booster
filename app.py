import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import random
import io
import os
import json
import base64

# --- CONFIG ---
INITIAL_LOGO = "image_923a6b.png"
FRIENDS_BG = "image_923a6b.png"
BADGES = {5: "🥉 Bronze Achu", 10: "🥈 Silver Achu", 15: "🥇 Gold Achu", 20: "💎 Diamond Queen"}
VICTORY_SOUND = "https://www.myinstants.com/media/sounds/crowd-cheer.mp3"

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("Missing API Key!")
    st.stop()

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_dynamic_friends_q(streak):
    difficulty = "Easy" if streak < 4 else "Intermediate" if streak < 8 else "Very Hard"
    prompt = f"Generate a unique {difficulty} difficulty MCQ about FRIENDS. Return ONLY a JSON object with keys: 'question', 'options' (list of 4), 'answer', 'hint'. No markdown."
    response = model.generate_content(prompt)
    return json.loads(response.text.strip())

def get_dynamic_word(streak):
    difficulty = "Common" if streak < 5 else "Medium" if streak < 10 else "Extremely Hard"
    prompt = f"Generate one {difficulty} English word for a spelling bee. Return ONLY a JSON object with keys: 'word', 'meaning'. No markdown."
    response = model.generate_content(prompt)
    return json.loads(response.text.strip())

def main():
    st.set_page_config(page_title="Achus Game App", page_icon="🎮")
    
    if "game_mode" not in st.session_state:
        st.session_state.update({
            "game_mode": None, "streak": 0, "max_streak": 0, 
            "current_data": None, "q_count": 0, "feedback": None,
            "next_hint_available": 0, "show_hint": False,
            "correct_answered": False
        })

    # --- DYNAMIC STYLING ---
    bg_style = "background-color: #0e1117;" 
    accent = "linear-gradient(135deg, #FF4B4B 0%, #FF8E8E 100%)"
    card_color = "rgba(255, 255, 255, 0.05)"

    if st.session_state.game_mode == "friends":
        try:
            bin_str = get_base64_of_bin_file(FRIENDS_BG)
            bg_style = f"background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('data:image/png;base64,{bin_str}'); background-size: cover; background-attachment: fixed;"
        except:
            bg_style = "background-color: #240b36;"
        accent = "linear-gradient(135deg, #6b2d5c 0%, #f0a202 100%)"
        card_color = "rgba(0, 0, 0, 0.9)"
    elif st.session_state.game_mode == "spellbee":
        bg_style = "background-color: #1a1a1a;"
        accent = "linear-gradient(135deg, #fbc02d 0%, #000000 100%)"
        card_color = "rgba(251, 192, 45, 0.15)"

    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} }}
        .big-title {{ font-size: 42px !important; font-weight: 700; color: white; text-align: center; margin-bottom: 20px; }}
        .game-card {{ background: {card_color}; padding: 30px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); color: white; }}
        .stButton>button {{ border-radius: 12px; background: {accent}; color: white !important; font-weight: bold; border: none; height: 3.5em; width: 100%; }}
        .streak-container {{ background: rgba(0,0,0,0.7); padding: 12px; border-radius: 15px; display: flex; justify-content: space-between; border: 1px solid gold; margin-bottom: 20px; color: gold; font-weight: bold; }}
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<p class="big-title">Achus Game App</p>', unsafe_allow_html=True)

    if st.session_state.game_mode is None:
        col_l, col_r = st.columns([1, 1])
        with col_l:
            if os.path.exists(INITIAL_LOGO):
                st.image(INITIAL_LOGO, use_container_width=True)
        with col_r:
            st.write("### Choose a game, Achumol!")
            if st.button("☕ Friends Series Quiz"):
                st.session_state.game_mode = "friends"
                st.rerun()
            if st.button("🐝 Spell Bee Challenge"):
                st.session_state.game_mode = "spellbee"
                st.rerun()
    
    else:
        st.markdown(f'<div class="streak-container"><span>🔥 Streak: {st.session_state.streak}</span><span>🏆 Best: {st.session_state.max_streak}</span></div>', unsafe_allow_html=True)
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)

        # FRIENDS QUIZ LOGIC
        if st.session_state.game_mode == "friends":
            if st.session_state.current_data is None:
                st.session_state.current_data = get_dynamic_friends_q(st.session_state.streak)
            
            data = st.session_state.current_data
            st.write(f"#### Question {st.session_state.q_count + 1}")
            st.write(f"**{data['question']}**")
            choice = st.radio("Options:", data['options'], index=None)
            
            if st.button("Submit Answer"):
                if choice == data['answer']:
                    st.session_state.streak += 1
                    st.session_state.max_streak = max(st.session_state.streak, st.session_state.max_streak)
                    st.session_state.q_count += 1
                    st.session_state.feedback = "✅ Correct!"
                else:
                    st.session_state.streak = 0
                    st.session_state.feedback = f"❌ Incorrect! It was {data['answer']}."
                st.session_state.current_data = None
                st.rerun()

        # SPELL BEE LOGIC (WITH NEXT BUTTON)
        elif st.session_state.game_mode == "spellbee":
            if st.session_state.current_data is None:
                st.session_state.current_data = get_dynamic_word(st.session_state.streak)
                st.session_state.correct_answered = False
            
            data = st.session_state.current_data
            
            if not st.session_state.correct_answered:
                tts = gTTS(text=data['word'], lang='en', tld='co.in')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                st.write("🔊 Listen carefully:")
                st.audio(fp, format='audio/wav')
                
                guess = st.text_input("Type the word:").strip()
                if st.button("Verify Spelling"):
                    if guess.lower() == data['word'].lower():
                        st.session_state.streak += 1
                        st.session_state.max_streak = max(st.session_state.streak, st.session_state.max_streak)
                        st.session_state.feedback = "✅ Spot on!"
                        st.session_state.correct_answered = True
                    else:
                        st.session_state.streak = 0
                        st.session_state.feedback = f"❌ Wrong! It was '{data['word']}'."
                        st.session_state.current_data = None
                    st.rerun()
            else:
                st.success(st.session_state.feedback)
                if st.button("➡️ Next Question"):
                    st.session_state.current_data = None
                    st.session_state.feedback = None
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.streak == 10:
            st.balloons()
            st.audio(VICTORY_SOUND, format="audio/mp3", autoplay=True)

        if st.button("🏠 Home Menu"):
            st.session_state.update({"game_mode": None, "current_data": None, "feedback": None, "streak": 0})
            st.rerun()

if __name__ == "__main__":
    main()
