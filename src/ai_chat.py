# src/ai_chat.py
import os
from groq import Groq

# --- HARDCODED KNOWLEDGE BASE (For Offline Mode) ---
OFFLINE_KNOWLEDGE = {
    "London": {
        "food": "🇬🇧 **London Eats:** You must try **Fish & Chips** at a local pub, **Curry** on Brick Lane, and visit **Borough Market** for street food.",
        "pack": "☔ **London Packing:** Bring a raincoat (weather is unpredictable!), comfortable walking shoes, and layers.",
        "visit": "ferris_wheel **Must Do:** The British Museum (it's free!), Tower of London, and a walk along the South Bank."
    },
    "Mumbai": {
        "food": "🇮🇳 **Mumbai Eats:** Try **Vada Pav** (street burger), **Pav Bhaji** at Juhu Beach, and Parsi food at Britannia & Co.",
        "pack": "👕 **Mumbai Packing:** Light cotton clothes (it's humid!), sunglasses, and sandals.",
        "visit": "🛕 **Must Do:** Gateway of India, Marine Drive at sunset, and the Elephanta Caves."
    },
    "New York": {
        "food": "🇺🇸 **NYC Eats:** Grab a **$1 Slice Pizza**, a Bagel with lox for breakfast, and Halal Guys street cart.",
        "pack": "👟 **NYC Packing:** Good walking shoes are mandatory. In winter, bring a heavy coat.",
        "visit": "statue_of_liberty **Must Do:** Central Park, The Met Museum, and the High Line."
    },
    "Paris": {
        "food": "🇫🇷 **Paris Eats:** Croissants for breakfast, Steak Frites for dinner, and Macarons from Ladurée.",
        "pack": "u **Paris Packing:** Stylish but comfortable outfit. Avoid sweatpants if you want to blend in.",
        "visit": "tower **Must Do:** Eiffel Tower at night, The Louvre, and Montmartre."
    }
}

def get_travel_advice(destination, user_question, api_key=None):
    """
    Generates travel advice using Llama 3.1 via Groq.
    Falls back to 'Smart Dictionary' if no API Key is provided.
    """
    
    # --- REAL AI MODE (With API Key) ---
    if api_key:
        try:
            # --- FIX: Add a 30-second timeout to prevent "Request Timed Out" ---
            client = Groq(api_key=api_key, timeout=30.0)
            
            system_prompt = f"""You are an expert local guide for {destination}. 
            The user asks: "{user_question}"
            Give specific, actionable advice (names of specific dishes, places, or items). 
            Keep it under 50 words. Use emojis."""
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.7,
                max_tokens=150,
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            return f"⚠️ AI Error: {str(e)}"

    # --- OFFLINE MODE (Smart Fallback) ---
    city_name = destination.split(",")[0].strip() 
    
    found_city = None
    for key in OFFLINE_KNOWLEDGE:
        if key.lower() in city_name.lower():
            found_city = OFFLINE_KNOWLEDGE[key]
            break
            
    if found_city:
        q = user_question.lower()
        if "eat" in q or "food" in q:
            return found_city["food"]
        elif "pack" in q or "wear" in q:
            return found_city["pack"]
        elif "visit" in q or "do" in q:
            return found_city["visit"]
    
    return f"🤖 **Offline Mode:** I don't have specific data for **{city_name}** yet. Please add a free Groq API Key to the sidebar to unlock full AI intelligence!"