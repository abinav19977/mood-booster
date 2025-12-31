if choice:
    with st.spinner("Finding a working link..."):
        sub_prompt = f"""
        Suggest a {choice} scene for mood: {st.session_state.mood} and context: "{user_text}".
        
        MANDATORY FORMAT: [Natural Banter] || [Scene Name] || [YouTube Video ID] || [Famous Dialogue]
        
        RULES:
        1. Natural Banter First: 3-4 lines mixing fun (60%), romance (20%), and serious (20%).
        2. YouTube Link: Provide ONLY the full URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID).
        3. Do not use embedded players that might show 'Video Unavailable'.
        """
        res = model.generate_content(sub_prompt)
        st.session_state.final_res = res.text
        st.rerun()

if st.session_state.final_res:
    parts = st.session_state.final_res.split("||")
    if len(parts) >= 4:
        st.divider()
        # 1. Natural Banter (60% Fun, 20% Romantic, 20% Serious)
        st.write(parts[0].strip())
        
        # 2. Direct Functional Link
        st.info(f"🎬 **{parts[1].strip()}**")
        video_url = parts[2].strip()
        st.markdown(f"🔗 **[Watch on YouTube]({video_url})**")
        
        # 3. Famous Dialogue
        st.markdown(f"*🗣️ {parts[3].strip()}*")
