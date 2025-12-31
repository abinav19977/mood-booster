with st.spinner("Finding a video..."):
    sub_prompt = f"""
    Suggest a {choice} scene for mood: {st.session_state.mood} and context: "{user_text}".
    
    STRICT RULES:
    1. You MUST provide a real YouTube Video ID. 
    2. If no exact match for "{user_text}" exists, pick a famous scene with similar energy (celebration, comedy, or chill vibe).
    3. NO TEXT-ONLY REPLIES. NO DISCLAIMERS. NO INTROS like "Okay here is a suggestion".
    
    Format STRICTLY: [Scene Name] || [YouTube Video ID] || [Famous Dialogue] || [Short Troll Comment]
    
    TROLL RULES: 
    - If Malayalam Movie: Write troll in MALAYALAM SCRIPT (മലയാളം).
    - If Friends: Write troll in English.
    - Max 3-4 lines. Address her as 'Nee'.
    """
    res = model.generate_content(sub_prompt)
    st.session_state.final_res = res.text
