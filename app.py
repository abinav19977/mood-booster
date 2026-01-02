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
    # Using 2.0 Flash for fast persona responses
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
    comments = ["Kidiloski! Nee puliyaanu kutto. 🔥", "Enna oru buddhi! Achu mass!", "Correct aanu! Pinne alla!"] if is_correct else \
               ["Ente ponno... poya buddhi pullu kootil! 😂", "Kashtam! Ithu ethu lokathu nina?", "Oru logicum illallo mwole!"]
    return random.choice(comments)

# --- AI LOGIC ---
def get_dynamic_friends_q(streak):
    prompt = f"Generate a unique MCQ about FRIENDS (Difficulty level based on streak: {streak}). Return ONLY a JSON object with keys: 'question', 'options' (list of 4), 'answer', 'hint'."
    response = model.generate_content(prompt)
    return json.loads(clean_json_response(response.text))

def get_scenario_response(scenario):
    prompt = f"""
    A user has this dilemma: '{scenario}'. 
    Provide a roundtable discussion where:
    - Chandler uses heavy sarcasm.
    - Joey relates it to food or says 'How you doin?'.
    - Phoebe mentions a past life or something whimsical.
    - Ross 'Ross-a-trons' the logic or facts.
    Keep it conversational and short.
    """
    response = model.generate_content(prompt)
    return response.text

def main():
    st.set_page_config(page_title="Achu's Friends App", page_icon="☕", layout="centered")
    
    if "session" not in st.session_state:
        st.session_state.update({
            "session": "menu", "streak": 0, "max_streak": 0, 
            "current_data": None, "feedback_msg": None, "comment": None
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
        .header-container {{ display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 20px; }}
        .logo-img {{ width: 50px; height: 50px; border-radius: 50%; border: 2px solid gold; }}
        .main-title {{ color: white; font-size: 28px; font-weight: bold; margin: 0; }}
        .game-card {{ background: rgba(0, 0, 0, 0.85); padding: 20px; border-radius: 15px; border: 1px solid #444; color: white; margin-bottom: 10px; }}
        .stButton>button {{ border-radius: 10px; font-weight: bold; width: 100%; background: linear-gradient(135deg, #6b2d5c 0%, #f0a202 100%); color: white !important; height: 3.5em; border: none; }}
        .comment-text {{ color: #ffeb3b; font-style: italic; text-align: center; }}
        </style>
        <div class="header-container">
            <img src="data:image/png;base64,{logo_str}" class="logo-img">
            <h1 class="main-title">Achu's Friends App</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- MENU SESSION ---
    if st.session_state.session == "menu":
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.write("### Welcome, Achu! Choose your session:")
        if st.button("🏆 Start Friends Quiz"):
            st.session_state.session = "quiz"
            st.rerun()
        if st.button("🎭 Scenario Planner (The Roundtable)"):
            st.session_state.session = "scenario"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- QUIZ SESSION ---
    elif st.session_state.session == "quiz":
        st.info(f"🔥 Streak: {st.session_state.streak} | 🏆 Best: {st.session_state.max_streak}")
        
        if st.session_state.current_data is None:
            st.session_state.current_data = get_dynamic_friends_q(st.session_state.streak)

        data = st.session_state.current_data
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.write(f"**Question:** {data['question']}")
        ans = st.radio("Choose:", data['options'], index=None, key=f"q_{st.session_state.streak}")
        
        if st.button("Submit"):
            if ans == data['answer']:
                st.session_state.streak += 1
                st.session_state.max_streak = max(st.session_state.streak, st.session_state.max_streak)
                st.session_state.feedback_msg = ("success", "Correct!")
                st.session_state.comment = get_manglish_comment(True)
            else:
                st.session_state.streak = 0
                st.session_state.feedback_msg = ("error", f"Wrong! Correct: {data['answer']}")
                st.session_state.comment = get_manglish_comment(False)
            st.session_state.current_data = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.feedback_msg:
            t, m = st.session_state.feedback_msg
            st.success(m) if t == "success" else st.error(m)
            st.markdown(f"<p class='comment-text'>\"{st.session_state.comment}\"</p>", unsafe_allow_html=True)
        
        if st.button("🏠 Back to Menu"):
            st.session_state.session = "menu"
            st.rerun()

    # --- SCENARIO PLANNER SESSION ---
    elif st.session_state.session == "scenario":
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.write("### 🥪 The 'What Should I Do?' Column")
        st.write("Upload your dilemma and let the gang debate it.")
        user_scenario = st.text_area("Example: I accidentally ate my roommate's sandwich...", placeholder="Type your problem here...")
        
        if st.button("Let the Gang Debate!"):
            if user_scenario:
                with st.spinner("Chandler is writing sarcasm..."):
                    response = get_scenario_response(user_scenario)
                    st.session_state.scenario_result = response
            else:
                st.warning("Para mwole, what happened?")
        
        if "scenario_result" in st.session_state:
            st.write("---")
            st.markdown(st.session_state.scenario_result)
            st.info("Ross: 'Actually, it's not a dilemma, it's a social transgression!'")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("🏠 Back to Menu"):
            if "scenario_result" in st.session_state: del st.session_state.scenario_result
            st.session_state.session = "menu"
            st.rerun()

if __name__ == "__main__":
    main()
