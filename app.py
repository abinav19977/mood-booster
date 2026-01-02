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
    comments = ["Kidiloski! Nee puliyaanu kutto. 🔥", "Enna oru buddhi! Achu mass!", "Correct aanu! Pinne alla!"] if is_correct else \
               ["Ente ponno... poya buddhi pullu kootil! 😂", "Kashtam! Ithu ethu lokathu nina?", "Oru logicum illallo mwole!"]
    return random.choice(comments)

# --- AI PERSONA ENGINE ---
def get_scenario_response(scenario):
    prompt = f"""
    Dilemma: '{scenario}'. 
    Generate a roundtable discussion:
    - Chandler: Uses extreme sarcasm ("Could I BE any more...").
    - Joey: Mentions sandwiches, pizza, or says 'How you doin?'.
    - Phoebe: Mentions a past life or a street-smart story.
    - Ross: 'Ross-a-trons' the situation by correcting grammar or a small detail.
    """
    return model.generate_content(prompt).text

def get_lost_episode(prompt_text):
    prompt = f"Write a short script for a lost FRIENDS episode titled '{prompt_text}'. Include scene descriptions and funny dialogue for the main cast."
    return model.generate_content(prompt).text

def get_ross_fact_check(fact):
    prompt = f"The user says: '{fact}'. Respond as Ross Geller. If they are wrong, correct them pedantically. If they are right, say 'Fine, but you forgot one minor detail...' and add an obscure fact."
    return model.generate_content(prompt).text

def main():
    st.set_page_config(page_title="Achu's Friends App", page_icon="☕", layout="centered")
    
    if "session" not in st.session_state:
        st.session_state.update({"session": "menu", "streak": 0, "max_streak": 0, "current_data": None})

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
        </style>
        <div class="header-container">
            <img src="data:image/png;base64,{logo_str}" class="logo-img">
            <h1 class="main-title">Achu's Friends App</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- NAVIGATION ---
    if st.session_state.session == "menu":
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.write("### Choose Your Session, Achumol!")
        if st.button("🏆 Series Trivia Quiz"):
            st.session_state.session = "quiz"
            st.rerun()
        if st.button("🎭 Scenario Planner & Persona Engine"):
            st.session_state.session = "scenario"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- QUIZ SESSION ---
    elif st.session_state.session == "quiz":
        st.info(f"🔥 Streak: {st.session_state.streak} | 🏆 Best: {st.session_state.max_streak}")
        if st.session_state.current_data is None:
            prompt = "Generate a FRIENDS MCQ. Return ONLY JSON: {'question','options','answer','hint'}."
            st.session_state.current_data = json.loads(clean_json_response(model.generate_content(prompt).text))
        
        data = st.session_state.current_data
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.write(f"**Question:** {data['question']}")
        ans = st.radio("Pick one:", data['options'], index=None, key=f"q_{st.session_state.streak}")
        if st.button("Submit"):
            if ans == data['answer']:
                st.session_state.streak += 1
                st.success("Correct! " + get_manglish_comment(True))
            else:
                st.session_state.streak = 0
                st.error(f"Wrong! {get_manglish_comment(False)} It was {data['answer']}")
            st.session_state.current_data = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("🏠 Menu"): st.session_state.session = "menu"; st.rerun()

    # --- SCENARIO PLANNER & PERSONA ENGINE ---
    elif st.session_state.session == "scenario":
        tab1, tab2, tab3 = st.tabs(["🥪 Advice Column", "🎬 Lost Episodes", "🦖 Ross-a-Tron"])
        
        with tab1:
            st.markdown("<div class='game-card'>", unsafe_allow_html=True)
            dilemma = st.text_input("Tell the gang your problem:")
            if st.button("Get Advice"):
                st.write(get_scenario_response(dilemma))
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='game-card'>", unsafe_allow_html=True)
            idea = st.text_input("The One Where...", placeholder="Ross joins a heavy metal band")
            if st.button("Generate Script"):
                st.write(get_lost_episode(idea))
            st.markdown("</div>", unsafe_allow_html=True)

        with tab3:
            st.markdown("<div class='game-card'>", unsafe_allow_html=True)
            fact = st.text_input("State a Friends fact to Ross:")
            if st.button("Check Fact"):
                st.write(get_ross_fact_check(fact))
            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🏠 Menu"): st.session_state.session = "menu"; st.rerun()

if __name__ == "__main__":
    main()
