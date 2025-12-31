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
    
    # Custom Styling for the Big Logo
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

    # 1. Initialize session states properly to avoid NameErrors
    if "mood" not in st.session_state: st.session_state.mood = None
    if "note" not in st.session_state: st.session_state.note = None
    if "show_choices" not in st.session_state: st.session_state.show_choices = False
    if "final_res" not in st.session_state: st.session_state.final_res = None

    # --- MOOD SELECTION ---
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
                Act as a caring Malayali boyfriend. 
                Tone: 60% Fun, 20% Romantic, 20% Serious.
                Language: 50% Manglish, 50% Simple English. Main content in English.
                Mood: {st.session_state.mood}. Detail: {user_text}.
                Rules: Use 'Nee/Ninakku'. No translations.
                """
                res = model.generate_content(prompt)
                st.session_state.note = res.text

    # --- THE NOTE ---
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

    # --- MOVIE CHOICE ---
    if st.session_state.show_choices and not st.session_state.final_res:
        st.divider()
        st.write("Pick your vibe:")
        c1, c2 = st.columns(2)
        
        # We use a localized variable here to avoid top-level NameErrors
        current_selection = None 
        if c1.button("🍿 Malayalam"): current_selection = "Malayalam Movie"
        if c2.button("☕ Friends"): current_selection = "Friends Series"
        
        if current_selection:
            with st.spinner("Finding something for you..."):
                sub_prompt = f"""
                Suggest a {current_selection} scene for mood: {st.session_state.mood} and context: "{user_text}".
                MANDATORY FORMAT: [Natural Banter] || [Scene Name] || [YouTube Link] || [Famous Dialogue]
                RULES:
                1. Banter First: 3-4 lines (60% fun, 20% romantic, 20% serious). 
                2. No labels like "Troll" or "Banter".
                3. If Malayalam: Banter in Malayalam script. If Friends: English.
                4. Link: Provide a direct URL link only. No embeds.
                """
                res = model.generate_content(sub_prompt)
                st.session_state.final_res = res.text
                st.rerun()

    # --- DISPLAY RESULT ---
    if st.session_state.final_res:
        parts = st.session_state.final_res.split("||")
        if len(parts) >= 4:
            st.divider()
            # 1. Natural Banter First
            st.write(parts[0].strip())
            # 2. Scene Info and Direct Link
            st.info(f"🎬 **{parts[1].strip()}**")
            st.markdown(f"🔗 **[Watch here]({parts[2].strip()})**")
            st.markdown(f"*🗣️ {parts[3].strip()}*")

    if st.session_state.note:
        st.write("---")
        if st.button("🔄 Reset"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
