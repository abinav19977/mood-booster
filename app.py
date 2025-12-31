import streamlit as st
import google.generativeai as genai

# --- CONFIG ---
# Ensure your API Key is set in Streamlit Cloud Secrets as GEMINI_API_KEY
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing API Key! Please add it to Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def main():
    st.set_page_config(page_title="Hi Achu", page_icon="❤️")
    
    # Custom CSS to keep the UI clean and hide Streamlit's default headers/footers
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stButton>button {width: 100%; border-radius: 10px;}
        </style>
        """, unsafe_allow_html=True)

    st.title("✨ Hi Achu...")

    # Initialize all session states
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
        if col.button(f"{icons[i]}\n\n{moods[i]}", key=f"mood_{i}"):
            # Reset everything when mood changes
            st.session_state.mood = moods[i]
            st.session_state.note = None
            st.session_state.show_choices = False
            st.session_state.final_res = None

    if st.session_state.mood:
        st.divider()
        # Toggle with Edooo at the start
        elab = st.toggle("Edooo, Kooduthal enthelum parayanundo?")
        user_text = st.text_area("Para...", placeholder="Enthelum vishesham undo?") if elab else ""

        if st.button("🚀 Boost Me"):
            with st.spinner(""):
                # System Prompt to act as a Mallu Boyfriend
                prompt = f"""
                ACT AS: A caring Malayali boyfriend talking to his girlfriend.
                LANGUAGE: Mix 60% proper English with 40% Manglish naturally. 
                STRICT RULE: No AI introductions like "Sure" or "Here is".
                SCENARIO: Her mood is {st.session_state.mood}. She says: "{user_text}".
                CONTENT: 
                - Address her as 'Edooo' or 'Nee'. 
                - Use 'Ninakku'.
                - If she mentions a physical issue (like a bite, headache, or pain), suggest a natural Kerala remedy (lime, turmeric, etc.).
                - Use plenty of heart and hug emojis.
                - Be romantic but simple and human.
                """
                res = model.generate_content(prompt)
                st.session_state.note = res.text

    # --- 2. THE NOTE (Always shown first) ---
    if st.session_state.note:
        st.success("💌 **Message:**")
        st.write(st.session_state.note)
        
        # Ask for Movie/Friends suggestion
        if not st.session_state.show_choices:
            st.write("Edooo, ninakku ippo mood boost cheyyan oru movie scene suggest cheyyatte?")
            y, n = st.columns(2)
            if y.button("✅ Yes"):
                st.session_state.show_choices = True
                st.rerun()
            if n.button("❌ No"):
                st.info("Okay Edooo, take care eeh! Nee chill ayitt iriku. ❤️")

    # --- 3. THE CHOICE (Only if Yes is clicked) ---
    if st.session_state.show_choices:
        st.divider()
        st.write("Pick your vibe, Edooo:")
        c1, c2 = st.columns(2)
        
        choice = None
        if c1.button("🍿 Malayalam Movie"): choice = "Malayalam Movie"
        if c2.button("☕ Friends Series"): choice = "Friends Series"
        
        if choice:
            with st.spinner("Searching for the perfect clip..."):
                sub_prompt = f"""
                As the boyfriend, suggest a specific {choice} scene for mood {st.session_state.mood} and context "{user_text}".
                Format the response STRICTLY as follows with || as the separator:
                [Scene Name] || [YouTube Video ID] || [Famous Dialogue/Line] || [A natural, funny boyfriend-style comment or roast connecting the scene to her situation]
                Example: CID Moosa || GwCdPTIaFPU || Enne erumbu kadichu! || Edooo, ithu pole build-up kodukkathe maryaadhakk cream idu!
                """
                res = model.generate_content(sub_prompt)
                st.session_state.final_res = res.text

    # --- 4. FINAL VIDEO AND BANTER ---
    if st.session_state.final_res:
        parts = st.session_state.final_res.split("||")
        if len(parts) >= 4:
            st.divider()
            scene_name = parts[0].strip()
            yt_id = parts[1].strip()
            dialogue = parts[2].strip()
            comment = parts[3].strip()
            
            st.info(f"🎬 **For you:** {scene_name}")
            # Embeds the video directly in the app
            st.video(f"https://www.youtube.com/watch?v={yt_id}") 
            
            st.markdown(f"**🗣️ {dialogue}**")
            st.write(comment)

    # Reset Button at the bottom
    if st.session_state.note:
        if st.button("🔄 Start Over"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
