import streamlit as st
import google.generativeai as genai

# Reads the key from Streamlit's Secrets safely
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Missing API Key in Secrets!")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def main():
    st.set_page_config(page_title="Hi Achu", page_icon="❤️")
    st.title("✨ Hi Achu...")

    if "mood" not in st.session_state: st.session_state.mood = None
    if "response" not in st.session_state: st.session_state.response = None

    st.write("Mood engane undu, Edooo?")
    cols = st.columns(4)
    moods = ["Happy", "Neutral", "Sad", "Angry"]
    icons = ["😃", "😐", "😢", "😡"]

    for i, col in enumerate(cols):
        if col.button(f"{icons[i]}\n\n{moods[i]}", use_container_width=True):
            st.session_state.mood = moods[i]
            st.session_state.response = None 

    if st.session_state.mood:
        st.divider()
        elab = st.toggle("Kooduthal enthelum parayanundo, Edooo?")
        user_text = st.text_area("Para...", placeholder="Share heart here...") if elab else ""

        if st.button("🚀 Boost Me"):
            with st.spinner("Trolling in progress..."):
                prompt = f"User is {st.session_state.mood}. Details: {user_text}. 1. NO 'Achu' name. Use 'Edooo' or 'Nee'. 2. 3-4 sentence Manglish note. 3. Suggest ONE Malayalam movie scene. 4. FUNNY TROLL in Malayalam about the moral of that video. Format: Note: [text] || Search: [query] || Moral: [troll_text]"
                res = model.generate_content(prompt)
                st.session_state.response = res.text

    if st.session_state.response:
        parts = st.session_state.response.split("||")
        st.success("💌 **Note:**")
        st.write(parts[0].replace("Note:", "").strip())
        if len(parts) > 1:
            st.divider()
            search = parts[1].replace("Search:", "").strip()
            yt_link = f"https://www.youtube.com/results?search_query={search.replace(' ', '+')}+full+scene+-shorts"
            st.link_button(f"📺 Watch: {search}", yt_link)
        if len(parts) > 2:
            st.warning("😜 **Troll Moral:**")
            st.write(parts[2].replace("Moral:", "").strip())

if __name__ == "__main__":
    main()
