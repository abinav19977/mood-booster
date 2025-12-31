import streamlit as st
import google.generativeai as genai

# --- CONFIG ---
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing API Key! Please add it to Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def main():
    st.set_page_config(page_title="Hi Achu", page_icon="❤️")
    
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .big-title {
            font-size: 50px !important;
            font-weight: 700;
            margin-bottom: 20px;
            color: #FF4B4B;
        }
        .stButton>button {width: 100%; border-radius: 10px; height: 3em;}
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<p class="big-title">✨ Hi Achu...</p>', unsafe_allow_html=True)

    if "mood" not in st.session_state: st.session_state.mood = None
    if "note" not in st.session_state: st.session_state.note = None
    if "show_choices" not in st.session_state: st.session_state.show_choices = False
    if "final_res" not in st.session_state: st.session_state.final_res = None

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

    if st.session_state.mood:
        st.divider()
        elab = st.toggle("Edooo, Kooduthal enthelum parayanundo?")
        user_text = st.text_area("Para...", placeholder="Enthelum vishesham undo?") if elab else ""

        if st.button("🚀 Boost Me"):
            with st.spinner(""):
                prompt = f"""
                Act as a Malayali boyfriend. Language: 70% Simple English, 30% Manglish.
                Mood: {st.session_state.mood}. Detail: {user_text}.
                Rules: Be chill, caring, and human. No drama. No translations. Use 'Nee/Ninakku'.
                Suggest Kerala home remedies if she has a physical problem. 
                """
                res = model.generate_content(prompt)
                st.session_state.note = res.text

    # --- 2. THE NOTE & CHOICE ---
    if st.session_state.note:
        st.success("💌 **Message:**")
        st.write(st.session_state.note)
        
        if not st.session_state.show_choices:
            st.write("Edooo, mood boost cheyyan oru scene suggest cheyyatte?")
            y, n = st.columns(2)
            if y.button("✅ Yes"):
                st.session_state.show_choices = True
                st.rerun()
            if n.button("❌ No"):
                st.info("Okay Edooo, take care! ❤️")

    # --- 3. MOVIE/FRIENDS CHOICE ---
    if st.session_state.show_choices:
        st.divider()
        st.write("Pick your vibe:")
        c1, c2 = st.columns(2)
        
        choice = None
        if c1.button("🍿 Malayalam"): choice = "Malayalam Movie"
        if c2.button("☕ Friends"): choice = "Friends Series"
        
        if choice:
            with st.spinner("Finding a video..."):
                sub_prompt = f"""
                Suggest a {choice} scene for mood: {st.session_state.mood} and context: "{user_text}".
                
                MANDATORY RULE: 
                - You MUST provide a real YouTube Video ID. 
                - If no exact match for "{user_text}" exists, pick a famous scene with similar energy.
                - NO text-only replies or excuses.
                
                Format STRICTLY: [Scene Name] || [YouTube Video ID] || [Famous Dialogue] || [Cute Troll Comment]
                
                TROLL RULES: 
                - Make it a cute, funny boyfriend-style roast. 
                - Connect it to her mood/context AND the movie scene.
                - If Malayalam Movie: Write in MALAYALAM SCRIPT (മലയാളം).
                - If Friends: Write in English.
                - Max 3-4 lines.
                """
                res = model.generate_content(sub_prompt)
                st.session_state.final_res = res.text

    # --- 4. VIDEO & CUTE TROLL ---
    if st.session_state.final_res:
        parts = st.session_state.final_res.split("||")
        if len(parts) >= 4:
            st.divider()
            st.info(f"🎬 **For you:** {parts[0].strip()}")
            st.video(f"https://www.youtube.com/watch?v={parts[1].strip()}") 
            st.markdown(f"**🗣️ {parts[2].strip()}**")
            # This is the cute troll section
            st.warning(f"😜 **Hehe...**\n\n{parts[3].strip()}")

    if st.session_state.note:
        st.write("---")
        if st.button("🔄 Reset"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
