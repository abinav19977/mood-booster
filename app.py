import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import random
import io
import os
import json
import base64

# --- CONFIG ---
INITIAL_LOGO = "images (2).jpg" # Updated based on your file list
FRIENDS_BG = "images (2).jpg"   # Updated based on your file list
VICTORY_SOUND = "https://www.myinstants.com/media/sounds/crowd-cheer.mp3"

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("Missing API Key!")
    st.stop()

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def clean_json_response(text):
    text = text.replace("```json", "").replace("```", "").strip()
    return text

def get_manglish_comment(is_correct):
    if is_correct:
        comments = ["Kidiloski! Nee puliyaanu kutto.", "Enna oru buddhi! Achu mass!", "Correct aanu! Pinne alla! 🔥"]
    else:
        comments = ["Ente ponno... poya buddhi pullu kootil! 😂", "Kashtam! Ithu ethu lokathu nina?", "Sathyam para, thookam varunundo?"]
    return random.choice(comments)

def get_dynamic_friends_q(streak):
    difficulty = "Easy" if streak < 4 else "Intermediate" if streak < 8 else "Very Hard"
    prompt = f"Generate a unique {difficulty} difficulty MCQ about FRIENDS. Return ONLY a JSON object with keys: 'question', 'options' (list of 4), 'answer', 'hint'. No markdown."
    response = model.generate_content(prompt)
    return json.loads(clean_json_response(response.text))

def get_dynamic_word(streak):
    # PROGRESSIVE DIFFICULTY
    if streak < 3: diff = "Common/Easy"
    elif streak < 7: diff = "Medium/Tricky"
    else: diff = "Complex/Hard"
    
    prompt = f"Generate one {diff} English word for a spelling bee. Return ONLY a JSON object with keys: 'word', 'meaning'. No markdown."
    response = model.generate_content(prompt)
    return json.loads(clean_json_response(response.text))

def main():
    st.set_page_config(page_title="Achus Game App", page_icon="🎮")
    
    if "game_mode" not in st.session_state:
        st.session_state.update({
            "game_mode": None, "streak": 0, "max_streak": 0, 
            "current_data": None, "feedback_msg": None, "comment": None
        })

    # --- DYNAMIC STYLING ---
    bin_str = get_base64_of_bin_file(FRIENDS_BG)
    bg_style = f"background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url('data:image/png;base64,{bin_str}'); background-size: cover;" if bin_str else "background-color: #0e1117;"

    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} }}
        .game-card {{ background: rgba(0, 0, 0, 0.85); padding: 25px; border-radius: 15px; border: 1px solid #444; color: white; }}
        .stButton>button {{ border-radius: 10px; font-weight: bold; height: 3em; }}
        .comment-text {{ color: #ffeb3b; font-style: italic; font-size: 1.1em; }}
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: white;'>Achus Game App</h1>", unsafe_allow_html=True)

    if st.session_state.game_mode is None:
        col1, col2 = st.columns(2)
        with col1: st.button("☕ Friends Quiz", on_click=lambda: st.session_state.update({"game_mode": "friends"}))
        with col2: st.button("🐝 Spell Bee", on_click=lambda: st.session_state.update({"game_mode": "spellbee"}))
    
    else:
        # Show stats
        st.info(f"🔥 Streak: {st.session_state.streak} | 🏆 Best: {st.session_state.max_streak}")
        
        # --- GAME LOGIC ---
        if st.session_state.current_data is None:
            if st.session_state.game_mode == "spellbee":
                st.session_state.current_data = get_dynamic_word(st.session_state.streak)
            else:
                st.session_state.current_data = get_dynamic_friends_q(st.session_state.streak)

        data = st.session_state.current_data

        with st.container():
            st.markdown("<div class='game-card'>", unsafe_allow_html=True)
            
            if st.session_state.game_mode == "spellbee":
                tts = gTTS(text=data['word'], lang='en', tld='co.in')
                fp = io.BytesIO(); tts.write_to_fp(fp)
                st.audio(fp, format='audio/wav')
                if st.checkbox("Need Meaning?"): st.caption(data['meaning'])
                
                user_input = st.text_input("Spell it:", key="spell_in").strip()
                if st.button("Check"):
                    if user_input.lower() == data['word'].lower():
                        st.session_state.streak += 1
                        st.session_state.feedback_msg = ("success", f"Correct! It was {data['word']}")
                        st.session_state.comment = get_manglish_comment(True)
                    else:
                        st.session_state.streak = 0
                        st.session_state.feedback_msg = ("error", f"Wrong! The word was {data['word']}")
                        st.session_state.comment = get_manglish_comment(False)
                    st.session_state.current_data = None # Reset for next word
                    st.rerun()

            else: # Friends Quiz
                st.write(f"### {data['question']}")
                ans = st.radio("Pick one:", data['options'], index=None)
                if st.button("Submit"):
                    if ans == data['answer']:
                        st.session_state.streak += 1
                        st.session_state.feedback_msg = ("success", "Correct Answer!")
                        st.session_state.comment = get_manglish_comment(True)
                    else:
                        st.session_state.streak = 0
                        st.session_state.feedback_msg = ("error", f"Wrong! Correct: {data['answer']}")
                        st.session_state.comment = get_manglish_comment(False)
                    st.session_state.current_data = None
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        # Show Feedback from previous turn
        if st.session_state.feedback_msg:
            type, msg = st.session_state.feedback_msg
            if type == "success": st.success(msg)
            else: st.error(msg)
            st.markdown(f"<p class='comment-text'>{st.session_state.comment}</p>", unsafe_allow_html=True)

        if st.button("🏠 Exit to Menu"):
            st.session_state.update({"game_mode": None, "current_data": None, "streak": 0, "feedback_msg": None})
            st.rerun()

if __name__ == "__main__":
    main()
