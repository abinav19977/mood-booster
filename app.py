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
    
    # Custom CSS to hide Streamlit branding
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
        # Changed label to Edooo first
        elab = st.toggle("Edooo, Koodothal enthenkilum parayanundo?")
        user_text = ""
        if elab:
            user_text = st.text_area("Para...", placeholder="Share what's on your mind...")

        # 3. Removed "Trolling in progress" spinner message
        if st.button("🚀 Boost Me"):
            with st.spinner("Connecting..."):
                prompt = f"""
                User mood: {st.session_state.mood}. Detail: {user_text}.
                
                RULES:
                1. ADDRESS: Always address as 'Edooo' or 'Nee'. NO 'Achu'.
                2. LANGUAGE: 50/50 Manglish and English (Natural flow).
                3. STYLE: Romantic, human-like, not robotic. 
                4. CONTENT: If she elaborated, give advice to boost her mood using human-like words (romantic/supportive). 
                   Use short motivational stories or relate to current positive vibes/issues that lift her spirits.
                5. TRANSITION: End the note with this Malayalam question: "Mood boost cheyyan nalla oru movie scene suggest cheyyatte?"
                6. MOVIE: Suggest ONE Malayalam movie scene based on mood (No Shorts).
                7. TROLL: Provide a fun Malayalam troll/roast based on the character/situation in that movie scene.
                
                Format: Note: [text] || Movie: [name] || Search: [query] || Troll: [text]
                """
                res = model.generate_content(prompt)
                st.session_state.response = res.text

    # DISPLAY RESULTS
    if st.session_state.response:
        try:
            # 2. This logic ensures no "Okay here is your request" text is shown
            parts = st.session_state.response.split("||")
            
            # Message Section
            st.success("💌 **Message:**")
            st.write(parts[0].replace("Note:", "").strip())
            
            # Movie Section
            if len(parts) > 2:
                st.divider()
                movie_name = parts[1].replace("Movie:", "").strip()
                search_query = parts[2].replace("Search:", "").strip()
                
                st.info(f"🍿 **Suggested Movie:** {movie_name}")
                yt_link = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}+full+scene+-shorts"
                st.link_button(f"📺 Watch Scene", yt_link)
            
            # Troll Section
            if len(parts) > 3:
                st.warning("😜 **Hehe...**")
                st.write(parts[3].replace("Troll:", "").strip())
        except:
            st.error("Something went wrong, try clicking Boost again!")

if __name__ == "__main__":
    main()
