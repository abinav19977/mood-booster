import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import random
import io

# --- CONFIG ---
PAGE_LOGO = "535a00a0-0968-491d-92db-30c32ced7ac6.webp" 
# Added more words for variety
SPELL_BEE_WORDS = ["Enthusiastic", "Serendipity", "Magnanimous", "Quintessential", "Pharaoh", "Onomatopoeia", "Bourgeois", "Mischievous"]

# ... (rest of your existing configuration and header code) ...

    # --- 3. SPELL BEE GAME ---
    if st.session_state.play_spell_bee:
        st.divider()
        st.subheader("🐝 Spell Bee Time!")
        st.write("Video venda alle? Enna namukku oru Spell Bee kalichalo?")
        
        # Initialize a word if not present
        if not st.session_state.current_word:
            st.session_state.current_word = random.choice(SPELL_BEE_WORDS)

        # Generate Audio
        try:
            tts = gTTS(text=st.session_state.current_word, lang='en')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format='audio/mp3')
            st.caption("Click play to hear the word.")
        except Exception as e:
            st.error("Audio generation error. Check your connection!")

        # User Input with Tone: 60% Fun, 10% Rom, 30% Tease
        guess = st.text_input("Type the spelling here:", key="spell_input").strip()
        
        if st.button("Check Spelling"):
            if guess.lower() == st.session_state.current_word.lower():
                st.balloons()
                st.success("Good work! Achumol brilliance thanne! 😎")
                # Clear word so a new one picks up next time
                if st.button("Next Word?"):
                    st.session_state.current_word = random.choice(SPELL_BEE_WORDS)
                    st.rerun()
            else:
                # 30% Teasing Tone
                st.error("Try again! Itra paranjittum mansiayilla? Spelling mistakes are your specialty ennu thonunnu! 😉")

# ... (rest of your app logic) ...
