import os
import json
from google import genai
from google.genai import types

def discover_colleges(query, state=""):
    """
    Finds verified colleges using Gemini AI and returns structured data.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY is not set.")
        return []

    client = genai.Client(api_key=api_key)

    prompt = f"""
    A student searched for '{query}' on Mentorex (mentorex.co.in). State filter: {state or 'Any'}.
    Provide up to 4 REAL, verified institutions in India matching this query.
    Return JSON list with:
    - name (Full name)
    - shortName (Acronym or short form, e.g. RVCE)
    - city
    - state
    - nirfRank (number or null)
    - type (Public/Private/Autonomous)
    - averagePlacementInr (in Rupees per year, e.g. 1100000)
    - websiteUrl
    - description (1-2 sentences)
    """

    models = ["gemini-2.5-flash", "gemini-1.5-flash"]
    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            data = json.loads(response.text)
            if isinstance(data, list):
                # Add source tag
                for item in data:
                    item["source"] = "ai_discovered"
                return data
        except Exception as e:
            print(f"Model {model} error: {e}")
            continue

    return []
