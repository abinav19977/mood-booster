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
    states = {"mood": None, "note": None, "show_choices": False, "final_res": None, "play_spell_bee": False, "current_word": None}
    for key, val in states.items():
        if key not in st.session_state: st.session_state[key] = val

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
                prompt = f"Act as a Mallu boyfriend. Tone: 60% Funny, 10% Warm, 30% Teasing. Lang: 50% Manglish/English. Max 250 words. Mood: {st.session_state.mood}, Detail: {user_text}. Use 'Edooo/Nee'. No filmy malayalam."
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
        st.write("Video venda alle? Enna namukku oru Spell Bee kalichalo?")
        
        if not st.session_state.current_word:
            st.session_state.current_word = random.choice(SPELL_BEE_WORDS)

        # Sound playing option
        tts = gTTS(text=st.session_state.current_word, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
        st.caption("Click play to hear the word.")

        # Input and Check
        guess = st.text_input("Type the spelling here:", key="spell_input").strip()
        if st.button("Check Spelling"):
            if guess.lower() == st.session_state.current_word.lower():
                st.balloons()
                st.success("Good work! Achumol brilliance thanne! 😎")
                if st.button("Play Next Word"):
                    st.session_state.current_word = random.choice(SPELL_BEE_WORDS)
                    st.rerun()
            else:
                st.error("Try again! Itra paranjittum mansiayilla? Teasing you! 😉")

    # --- 4. MOVIE CHOICE (If Yes) ---
    if st.session_state.show_choices and not st.session_state.final_res:
        st.divider()
        st.write("Pick your vibe:")
        c1, c2 = st.columns(2)
        sel = None
        if c1.button("🍿 Malayalam"): sel = "Malayalam Movie Comedy Best Scenes"
        if c2.button("☕ Friends"): sel = "Friends TV Show Chandler Joey funny moments"
        
        if sel:
            with st.spinner("Searching..."):
                sub_prompt = f"Suggest a real {sel} link for mood {st.session_state.mood}. Format: [Natural Banter] || [YouTube Search Link]. Tone: 60/10/30. No dialogues."
                res = model.generate_content(sub_prompt)
                st.session_state.final_res = res.text
                st.rerun()

    if st.session_state.final_res:
        parts = st.session_state.final_res.split("||")
        if len(parts) >= 2:
            st.divider()
            st.write(parts[0].strip())
            st.markdown(f"🔗 **[Watch here]({parts[1].strip()})**")

    if st.session_state.note:
        st.write("---")
        if st.button("🔄 Reset"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
