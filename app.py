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
        comments = ["Kidiloski! Nee puliyaanu kutto. 🔥", "Enna oru buddhi! Achu mass!", "Correct aanu! Pinne alla!"]
    else:
        comments = ["Ente ponno... poya buddhi pullu kootil! 😂", "Kashtam! Ithu ethu lokathu nina?", "Oru logicum illallo mwole!"]
    return random.choice(comments)

# --- AI PERSONA ENGINE ---
def get_scenario_response(scenario):
    # Prompt logic to detect and mirror language style
    prompt = f"""
    The user has a dilemma: '{scenario}'. 
    Generate a roundtable discussion with:
    1. Chandler (Sarcastic)
    2. Joey (Food-obsessed/How you doin)
    3. Phoebe (Whimsical/Past lives)
    4. Ross (Pedantic/Correcting)

    CRITICAL INSTRUCTION: If the user's dilemma is written in Manglish (Malayalam written in English script), ALL characters MUST respond in Manglish. If it is in English, they respond in English.
    """
    return model.generate_content(prompt).text

def main():
    st.set_page_config(page_title="Achu's Friends App", page_icon="☕", layout="centered")
    
    if "session" not in st.session_state:
        st.session_state.update({
            "session": "menu", "streak": 0, "max_streak": 0, 
            "current_data": None, "quiz_feedback": None
        })

    # --- CSS STYLING ---
    bg_str = get_base64_of_bin_file(FRIENDS_BG)
    logo_str = get_base64_of_bin_file(LOGO_FILE)
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url('data:image/png;base64,{bg_str}');
            background-size: cover; background-position: center; background-attachment: fixed;
        }}
        .header-container {{ display: flex; flex-direction: column; align-items: center; gap: 10px; margin-bottom: 20px; }}
        .logo-img {{ width: 180px; }}
        .main-title {{ color: white; font-size: 32px; font-weight: bold; text-align: center; }}
        .game-card {{ background: rgba(0, 0, 0, 0.85); padding: 20px; border-radius: 15px; border: 1px solid #444; color: white; margin-bottom: 10px; }}
        .stButton>button {{ border-radius: 10px; font-weight: bold; width: 100%; background: linear-gradient(135deg, #6b2d5c 0%, #f0a202 100%); color: white !important; height: 3.5em; border: none; }}
        .comment-box {{ color: #ffeb3b; font-style: italic; font-size: 1.2em; text-align: center; margin-top: 10px; }}
        </style>
        
        <div class="header-container">
            <img src="data:image/png;base64,{logo_str}" class="logo-img">
            <h1 class="main-title">Achu's Friends App</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- MENU ---
    if st.session_state.session == "menu":
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        if st.button("🏆 Start Friends Quiz"):
            st.session_state.session = "quiz"
            st.rerun()
        if st.button("🎭 Scenario Planner"):
            st.session_state.session = "scenario"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- QUIZ SESSION ---
    elif st.session_state.session == "quiz":
        st.info(f"🔥 Streak: {st.session_state.streak} | 🏆 Best: {st.session_state.max_streak}")
        
        if st.session_state.current_data is None and st.session_state.quiz_feedback is None:
            with st.spinner("Fetching question..."):
                prompt = "Generate a FRIENDS MCQ. Return ONLY JSON: {'question','options','answer','hint'}."
                response = model.generate_content(prompt)
                st.session_state.current_data = json.loads(clean_json_response(response.text))

        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        
        if st.session_state.quiz_feedback is None:
            data = st.session_state.current_data
            st.write(f"### {data['question']}")
            ans = st.radio("Choose:", data['options'], index=None, key=f"q_{st.session_state.streak}")
            
            if st.button("Submit Answer"):
                if ans == data['answer']:
                    st.session_state.streak += 1
                    st.session_state.max_streak = max(st.session_state.streak, st.session_state.max_streak)
                    st.session_state.quiz_feedback = ("success", "✅ Correct!", get_manglish_comment(True))
                else:
                    st.session_state.streak = 0
                    st.session_state.quiz_feedback = ("error", f"❌ Wrong! It was {data['answer']}", get_manglish_comment(False))
                st.rerun()
        else:
            type, msg, comment = st.session_state.quiz_feedback
            if type == "success": st.success(msg)
            else: st.error(msg)
            st.markdown(f"<p class='comment-box'>\"{comment}\"</p>", unsafe_allow_html=True)
            
            if st.button("➡️ Next Question"):
                st.session_state.quiz_feedback = None
                st.session_state.current_data = None
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("🏠 Home Menu"): st.session_state.session = "menu"; st.rerun()

    # --- SCENARIO PLANNER ---
    elif st.session_state.session == "scenario":
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.write("### 🥪 The Roundtable")
        st.caption("If you type in Manglish, the gang will reply in Manglish!")
        scenario = st.text_area("What's the dilemma?", placeholder="Type here (e.g., 'Ente roommate ente sandwich thinu...')")
        
        if st.button("Ask the Gang"):
            if scenario:
                with st.spinner("Characters are thinking..."):
                    st.write(get_scenario_response(scenario))
            else:
                st.warning("Please type something first!")
                
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("🏠 Home Menu"): st.session_state.session = "menu"; st.rerun()

if __name__ == "__main__":
    main()
