simport streamlit as st
import google.generativeai as genai
import os

# --- CONFIG ---
# Updated to match the path provided in your message
PAGE_LOGO = "535a00a0-0968-491d-92db-30c32ced7ac6.webp" 

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing API Key! Please add it to Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def main():
    # Safety Check for Image
    image_exists = os.path.exists(PAGE_LOGO)
    
    st.set_page_config(
        page_title="Achumol is...", 
        page_icon=PAGE_LOGO if image_exists else "🐘"
    )
    
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .big-title {
            font-size: 50px !important;
            font-weight: 700;
            color: #FF4B4B;
            margin: 0;
            line-height: 1.2;
        }
        .stButton>button {width: 100%; border-radius: 10px; height: 3em;}
        </style>
        """, unsafe_allow_html=True)

    # --- BRAND HEADER ---
    head_col1, head_col2 = st.columns([1, 4])
    with head_col1:
        if image_exists:
            st.image(PAGE_LOGO, width=90)
        else:
            st.warning("📸 Image missing")
    with head_col2:
        st.markdown('<p class="big-title">Achumol is...</p>', unsafe_allow_html=True)

    # Initialize session states
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
                Act as a Mallu boyfriend. 
                Tone: 60% Fun, 20% Romantic, 20% Serious.
                Language: 50% Manglish, 50% Simple English. Main content in English.
                Context: Mood is {st.session_state.mood}, detail: {user_text}.
                Instructions: Be a human. Use 'Nee/Ninakku'. 50/50 mix.
                """
                res = model.generate_content(prompt)
                st.session_state.note = res.text

    # --- 2. THE NOTE ---
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

    # --- 3. MOVIE CHOICE ---
    if st.session_state.show_choices and not st.session_state.final_res:
        st.divider()
        st.write("Pick your vibe:")
        c1, c2 = st.columns(2)
        
        sel = None 
        if c1.button("🍿 Malayalam"): sel = "Malayalam Movie Comedy Scene"
        if c2.button("☕ Friends"): sel = "Friends Series Funny Scene"
        
        if sel:
            with st.spinner("Finding something..."):
                sub_prompt = f"""
                You are a Mallu boyfriend. Suggest a real {sel} for mood {st.session_state.mood}.
                FORMAT: [Natural Banter] || [Scene Name] || [Search Link] || [Real Dialogue]
                RULES:
                1. START IMMEDIATELY with the banter (60% Fun, 20% Rom, 20% Ser). 
                2. If Malayalam: Malayalam script. If Friends: English.
                3. Link: Provide a direct YouTube search link.
                """
                res = model.generate_content(sub_prompt)
                st.session_state.final_res = res.text
                st.rerun()

    # --- 4. DISPLAY RESULT ---
    if st.session_state.final_res:
        parts = st.session_state.final_res.split("||")
        if len(parts) >= 4:
            st.divider()
            st.write(parts[0].strip())
            st.info(f"🎬 **{parts[1].strip()}**")
            st.markdown(f"🔗 [Watch on YouTube]({parts[2].strip()})")
            st.markdown(f"*🗣️ {parts[3].strip()}*")

    if st.session_state.note:
        st.write("---")
        if st.button("🔄 Reset"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
