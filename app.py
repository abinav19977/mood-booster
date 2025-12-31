import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import random
import io

# --- CONFIG ---
PAGE_LOGO = "535a00a0-0968-491d-92db-30c32ced7ac6.webp" 
SPELL_BEE_WORDS = ["Enthusiastic", "Serendipity", "Magnanimous", "Quintessential", "Pharaoh", "Onomatopoeia", "Bourgeois", "Mischievous"]

# Hardcoded reliable links to avoid "Video Unavailable" errors
MALAYALAM_LINKS = [
    "https://www.youtube.com/watch?v=9two30yb62Q", # Pulival Kalyanam
    "https://www.youtube.com/watch?v=h3ka9dCpN0I", # Jagathy Comedy
    "https://www.youtube.com/watch?v=yS3F3gq_0zM"  # Salim Kumar
]
FRIENDS_LINKS = [
    "https://www.youtube.com/watch?v=xT5zt93BbAg", # Chandler Sarcasm
    "https://www.youtube.com/watch?v=JZ0AGtN_Uao", # Chandler & Joey
    "https://www.youtube.com/watch?v=ojTdYiBRtdU"  # Simple Joey
]

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing API Key! Please add it to Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def main():
    image_exists = os.path.exists(PAGE_LOGO)
    st.set_page_config(page_title="Achumol is...", page_icon=PAGE_LOGO if image_exists else "🐘")
    
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .big-title { font-size: 50px !important; font-weight: 700; color: #FF4B4B; margin: 0; line-height: 1.2; }
        .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
        .watch-btn {
            background-color: #FF4B4B; color: white; padding: 12px 24px; text-align: center;
            text-decoration: none; display: block; font-size: 16px; font-weight: bold;
            border-radius: 10px; margin-top: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    # --- BRAND HEADER ---
    head_col1, head_col2 = st.columns([1, 4])
    with head_col1:
        if image_exists: st.image(PAGE_LOGO, width=90)
    with head_col2:
        st.markdown('<p class="big-title">Achumol is...</p>', unsafe_allow_html=True)

    # State initialization
    for key in ["mood", "note", "show_choices", "final_res", "play_spell_bee", "current_word"]:
        if key not in st.session_state: st.session_state[key] = None

    # --- 1. MOOD SELECTION ---
    st.write("Endhaappa mood?")
    cols = st.columns(4)
    moods, icons = ["Happy", "Neutral", "Sad", "Angry"], ["😃", "😐", "😢", "😡"]
    
    for i, col in enumerate(cols):
        if col.button(f"{icons[i]} {moods[i]}", key=f"mood_{i}"):
            st.session_state.mood = moods[i]
            st.session_state.note, st.session_state.final_res = None, None
            st.session_state.show_choices, st.session_state.play_spell_bee = False, False

    if st.session_state.mood:
        st.divider()
        user_text = st.text_area("Endhelum vishesham parayanundo?", placeholder="Para...") 
        if st.button("🚀 Paraa"):
            with st.spinner(""):
                prompt = f"""
                Act as a Mallu partner. Mood: {st.session_state.mood}, Detail: {user_text}.
                Tone: Grounded Malayali conversation. 60% funny, 30% teasing, 10% warm. 
                STRICT: No 'honey/dear/love'. Use 'Edo/Nee'. Keep it natural, NOT cringe. 
                Mix Manglish & English naturally. Max 250 words.
                """
                res = model.generate_content(prompt)
                st.session_state.note = res.text

    # --- 2. NOTE ---
    if st.session_state.note:
        st.success("💌 **Message:**")
        st.write(st.session_state.note)
        
        if not st.session_state.show_choices and not st.session_state.play_spell_bee:
            st.write("Oru scene kandaalo mood boost cheyyaan?")
            y, n = st.columns(2)
            if y.button("✅ Pinne enna!"):
                st.session_state.show_choices = True
                st.rerun()
            if n.button("❌ Venda"):
                st.session_state.play_spell_bee = True
                st.rerun()

    # --- 3. SPELL BEE ---
    if st.session_state.play_spell_bee:
        st.divider()
        st.subheader("🐝 Spell Bee Game")
        if not st.session_state.current_word: st.session_state.current_word = random.choice(SPELL_BEE_WORDS)
        tts = gTTS(text=st.session_state.current_word, lang='en')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        st.audio(audio_fp, format='audio/mp3')
        guess = st.text_input("Type it here:", key="spell_input").strip()
        if st.button("Check"):
            if guess.lower() == st.session_state.current_word.lower():
                st.balloons()
                st.success("Nalla brilliance! Correct aanu. 😎")
            else:
                st.error("Thetti! Itra paranjittum manassilaayille? 😉")

    # --- 4. VIDEO CHOICE ---
    if st.session_state.show_choices and not st.session_state.final_res:
        st.divider()
        st.write("Select vibe:")
        c1, c2 = st.columns(2)
        v_type = None
        if c1.button("🍿 Malayalam"): v_type = "MALAYALAM"
        if c2.button("☕ Friends"): v_type = "FRIENDS"
        
        if v_type:
            with st.spinner(""):
                url = random.choice(MALAYALAM_LINKS if v_type == "MALAYALAM" else FRIENDS_LINKS)
                lang = "Malayalam script" if v_type == "MALAYALAM" else "English"
                p = f"Write exactly 2 lines of teasing banter in {lang} about watching {v_type}. No intro/labels."
                banter = model.generate_content(p).text
                st.session_state.final_res = f"{banter}||{url}"
                st.rerun()

    if st.session_state.final_res:
        parts = st.session_state.final_res.split("||")
        if len(parts) >= 2:
            st.divider()
            st.write(parts[0].strip())
            st.markdown(f'<a href="{parts[1].strip()}" target="_blank" class="watch-btn">📺 Watch on YouTube</a>', unsafe_allow_html=True)

    if st.session_state.note:
        st.write("---")
        if st.button("🔄 Reset"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
