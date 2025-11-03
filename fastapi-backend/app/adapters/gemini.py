import os
from google import genai
from google.genai import types

_client = None

def get_client():
    global _client
    if _client:
        return _client

    # Gemini API key picked via env
    _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


async def normalize_with_gemini(text: str) -> str:
    client = get_client()

    system_instruction = (
        "Rewrite the diary text as a short uplifting music search query.\n"
        "Rules:\n"
        "- 5–12 words\n"
        "- No JSON, no quotes, no lists\n"
        "- If diary is sad/stressed → make it hopeful\n"
        "- Output only the search query\n"
        "Example:\n"
        "Input: \"Feeling lonely and drained today\"\n"
        "Output: warm comforting songs to uplift loneliness"
    )

    try:
        resp = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.4,
            ),
        )

        # ✅ Extract text per GenAI SDK recommended pattern
        # Try direct .text
        if getattr(resp, "text", None):
            out = resp.text.strip()
            if out:
                return out

        # Try candidate parts
        if resp.candidates:
            for c in resp.candidates:
                if c.content and c.content.parts:
                    for p in c.content.parts:
                        if getattr(p, "text", None):
                            out = p.text.strip()
                            if out:
                                return out

        # If we reach here → no text found
        raise ValueError("No valid text returned")

    except Exception as e:
        print("Gemini rewrite error:", e)
        return "uplifting songs to feel better after a bad day"
    
    
async def translate_query(text: str, target_lang: str) -> str:
    client = get_client()

    prompt = f"Translate this music search query into {target_lang}. Only return translated text:\n{text}"

    try:
        resp = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=40,
                temperature=0.2
            )
        )
        if resp.text:
            return resp.text.strip()
    except Exception as e:
        print("Translation error:", e)

    # fallback
    return text
