import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import random
import io

# --- CONFIG ---
PAGE_LOGO = "535a00a0-0968-491d-92db-30c32ced7ac6.webp" 
SPELL_BEE_WORDS = ["Enthusiastic", "Serendipity", "Magnanimous", "Quintessential", "Pharaoh", "Onomatopoeia", "Bourgeois", "Mischievous"]
NICKNAMES = ["Collector Achumol", "Spelling Rani", "Einstein Achu", "Budhirakshasi", "Achu-Panda", "Chakkara-Bee"]

MALAYALAM_LINKS = ["https://www.youtube.com/watch?v=9two30yb62Q", "https://www.youtube.com/watch?v=h3ka9dCpN0I", "https://www.youtube.com/watch?v=yS3F3gq_0zM"]
FRIENDS_LINKS = ["https://www.youtube.com/watch?v=xT5zt93BbAg", "https://www.youtube.com/watch?v=JZ0AGtN_Uao", "https://www.youtube.com/watch?v=ojTdYiBRtdU"]

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing API Key!")
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
        .nickname-box {
            padding: 15px; background-color: #fce4ec; border-radius: 10px; border: 2px solid #FF4B4B;
            text-align: center; font-size: 22px; font-weight: bold; color: #FF4B4B; margin: 15px 0;
        }
        </style>
        """, unsafe_allow_html=True)

    head_col1, head_col2 = st.columns([1, 4])
    with head_col1:
        if image_exists: st.image(PAGE_LOGO, width=90)
    with head_col2:
        st.markdown('<p class="big-title">Achumol is...</p>', unsafe_allow_html=True)

    for key in ["mood", "note", "show_choices", "final_res", "play_spell_bee", "current_word", "nickname", "nothing_needed"]:
        if key not in st.session_state: st.session_state[key] = None

    st.write("Enthokke ind Visesham?") 
    
    cols = st.columns(4)
    moods, icons = ["Happy", "Neutral", "Sad", "Angry"], ["😃", "😐", "😢", "😡"]
    
    for i, col in enumerate(cols):
        if col.button(f"{icons[i]} {moods[i]}", key=f"mood_{i}"):
            st.session_state.mood = moods[i]
            st.session_state.note, st.session_state.final_res, st.session_state.nickname = None, None, None
            st.session_state.show_choices, st.session_state.play_spell_bee = False, False
            st.session_state.nothing_needed = False

    if st.session_state.mood:
        st.divider()
        user_text = st.text_area("Enthenkilum extra parayan undo?", placeholder="Para...") 
        if st.button("🚀 Paraa"):
            with st.spinner("Writing..."):
                prompt = f"""
                Act as a Mallu partner. Mood: {st.session_state.mood}. Input context: {user_text}.
                
                STRICT LANGUAGE RULES:
                1. Dominantly English (85%).
                2. Use small parts in Manglish (15%) to keep it feeling like a real Malayali chat.
                3. Ensure there is at least one clear Manglish line (e.g., 'Chumma bore adichu irikkathe').
                
                TONE RULES:
                - 60% Funny, 30% Teasing, 10% Romantic.
                - Only the romantic part should be in pure English.
                - Max 200 words. Use 'Edo' or 'Nee'.
                - End the note by asking if they want a movie scene, a spell bee game, or nothing.
                - Do NOT mention personal details.
                """
                res = model.generate_content(prompt)
                st.session_state.note = res.text

    if st.session_state.note:
        st.success("💌 **Message:**")
        st.write(st.session_state.note)
        
        if not any([st.session_state.show_choices, st.session_state.play_spell_bee, st.session_state.nothing_needed]):
            st.write("Vibe select cheyyu:")
            opt1, opt2, opt3 = st.columns(3)
            if opt1.button("🎬 Movie Scene"):
                st.session_state.show_choices = True
                st.rerun()
            if opt2.button("🐝 Spell Bee"):
                st.session_state.play_spell_bee = True
                st.rerun()
            if opt3.button("💤 Ippam onnum venda"):
                st.session_state.nothing_needed = True
                st.rerun()

    # Option 1: Movie Scene Logic
    if st.session_state.show_choices and not st.session_state.final_res:
        st.divider()
        st.write("Innu enthu kanoonam?")
        c1, c2 = st.columns(2)
        v_type = None
        if c1.button("🍿 Malayalam"): v_type = "MALAYALAM"
        if c2.button("☕ Friends"): v_type = "FRIENDS"
        
        if v_type:
            with st.spinner("Finding..."):
                url = random.choice(MALAYALAM_LINKS if v_type == "MALAYALAM" else FRIENDS_LINKS)
                p = f"Write 2 lines of teasing banter about watching {v_type}. No labels."
                banter = model.generate_content(p).text
                st.session_state.final_res = f"{banter}||{url}"
                st.rerun()

    if st.session_state.final_res:
        parts = st.session_state.final_res.split("||")
        if len(parts) >= 2:
            st.divider()
            st.write(parts[0].strip())
            st.markdown(f'<a href="{parts[1].strip()}" target="_blank" class="watch-btn">📺 Watch on YouTube</a>', unsafe_allow_html=True)

    # Option 2: Spell Bee Logic
    if st.session_state.play_spell_bee:
        st.divider()
        st.subheader("🐝 Spell Bee Time!")
        if not st.session_state.current_word: st.session_state.current_word = random.choice(SPELL_BEE_WORDS)
        
        tts = gTTS(text=st.session_state.current_word, lang='en')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        st.audio(audio_fp, format='audio/mp3')
        
        guess = st.text_input("Spelling adichu kodu:", key="spell_input").strip()
        if st.button("Check"):
            if guess.lower() == st.session_state.current_word.lower():
                st.balloons()
                st.session_state.nickname = random.choice(NICKNAMES)
                st.success("Correct-aanu! Smart girl.")
                st.markdown(f'<div class="nickname-box">New Nickname: {st.session_state.nickname} 😎</div>', unsafe_allow_html=True)
                if st.button("Next Word"):
                    st.session_state.current_word = random.choice(SPELL_BEE_WORDS)
                    st.session_state.nickname = None
                    st.rerun()
            else:
                st.error("Thetti! Sarcastic teaser: Itra simple spelling polum ariyille? 😉")

    # Option 3: Nothing Needed Logic
    if st.session_state.nothing_needed:
        st.divider()
        st.info("Sari enna, pinne kaanaam! Take care. ❤️")

    if st.session_state.note:
        st.write("---")
        if st.button("🔄 Reset"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
