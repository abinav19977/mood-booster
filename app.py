import streamlit as st
import google.generativeai as genai
import random
import json
import base64
import os

# --- CONFIG ---
FRIENDS_BG = "images (2).jpg" 
LOGO_FILE = "535a00a0-0968-491d-92db-30c32ced7ac6.webm" 

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("Missing API Key!")
    st.stop()

def get_base64_of_bin_file(bin_file):
    try:
        if os.path.exists(bin_file):
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
    except: return ""
    return ""

def clean_json_response(text):
    return text.replace("```json", "").replace("```", "").strip()

def get_manglish_comment(is_correct):
    if is_correct:
        comments = ["Kidiloski! Physio puliyaanu kutto. 🔥", "Enna oru clinic sense! Achu mass!", "Correct aanu! Pinne alla!"]
    else:
        comments = ["Ente ponno... poya buddhi BD Chaurasia-il illa! 😂", "Kashtam! Ithu ethu nerve aanu mwole?", "Sathyam para, thookam varunundo?"]
    return random.choice(comments)

# --- AI GENERATION ---
def get_anatomy_data(mode, topic, streak):
    if mode == "general":
        prompt = f"Topic: {topic}. Generate a BD Chaurasia style MCQ. Return ONLY JSON: {{'question','options','answer','explanation','link'}}. Difficulty: {'Easy' if streak < 5 else 'Hard'}."
    else:
        prompt = f"Topic: {topic}. Generate a Physiotherapy Clinical Scenario (e.g., patient with winged scapula or foot drop). Return ONLY JSON: {{'question','options','answer','explanation','link'}}. Ensure options are clinical diagnoses or muscle tests."
    
    response = model.generate_content(prompt)
    return json.loads(clean_json_response(response.text))

def main():
    st.set_page_config(page_title="Achu's Anatomy Lab", page_icon="🧬", layout="centered")
    
    if "session" not in st.session_state:
        st.session_state.update({
            "session": "menu", "game_mode": None, "streak": 0, "total_score": 0,
            "current_data": None, "quiz_feedback": None, "topic": None
        })

    # --- CSS & HEADER ---
    bg_str = get_base64_of_bin_file(FRIENDS_BG)
    logo_str = get_base64_of_bin_file(LOGO_FILE)
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.88), rgba(0,0,0,0.88)), url('data:image/png;base64,{bg_str}');
            background-size: cover; background-position: center; background-attachment: fixed;
        }}
        .header-container {{ display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; }}
        .logo-video {{ width: 100%; max-width: 180px; height: auto; }}
        .main-title {{ color: white; font-size: 28px; font-weight: bold; text-align: center; }}
        .game-card {{ background: rgba(0, 0, 0, 0.9); padding: 20px; border-radius: 15px; border: 1px solid #00d4ff; color: white; }}
        .stButton>button {{ border-radius: 10px; font-weight: bold; width: 100%; background: linear-gradient(135deg, #005f73 0%, #0a9396 100%); color: white !important; height: 3.5em; border: none; }}
        .achievement-tag {{ background: #ffd700; color: black; padding: 5px; border-radius: 5px; font-weight: bold; text-align: center; margin-bottom: 10px; }}
        </style>
        
        <div class="header-container">
            <video class="logo-video" autoplay loop muted playsinline><source src="data:video/webm;base64,{logo_str}" type="video/webm"></video>
            <h1 class="main-title">Achu's Anatomy & Physio Lab</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- MENU ---
    if st.session_state.session == "menu":
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.write("### Select Your Specialization:")
        mode = st.radio("Choose Game Mode:", ["General BD Chaurasia Quiz", "Physiotherapist Scenario Player"], index=0)
        topic = st.selectbox("Select System:", ["Upper Limb", "Lower Limb", "Thorax", "Head & Neck", "Neuroanatomy"])
        
        if st.button("Start Session"):
            st.session_state.game_mode = "general" if "General" in mode else "physio"
            st.session_state.topic = topic
            st.session_state.session = "quiz"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- QUIZ / SCENARIO SESSION ---
    elif st.session_state.session == "quiz":
        st.markdown(f"<div style='text-align:center; color:#00d4ff;'><strong>Mode: {'General' if st.session_state.game_mode == 'general' else 'Clinical Physio'}</strong></div>", unsafe_allow_html=True)
        st.progress(min(st.session_state.streak / 10, 1.0))
        st.write(f"🔥 Streak: {st.session_state.streak} | 🏆 Score: {st.session_state.total_score}")

        if st.session_state.current_data is None and st.session_state.quiz_feedback is None:
            st.session_state.current_data = get_anatomy_data(st.session_state.game_mode, st.session_state.topic, st.session_state.streak)

        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        
        if st.session_state.quiz_feedback is None:
            data = st.session_state.current_data
            st.write(f"#### {st.session_state.topic} Challenge")
            st.write(f"**{data['question']}**")

            ans = st.radio("Diagnostic Choice:", data['options'], index=None, key=f"q_{st.session_state.streak}")
            
            if st.button("Confirm Diagnosis"):
                if ans == data['answer']:
                    st.session_state.streak += 1
                    st.session_state.total_score += 15
                    st.session_state.quiz_feedback = ("success", "✅ Excellent Clinical Reasoning!", get_manglish_comment(True), data['explanation'], data['link'])
                else:
                    st.session_state.streak = 0
                    st.session_
