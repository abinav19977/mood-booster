import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import random
import io
import os

# --- CONFIG ---
PAGE_LOGO = "535a00a0-0968-491d-92db-30c32ced7ac6.webp" 

# --- DATA ---
FRIENDS_LEVELS = {
    "intermediate": [
        {"q": "What is the name of Joey's penguin?", "o": ["Hugsy", "Waddle", "Pingu", "Snowy"], "a": "Hugsy", "h": "It's a bedtime pal."},
        {"q": "How many sisters does Joey have?", "o": ["5", "6", "7", "8"], "a": "7", "h": "It's a lucky number for some."},
        {"q": "What was the name of Ross's monkey?", "o": ["Marcel", "George", "Abu", "Kong"], "a": "Marcel", "h": "Starts with M."},
    ],
    "hard": [
        {"q": "What is Chandler's middle name?", "o": ["Muriel", "Francis", "Eustace", "Bing"], "a": "Muriel", "h": "It's quite an old-fashioned female name."},
        {"q": "What is the name of the 'Geller Cup' trophy?", "o": ["A Troll", "A Doll", "A Monkey", "A Soda Can"], "a": "A Troll", "h": "It's nailed to a 2x4."},
        {"q": "What was the name of Rachel’s hairless cat?", "o": ["Mrs. Whiskerson", "Fluffy", "Baldy", "Minerva"], "a": "Mrs. Whiskerson", "h": "It sounds very formal."},
    ]
}

SPELL_BEE_DATA = [
    {"w": "Queue", "m": "A line of people waiting.", "l": "easy"},
    {"w": "Colonel", "m": "A high-ranking military officer.", "l": "medium"},
    {"w": "Occurrence", "m": "An event that happens.", "l": "hard"},
    {"w": "Diatribe", "m": "A forceful and bitter verbal attack.", "l": "hard"}
]

BADGES = {5: "🥉 Bronze Achu", 10: "🥈 Silver Achu", 15: "🥇 Gold Achu", 20: "💎 Diamond Queen"}

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("Missing API Key!")
    st.stop()

def main():
    image_exists = os.path.exists(PAGE_LOGO)
    st.set_page_config(page_title="Achus Game App", page_icon=PAGE_LOGO if image_exists else "🎮")
    
    st.markdown("""
        <style>
        .big-title { font-size: 45px !important; font-weight: 700; color: #FF4B4B; }
        .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
        .streak-box { padding: 10px; background: #333; color: gold; border-radius: 10px; text-align: center; font-size: 20px; }
        </style>
        """, unsafe_allow_html=True)

    # --- HEADER ---
    col1, col2 = st.columns([1, 4])
    with col1:
        if image_exists: st.image(PAGE_LOGO, width=100)
    with col2:
        st.markdown('<p class="big-title">Achus Game App</p>', unsafe_allow_html=True)

    # --- SESSION STATE ---
    states = {
        "game_mode": None, "streak": 0, "max_streak": 0, 
        "current_q": None, "hint_used": 0, "q_count": 0, "feedback": None
    }
    for k, v in states.items():
        if k not in st.session_state: st.session_state[k] = v

    if not st.session_state.game_mode:
        st.write("### What does Achumol want to play today?")
        c1, c2 = st.columns(2)
        if c1.button("☕ Friends Series Quiz"):
            st.session_state.game_mode = "friends"
            st.rerun()
        if c2.button("🐝 Spell Bee"):
            st.session_state.game_mode = "spellbee"
            st.rerun()
    else:
        # Display Streak
        st.markdown(f'<div class="streak-box">🔥 Current Streak: {st.session_state.streak} | 🏆 Max Streak: {st.session_state.max_streak}</div>', unsafe_allow_html=True)
        
        # --- FRIENDS QUIZ LOGIC ---
        if st.session_state.game_mode == "friends":
            if not st.session_state.current_q:
                level = "hard" if st.session_state.streak > 5 else "intermediate"
                st.session_state.current_q = random.choice(FRIENDS_LEVELS[level])
            
            q = st.session_state.current_q
            st.write(f"### Question {st.session_state.q_count + 1}:")
            st.write(f"**{q['q']}**")
            
            user_choice = st.radio("Choose one:", q['o'], index=None)
            
            # Hint logic
            if st.session_state.q_count % 5 == 0 and st.session_state.q_count != 0:
                if st.button("💡 Use Hint"):
                    st.info(f"Hint: {q['h']}")

            if st.button("Submit Answer"):
                if user_choice == q['a']:
                    st.session_state.streak += 1
                    st.session_state.q_count += 1
                    if st.session_state.streak > st.session_state.max_streak:
                        st.session_state.max_streak = st.session_state.streak
                    
                    p = f"Achumol got it right! Friends mood: Correct. Tone: 10% Romantic, 90% Friends appreciation. No cringe."
                    st.session_state.feedback = model.generate_content(p).text
                else:
                    st.session_state.streak = 0
                    p = f"Achumol got it wrong! Answer was {q['a']}. Tone: Sarcastic Friends troll. No cringe."
                    st.session_state.feedback = model.generate_content(p).text
                
                st.session_state.current_q = None
                st.rerun()

        # --- SPELL BEE LOGIC ---
        elif st.session_state.game_mode == "spellbee":
            if not st.session_state.current_word_obj:
                st.session_state.current_word_obj = random.choice(SPELL_BEE_DATA)
            
            word_obj = st.session_state.current_word_obj
            
            # Indian English Pronunciation
            tts = gTTS(text=word_obj['w'], lang='en', tld='co.in')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3')

            if st.toggle("Show Meaning"):
                st.caption(f"Meaning: {word_obj['m']}")

            guess = st.text_input("Enter Spelling:").strip()
            if st.button("Check"):
                if guess.lower() == word_obj['w'].lower():
                    st.session_state.streak += 1
                    if st.session_state.streak > st.session_state.max_streak:
                        st.session_state.max_streak = st.session_state.streak
                    st.session_state.feedback = "Correct! Achumol, you are a genius! 🌟"
                else:
                    st.session_state.streak = 0
                    st.session_state.feedback = f"Wrong! Spelling is {word_obj['w']}. Try harder, dummy! 😉"
                st.session_state.current_word_obj = None
                st.rerun()

        # --- FEEDBACK & BADGES ---
        if st.session_state.feedback:
            st.write("---")
            st.write(st.session_state.feedback)
            
            # Show Badge
            for score, badge in BADGES.items():
                if st.session_state.max_streak >= score:
                    st.toast(f"New Badge Unlocked: {badge}!")
                    st.success(f"🏅 Current Rank: {badge}")

        if st.button("Back to Menu"):
            st.session_state.game_mode = None
            st.rerun()

if __name__ == "__main__":
    if "current_word_obj" not in st.session_state: st.session_state.current_word_obj = None
    main()
