import google.generativeai as genai

# ✅ Use your actual API key
genai.configure(api_key="AIzaSyChznhf7CGP83rrQnwsaKpDINergppgMZE")

# ✅ Choose a model from your available list (use one that supports generateContent)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

def get_bot_response(prompt: str) -> str:
    try:
        # This is the correct call for 'generateContent' models
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Bot: Error from Gemini: {str(e)}"
