import streamlit as st
import google.generativeai as genai

# --- CONFIG ---
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing API Key in Secrets!")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def main():
    st.set_page_config(page_title="Hi Achu", page_icon="❤️")
    
    # Hide all technical streamlit labels
    st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>""", unsafe_allow_html=True)

    st.title("✨ Hi Achu...")

    if "mood" not in st.session_state: st.session_state.mood = None
    if "response" not in st.session_state: st.session_state.response = None

    # 1. MOOD SELECTION
    st.write("Edooo, Mood engane undu?")
    cols = st.columns(4)
    moods = ["Happy", "Neutral", "Sad", "Angry"]
    icons = ["😃", "😐", "😢", "😡"]
    
    for i, col in enumerate(cols):
        if col.button(f"{icons[i]}\n\n{moods[i]}", use_container_width=True):
            st.session_state.mood = moods[i]
            st.session_state.response = None 

    if st.session_state.mood:
        st.divider()
        
        # Edooo moved to the start of the toggle
        elab = st.toggle("Edooo, Kooduthal enthelum parayanundo?")
        user_text = ""
        if elab:
            user_text = st.text_area("Para...", placeholder="Share what's on your mind, I'm listening...")

        if st.button("🚀 Boost Me"):
            # Empty spinner to hide "trolling in progress" text
            with st.spinner(""):
                prompt = f"""
                Context: The user is my girlfriend. 
                Her current mood: {st.session_state.mood}. 
                Details she shared: {user_text if user_text else 'None'}.
                
                STRICT RULES:
                1. START DIRECTLY: Do not show any AI technical intros or "Here is your request."
                2. LANGUAGE RATIO: 60% proper English + 40% Manglish. 
                3. TONE: Romantic, deeply caring, and genuinely supportive. Not robotic.
                4. ADVICE CONTENT: Give thoughtful advice. Include a very short motivational story, a real-life example, or a famous quote (like Rumi, Marcus Aurelius, or Maya Angelou) that fits her specific situation to lift her up.
                5. TRANSITION: After the note, you MUST ask: "Edooo, mood boost cheyyan oru Malayalam movie scene suggest cheyyatte, atho Friends series-ile oru clip veno?"
                6. SELECTION: Based on her situation, pick ONE specific Malayalam movie scene OR ONE specific 'Friends' scene.
                7. SEARCH: Provide a specific YouTube search query for the exact video scene.
                8. TROLL: End with a funny Malayalam troll or a classic dialogue from that scene that playfully roasts her or her current situation.
                
                Format: Note: [text] || Choice: [name] || Search: [query] || Troll: [text]
                """
                res = model.generate_content(prompt)
                st.session_state.response = res.text

    # DISPLAY RESULTS
    if st.session_state.response:
        try:
            parts = st.session_state.response.split("||")
            
            # Message Section (Filters technical chatter)
            note_content = parts[0].replace("Note:", "").strip()
            # Emergency filter to remove any "Okay" or "Here's the result" starting lines
            if note_content.lower().startswith("okay") or note_content.lower().startswith("here"):
                 note_content = "\n".join(note_content.split("\n")[1:])

            st.success("💌 **Message:**")
            st.write(note_content)
            
            # Scene Section
            if len(parts) > 2:
                st.divider()
                scene_name = parts[1].replace("Choice:", "").strip()
                search_query = parts[2].replace("Search:", "").strip()
                
                st.info(f"🎬 **For you:** {scene_name}")
                yt_link = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}+official+scene"
                st.link_button(f"📺 Watch Now", yt_link)
            
            # Troll Section
            if len(parts) > 3:
                st.warning("😜 **Hehe...**")
                st.write(parts[3].replace("Troll:", "").strip())
        except:
            st.error("Click Boost Me again!")

if __name__ == "__main__":
    main()
