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
                
                STRICT RULES:
                1. KEEP IT CHILL: Don't be over-romantic or dramatic. Be a supportive friend/partner.
                2. NO TRANSLATIONS: Just write the Manglish words naturally.
                3. PERSONA: Use 'Nee/Ninakku'. If she has a problem, suggest a simple Kerala remedy.
                4. LENGTH: Keep the note natural and realistic.
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
            with st.spinner(""):
                sub_prompt = f"""
                Suggest a {choice} scene for mood: {st.session_state.mood} and context: "{user_text}".
                
                RULES:
                1. ALWAYS provide a real YouTube Video ID. Pivot to similar vibes if no exact match.
                2. FORMAT: [Scene Name] || [YouTube Video ID] || [Famous Dialogue] || [Cute/Funny Troll]
                3. TROLL TONE: Make it a fun, light-hearted tease. NOT overly romantic.
                4. LANGUAGE: If Malayalam Movie, troll in MALAYALAM SCRIPT (മലയാളം). If Friends, English.
                5. Connect it to her context/mood naturally.
                """
                res = model.generate_content(sub_prompt)
                st.session_state.final_res = res.text

    # --- 4. VIDEO & TROLL ---
    if st.session_state.final_res:
        parts = st.session_state.final_res.split("||")
        if len(parts) >= 4:
            st.divider()
            st.info(f"🎬 **For you:** {parts[0].strip()}")
            st.video(f"https://www.youtube.com/watch?v={parts[1].strip()}") 
            st.markdown(f"**🗣️ {parts[2].strip()}**")
            # Cute troll without the extra romance
            st.warning(f"😜 **Hehe...**\n\n{parts[3].strip()}")

    if st.session_state.note:
        st.write("---")
        if st.button("🔄 Reset"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
