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
    st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

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
        elab = st.toggle("Edooo, Koodothal enthenkilum parayanundo?")
        user_text = ""
        if elab:
            user_text = st.text_area("Para...", placeholder="Share what's on your mind...")

        if st.button("🚀 Boost Me"):
            with st.spinner("Connecting..."):
                prompt = f"""
                User mood: {st.session_state.mood}. Detail: {user_text}.
                
                STRICT PERSONALITY RULES:
                1. NO INTRO: Do not say "Okay" or "Here is your request". Start IMMEDIATELY with the note.
                2. ADDRESS: Use 'Edooo' or 'Nee'. NEVER say 'Achu'.
                3. LANGUAGE: Use a strict 50/50 mix of Manglish and English. Mix them in every sentence. 
                   (Example: "Edooo, why are you sitting like this? Oru smile okke itte, let's make this day better.")
                4. ADVICE: If detail is given, give romantic/human advice to boost the mood. Use a short motivational story or a relatable current issue.
                5. TRANSITION: End the note part with: "Mood boost cheyyan nalla oru movie scene suggest cheyyatte?"
                6. MOVIE: Name a specific Malayalam movie and a specific scene.
                7. YOUTUBE: Provide a specific search query that will find the EXACT scene (not a group).
                8. TROLL: A funny Malayalam troll roasting the user based on that specific scene.
                
                Format: Note: [text] || Movie: [name] || Search: [specific search query] || Troll: [text]
                """
                res = model.generate_content(prompt)
                st.session_state.response = res.text

    # DISPLAY RESULTS
    if st.session_state.response:
        try:
            # Cleanup AI chatter if it happens
            raw_text = st.session_state.response
            if "Note:" not in raw_text and "||" not in raw_text:
                st.error("AI is being moody. Try clicking again!")
                st.stop()
                
            parts = raw_text.split("||")
            
            # 1. Clean the Note
            note_content = parts[0].replace("Note:", "").strip()
            # Safety filter for unwanted intros
            note_lines = note_content.split('\n')
            note_content = next((line for line in note_lines if any(word in line.lower() for word in ['edooo', 'nee', 'why', 'is'])), note_content)

            st.success("💌 **Message:**")
            st.write(note_content)
            
            # 2. Movie & Specific Link
            if len(parts) > 2:
                st.divider()
                movie_name = parts[1].replace("Movie:", "").strip()
                search_query = parts[2].replace("Search:", "").strip()
                
                st.info(f"🍿 **Suggested Movie:** {movie_name}")
                # Added "full scene" and "Malayalam" to the search to make it more specific
                yt_link = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}+Malayalam+movie+scene+official"
                st.link_button(f"📺 Watch Specific Scene", yt_link)
            
            # 3. Troll Section
            if len(parts) > 3:
                st.warning("😜 **Hehe...**")
                st.write(parts[3].replace("Troll:", "").strip())
        except:
            st.error("Click Boost Me again for a better response!")

if __name__ == "__main__":
    main()
