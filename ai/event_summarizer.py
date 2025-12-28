from ai.gemini_client import gemini_generate

def summarize_event(text):
    prompt = f"""
    Summarize the following campus event in 3–4 lines.
    Focus on date, venue, purpose, and audience.

    Event Text:
    {text}
    """
    return gemini_generate(prompt)
