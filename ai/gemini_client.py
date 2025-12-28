# ai/gemini_client.py

from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def gemini_generate(prompt: str) -> str:
    response = client.models.generate_content(
        model="models/gemini-flash-latest",  # ✅ EXACT MATCH
        contents=prompt
    )
    return response.text
