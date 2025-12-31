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
        .watch-btn {
            background-color: #FF4B4B;
            color: white;
            padding: 12px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            font-weight: bold;
            border-radius: 10px;
            margin: 10px 0px;
        }
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
        elab = st.toggle("Kooduthal enthelum parayanundo?")
        user_text = st.text_area("Para...", placeholder="Endhaanappa vishesham?") if elab else ""

        if st.button("🚀 Paraa"):
            with st.spinner(""):
                prompt = f"""
                Act as a Mallu partner. Mood: {st.session_state.mood}, Details: {user_text}.
                Tone: 60% Fun/Sarcastic, 10% Care/Warmth, 30% Teasing.
                Language: Mix of Manglish and English. 
                STRICT RULES:
                - Do NOT use cringe romantic names like 'honey' or 'sweetheart'. 
                - Use 'Edo' or 'Nee'. 
                - Talk like a real Malayali would talk to their partner (natural, relaxed, zero drama).
                - Keep it under 250 words.
                """
                res = model.generate_content(prompt)
                st.session_state.note = res.text

    # --- 2. THE NOTE ---
    if st.session_state.note:
        st.success("💌 **Message:**")
        st.write(st.session_state.note)
        
        if not st.session_state.show_choices and not st.session_state.play_spell_bee:
            st.write("Mood onn boost cheyyan oru scene ayalo?")
            y, n = st.columns(2)
            if y.button("✅ Pinne enna!"):
                st.session_state.show_choices = True
                st.rerun()
            if n.button("❌ Venda"):
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
                st.success("Correct-aanu! Athu pottu, nee entha spelling bee winner aano? 😉")
                if st.button("Next Word"):
                    st.session_state.current_word = random.choice(SPELL_BEE_WORDS)
                    st.rerun()
            else:
                st.error("Thetti! Ithokke itra paadaano? Onnu koodi nokku! 😄")

    # --- 4. MOVIE CHOICE ---
    if st.session_state.show_choices and not st.session_state.final_res:
        st.divider()
        st.write("Vibe select cheyyu:")
        c1, c2 = st.columns(2)
        sel = None 
        if c1.button("🍿 Malayalam Comedy"): sel = "Malayalam Movie Comedy Best Scene"
        if c2.button("☕ Friends"): sel = "Friends TV Show Chandler Joey funny clip"
        
        if sel:
            with st.spinner("Finding video..."):
                sub_prompt = f"""
                Suggest a real YouTube video URL for {sel} based on mood {st.session_state.mood}.
                FORMAT: [Banter] || [YouTube URL]
                RULES: 
                - Banter: Exactly 2 lines. Use Malayalam script for Malayalam movies. English for Friends. 
                - Tone: Funny/Teasing. 
                - URL: MUST be a real direct link. 
                - Example: [Banter] || https://www.youtube.com/watch?v=h3ka9dCpN0I
                """
                res = model.generate_content(sub_prompt)
                st.session_state.final_res = res.text
                st.rerun()

    if st.session_state.final_res:
        parts = st.session_state.final_res.split("||")
        if len(parts) >= 2:
            st.divider()
            st.write(parts[0].strip())
            video_url = parts[1].strip()
            # Direct link button using HTML for reliable redirection
            st.markdown(f'<a href="{video_url}" target="_blank" class="watch-btn">📺 Watch on YouTube</a>', unsafe_allow_html=True)

    if st.session_state.note:
        st.write("---")
        if st.button("🔄 Reset"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
