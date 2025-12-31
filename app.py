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
                
                STRICT RULES:
                1. START DIRECTLY: No intro like "Here is your request" or "Trolling". Start immediately with the note.
                2. ADDRESS: Use 'Edooo' or 'Nee'. Never use 'Achu'.
                3. LANGUAGE: Strict 50/50 mix of Manglish and English in every sentence.
                4. ADVICE: Be romantic/human. Use a short story or current issue to boost the mood if details are provided.
                5. TRANSITION: You MUST end the note with this exact Manglish question: "Mood boost cheyyan oru Malayalam movie scene suggest cheyyatte, atho Friends series-ile oru scene veno?"
                6. SUGGESTION: Pick either a famous Malayalam movie scene OR a classic 'Friends' TV show scene based on the mood.
                7. SEARCH: Provide a very specific YouTube search query for that exact scene.
                8. TROLL: A funny Malayalam roast (troll) of the user based on that scene's context.
                
                Format: Note: [text] || Scene: [name] || Search: [query] || Troll: [text]
                """
                res = model.generate_content(prompt)
                st.session_state.response = res.text

    # DISPLAY RESULTS
    if st.session_state.response:
        try:
            raw_text = st.session_state.response
            parts = raw_text.split("||")
            
            # 1. Clean Note (Removes any hidden AI chatter)
            note_content = parts[0].replace("Note:", "").strip()
            # This filter removes any line that looks like a technical description
            lines = note_content.split('\n')
            note_content = "\n".join([l for l in lines if not any(x in l.lower() for x in ["here is", "trolling", "restriction", "request"])])

            st.success("💌 **Message:**")
            st.write(note_content.strip())
            
            # 2. Scene & Link
            if len(parts) > 2:
                st.divider()
                scene_name = parts[1].replace("Scene:", "").strip()
                search_query = parts[2].replace("Search:", "").strip()
                
                st.info(f"🎬 **Suggested Scene:** {scene_name}")
                yt_link = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}+official+scene"
                st.link_button(f"📺 Watch This Scene", yt_link)
            
            # 3. Fun Troll
            if len(parts) > 3:
                st.warning("😜 **Hehe...**")
                st.write(parts[3].replace("Troll:", "").strip())
        except:
            st.error("Click Boost Me again!")

if __name__ == "__main__":
    main()
