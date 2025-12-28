from ai.gemini_client import gemini_generate
import json

def extract_event_info(text):
    prompt = f"""
    Extract event details from the text below.
    Return ONLY valid JSON with these keys:
    title, event_date, event_time, venue

    Text:
    {text}
    """

    response = gemini_generate(prompt)

    try:
        return json.loads(response)
    except:
        return {
            "title": "",
            "event_date": "",
            "event_time": "",
            "venue": ""
        }
