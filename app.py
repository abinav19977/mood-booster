import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import random
import io

# --- CONFIG ---
PAGE_LOGO = "535a00a0-0968-491d-92db-30c32ced7ac6.webp" 
SPELL_BEE_WORDS = ["Enthusiastic", "Serendipity", "Magnanimous", "Quintessential", "Pharaoh", "Onomatopoeia", "Bourgeois", "Mischievous"]

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
        </style>
        """, unsafe_allow_html=True)

    # --- BRAND HEADER ---
    head_col1, head_col2 = st.columns([1, 4])
    with head_col1:
        if image_exists: st.image(PAGE_LOGO, width=90)
    with head_col2:
        st.markdown('<p class="big-title">Achumol is...</p>', unsafe_allow_html=True)

    # Initialize session states
    if "mood" not in st.session_state: st.session_state.mood = None
    if "note" not in st.session_state: st.session_state.note = None
    if "show_choices" not in st.session_state: st.session_state.show_choices = False
    if "final_res" not in st.session_state: st.session_state.final_res = None
    if "play_spell_bee" not in st.session_state: st.session_state.play_spell_bee = False
    if "current_word" not in st.session_state: st.session_state.current_word = None

    # --- 1. MOOD SELECTION ---
    st.write("Edooo, Mood engane undu?")
    cols = st.columns(4)
    moods = ["Happy", "Neutral", "Sad", "Angry"]
    icons = ["😃", "😐", "😢", "😡"]
    
    for i, col in enumerate(cols):
        if col.button(f"{icons[i]} {moods[i]}", key=f"mood_{i}"):
            st.session_state.mood = moods[i]
            st.session_state.note = None
            st.session_state.show_choices = False
            st.session_state.final_res = None
            st.session_state.play_spell_bee = False

    if st.session_state.mood:
        st.divider()
        elab = st.toggle("Edooo, Kooduthal enthelum parayanundo?")
        user_text = st.text_area("Para...", placeholder="Enthelum vishesham undo?") if elab else ""

        if st.button("🚀 Paraa"):
            with st.spinner(""):
                prompt = f"Act as a Mallu boyfriend. Tone: 60% Funny, 10% Warm, 30% Teasing. Lang: 50% Manglish/English. Max 250 words. Mood: {st.session_state.mood}, Detail: {user_text}. Use 'Edooo/Nee'."
                res = model.generate_content(prompt)
                st.session_state.note = res.text

    # --- 2. THE NOTE & CHOICES ---
    if st.session_state.note:
        st.success("💌 **Message:**")
        st.write(st.session_state.note)
        
        if not st.session_state.show_choices and not st.session_state.play_spell_bee:
            st.write("Edooo, mood boost cheyyan oru scene suggest cheyyatte?")
            y, n = st.columns(2)
            if y.button("✅ Yes"):
                st.session_state.show_choices = True
                st.rerun()
            if n.button("❌ No"):
                st.session_state.play_spell_bee = True
                st.rerun()

    # --- 3. SPELL BEE GAME ---
    if st.session_state.play_spell_bee:
        st.divider()
        st.subheader("🐝 Spell Bee Time!")
        if not st.session_state.current_word: st.session_state.current_word = random.choice(SPELL_BEE_WORDS)

        tts = gTTS(text=st.session_state.current_word, lang='en')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        st.audio(audio_fp, format='audio/mp3')

        guess = st.text_input("Type the spelling here:", key="spell_input").strip()
        if st.button("Check Spelling"):
            if guess.lower() == st.session_state.current_word.lower():
                st.balloons()
                st.success("Good work! Achumol brilliance thanne! 😎")
            else:
                st.error("Try again! Spelling mistakes are your specialty! 😉")

    # --- 4. MOVIE CHOICE ---
    if st.session_state.show_choices and not st.session_state.final_res:
        st.divider()
        st.write("Pick your vibe:")
        c1, c2 = st.columns(2)
        sel = None 
        if c1.button("🍿 Malayalam"): sel = "Malayalam Movie Comedy"
        if c2.button("☕ Friends"): sel = "Friends Series Funny"
        
        if sel:
            with st.spinner("Finding video..."):
                sub_prompt = f"""
                Suggest a real YouTube video link for {sel}.
                FORMAT: [Banter] || [YouTube URL]
                RULES: 
                1. BANTER: Exactly 2 lines. 
                   - If Malayalam Movie: Use Malayalam script.
                   - If Friends: Use English.
                   - Tone: 60% Fun, 10% Romantic, 30% Teasing.
                2. URL: A direct YouTube URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID).
                3. DO NOT include any introductory text or labels.
                """
                res = model.generate_content(sub_prompt)
                st.session_state.final_res = res.text
                st.rerun()

    if st.session_state.final_res:
        parts = st.session_state.final_res.split("||")
        if len(parts) >= 2:
            st.divider()
            st.write(parts[0].strip())
            # Directly use the URL in a standard anchor tag to ensure external redirect
            video_url = parts[1].strip()
            st.markdown(f'<a href="{video_url}" target="_blank" style="text-decoration:none;"><button style="background-color:#FF4B4B; color:white; border:none; padding:10px 20px; border-radius:10px; cursor:pointer; font-weight:bold;">📺 Watch on YouTube</button></a>', unsafe_allow_html=True)

    if st.session_state.note:
        st.write("---")
        if st.button("🔄 Reset"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
