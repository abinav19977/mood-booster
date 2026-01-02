import streamlit as st
import google.generativeai as genai
import random
import json
import base64
import os

# --- CONFIG ---
# Using the filename from your uploaded files
FRIENDS_BG = "images (2).jpg" 
VICTORY_SOUND = "https://www.myinstants.com/media/sounds/crowd-cheer.mp3"

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
    except:
        return ""
    return ""

def clean_json_response(text):
    text = text.replace("```json", "").replace("```", "").strip()
    return text

def get_manglish_comment(is_correct):
    """Generates a funny Manglish praise or troll."""
    if is_correct:
        comments = [
            "Kidiloski! Nee puliyaanu kutto. 🔥", 
            "Enna oru buddhi! Achu mass aanu!", 
            "Correct aanu! Pinne alla!",
            "Sambaar alla, ithu vere level logic!"
        ]
    else:
        comments = [
            "Ente ponno... poya buddhi pullu kootil! 😂", 
            "Kashtam! Ithu ethu lokathu nina?", 
            "Sathyam para, thookam varunundo?",
            "Oru logicum illallo mwole!"
        ]
    return random.choice(comments)

def get_dynamic_friends_q(streak):
    difficulty = "Easy" if streak < 4 else "Intermediate" if streak < 8 else "Very Hard"
    prompt = f"Generate a unique {difficulty} difficulty MCQ about the TV show FRIENDS. Return ONLY a JSON object with keys: 'question', 'options' (list of 4), 'answer', 'hint'. No markdown."
    response = model.generate_content(prompt)
    return json.loads(clean_json_response(response.text))

def main():
    st.set_page_config(page_title="Achus Friends Quiz", page_icon="☕", layout="centered")
    
    if "streak" not in st.session_state:
        st.session_state.update({
            "streak": 0, "max_streak": 0, "current_data": None, 
            "feedback_msg": None, "comment": None
        })

    # --- MOBILE COMPATIBLE BACKGROUND STYLING ---
    bin_str = get_base64_of_bin_file(FRIENDS_BG)
    bg_css = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url('data:image/png;base64,{bin_str}');
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        
        /* Ensure card fits phone screens well */
        .game-card {{
            background: rgba(0, 0, 0, 0.85); 
            padding: 20px; 
            border-radius: 15px; 
            border: 1px solid #444; 
            color: white;
            margin-top: 10px;
        }}

        .stButton>button {{
            border-radius: 10px;
            font-weight: bold;
            width: 100%;
            height: 3.5em;
            background: linear-gradient(135deg, #6b2d5c 0%, #f0a202 100%);
            color: white !important;
            border: none;
        }}
        
        .comment-text {{
            color: #ffeb3b; 
            font-style: italic; 
            font-size: 1.2em; 
            text-align: center;
            margin-top: 15px;
        }}
        </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: white;'>☕ Achus Friends Quiz</h1>", unsafe_allow_html=True)

    # Display Stats
    st.markdown(f"""
        <div style='display: flex; justify-content: space-around; background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; color: gold; font-weight: bold; margin-bottom: 10px;'>
            <span>🔥 Streak: {st.session_state.streak}</span>
            <span>🏆 Best: {st.session_state.max_streak}</span>
        </div>
    """, unsafe_allow_html=True)

    # --- GAME LOGIC ---
    if st.session_state.current_data is None:
        with st.spinner("Fetching new question..."):
            st.session_state.current_data = get_dynamic_friends_q(st.session_state.streak)

    data = st.session_state.current_data

    st.markdown("<div class='game-card'>", unsafe_allow_html=True)
    st.write(f"### {data['question']}")
    
    # Use key based on streak to reset radio buttons automatically
    ans = st.radio("Pick the correct answer:", data['options'], index=None, key=f"q_{st.session_state.streak}")
    
    if st.button("Submit Answer"):
        if ans is None:
            st.warning("Please select an option first!")
        else:
            if ans == data['answer']:
                st.session_state.streak += 1
                st.session_state.max_streak = max(st.session_state.streak, st.session_state.max_streak)
                st.session_state.feedback_msg = ("success", "✅ Correct! You're a true fan.")
                st.session_state.comment = get_manglish_comment(True)
            else:
                st.session_state.streak = 0
                st.session_state.feedback_msg = ("error", f"❌ Wrong! Correct answer: {data['answer']}")
                st.session_state.comment = get_manglish_comment(False)
            
            st.session_state.current_data = None # This triggers a new question on rerun
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Show Feedback
    if st.session_state.feedback_msg:
        msg_type, msg_text = st.session_state.feedback_msg
        if msg_type == "success":
            st.success(msg_text)
        else:
            st.error(msg_text)
        st.markdown(f"<p class='comment-text'>{st.session_state.comment}</p>", unsafe_allow_html=True)

    # Celebrate milestones
    if st.session_state.streak > 0 and st.session_state.streak % 5 == 0:
        st.balloons()

if __name__ == "__main__":
    main()
