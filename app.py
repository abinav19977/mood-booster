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
            return base64.b64encode(open(bin_file, 'rb').read()).decode()
    except: return ""
    return ""

def clean_json_response(text):
    return text.replace("```json", "").replace("```", "").strip()

def get_manglish_comment(is_correct):
    comments = ["Kidiloski! Physio puliyaanu kutto. 🔥", "Enna oru clinic sense! Achu mass!", "Correct aanu! Pinne alla!"] if is_correct else \
               ["Ente ponno... poya buddhi BD Chaurasia-il illa! 😂", "Kashtam! Ithu ethu nerve aanu mwole?", "Sathyam para, thookam varunundo?"]
    return random.choice(comments)

# --- AI GENERATION ---
def get_anatomy_data(mode, topic, difficulty):
    if mode == "general":
        prompt = f"Topic: {topic}. Difficulty: {difficulty}. Generate a BD Chaurasia style MCQ. Return ONLY JSON: {{'question','options','answer','explanation','link','hint'}}."
    else:
        prompt = f"Topic: {topic}. Difficulty: {difficulty}. Generate a Physiotherapy Clinical Scenario (patient case). Return ONLY JSON: {{'question','options','answer','explanation','link','hint'}}."
    
    response = model.generate_content(prompt)
    return json.loads(clean_json_response(response.text))

def ask_patient_ai(question, context):
    prompt = f"The patient scenario is: {context}. The user (doctor) asks: '{question}'. Respond as the patient based on BD Chaurasia anatomy facts. Keep it brief."
    return model.generate_content(prompt).text

def main():
    st.set_page_config(page_title="Achu's Anatomy Lab", page_icon="🧬", layout="centered")
    
    if "session" not in st.session_state:
        st.session_state.update({
            "session": "menu", "game_mode": None, "difficulty": "Medium", 
            "streak": 0, "total_score": 0, "current_data": None, 
            "quiz_feedback": None, "topic": None, "next_hint_at": 0, 
            "show_hint": False, "patient_chat": []
        })

    # --- CSS & HEADER ---
    bg_str = get_base64_of_bin_file(FRIENDS_BG)
    logo_str = get_base64_of_bin_file(LOGO_FILE)
    st.markdown(f"""
        <style>
        .stApp {{ background-image: linear-gradient(rgba(0,0,0,0.88), rgba(0,0,0,0.88)), url('data:image/png;base64,{bg_str}'); background-size: cover; background-attachment: fixed; }}
        .header-container {{ display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; }}
        .logo-video {{ width: 100%; max-width: 250px; height: auto; }}
        .game-card {{ background: rgba(0, 0, 0, 0.9); padding: 20px; border-radius: 15px; border: 1px solid #00d4ff; color: white; }}
        .stButton>button {{ border-radius: 10px; font-weight: bold; width: 100%; background: linear-gradient(135deg, #005f73 0%, #0a9396 100%); color: white !important; height: 3.5em; border: none; }}
        .chat-bubble {{ background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; margin: 5px 0; border-left: 3px solid #00d4ff; }}
        </style>
        <div class="header-container">
            <video class="logo-video" autoplay muted loop playsinline src="data:video/webm;base64,{logo_str}"></video>
            <h1 style="color:white; text-align:center;">Achu's Anatomy & Physio Lab</h1>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.session == "menu":
        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        st.write("### ⚙️ Setup Your Session:")
        
        mode = st.radio("Choose Mode:", ["General BD Chaurasia Quiz", "Physiotherapist Scenario Player"], index=0)
        topic = st.selectbox("Select Topic:", ["Upper Limb", "Lower Limb", "Thorax", "Head & Neck", "Neuroanatomy"])
        diff = st.select_slider("Select Difficulty:", options=["Easy", "Medium", "Hard"], value="Medium")
        
        if st.button("Start Session"):
            st.session_state.update({
                "game_mode": "general" if "General" in mode else "physio", 
                "topic": topic, 
                "difficulty": diff,
                "session": "quiz", 
                "patient_chat": []
            })
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.session == "quiz":
        st.info(f"📍 {st.session_state.difficulty} Mode | 🔥 Streak: {st.session_state.streak} | 🏆 Score: {st.session_state.total_score}")

        if st.session_state.current_data is None and st.session_state.quiz_feedback is None:
            st.session_state.current_data = get_anatomy_data(st.session_state.game_mode, st.session_state.topic, st.session_state.difficulty)
            st.session_state.show_hint = False

        st.markdown("<div class='game-card'>", unsafe_allow_html=True)
        if st.session_state.quiz_feedback is None:
            data = st.session_state.current_data
            st.write(f"#### {st.session_state.topic} Challenge")
            st.write(f"**Scenario:** {data['question']}")

            if st.session_state.game_mode == "physio":
                st.write("---")
                st.write("🩺 **Diagnostic Consultation:**")
                for chat in st.session_state.patient_chat:
                    st.markdown(f"<div class='chat-bubble'><b>{chat['role']}:</b> {chat['text']}</div>", unsafe_allow_html=True)
                
                col_q, col_b = st.columns([3, 1])
                with col_q: q_to_patient = st.text_input("Ask the patient a question:", key="q_input")
                with col_b: 
                    if st.button("Ask"):
                        if q_to_patient:
                            response = ask_patient_ai(q_to_patient, data['question'])
                            st.session_state.patient_chat.append({"role": "Dr. Achu", "text": q_to_patient})
                            st.session_state.patient_chat.append({"role": "Patient", "text": response})
                            st.rerun()
                st.write("---")

            if st.session_state.streak >= st.session_state.next_hint_at:
                if st.button("💡 Hint"): 
                    st.session_state.show_hint = True
                    st.session_state.next_hint_at = st.session_state.streak + 5
            if st.session_state.show_hint: st.warning(f"Hint: {data['hint']}")

            ans = st.radio("Select Diagnosis:", data['options'], index=None, key=f"q_{st.session_state.streak}")
            if st.button("Submit Final Diagnosis"):
                if ans == data['answer']:
                    score_gain = {"Easy": 10, "Medium": 15, "Hard": 25}[st.session_state.difficulty]
                    st.session_state.streak += 1
                    st.session_state.total_score += score_gain
                    st.session_state.quiz_feedback = ("success", f"✅ Correct! (+{score_gain})", get_manglish_comment(True), data['explanation'], data['link'])
                else:
                    st.session_state.streak = 0
                    st.session_state.quiz_feedback = ("error", f"❌ Misdiagnosis! Correct: {data['answer']}", get_manglish_comment(False), data['explanation'], data['link'])
                st.rerun()
        else:
            type, msg, comment, logic, link = st.session_state.quiz_feedback
            st.success(msg) if type == "success" else st.error(msg)
            st.markdown(f"<p style='color:gold; text-align:center;'><i>{comment}</i></p>", unsafe_allow_html=True)
            st.write(f"**Anatomical Logic:** {logic}")
            st.markdown(f"🔗 [Further Reading]({link})")
            if st.button("Next Case"):
                st.session_state.update({"quiz_feedback": None, "current_data": None, "patient_chat": []})
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("🏠 Menu"): st.session_state.session = "menu"; st.rerun()

if __name__ == "__main__": main()
