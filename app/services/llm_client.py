"""
LLM client abstraction layer.
Supports Google Gemini with fallback mock mode when no API key is configured.
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
_USE_MOCK = (not GEMINI_API_KEY) or GEMINI_API_KEY == "your_gemini_api_key_here"

client = None

if not _USE_MOCK:
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_API_KEY)
        print(f"[LLM] Gemini client initialised with model: {LLM_MODEL}")
    except Exception as e:
        print(f"[LLM] Failed to init Gemini client: {e}. Using mock mode.")
        _USE_MOCK = True
else:
    print("[LLM] No valid API key found. Using mock/fallback mode.")


def generate_text(prompt: str, system_prompt: str = "") -> str:
    """Generate free-form text from the LLM."""
    if _USE_MOCK:
        return _mock_generate(prompt)

    from google.genai import types
    contents = []
    if system_prompt:
        contents.append(types.Content(role="user", parts=[types.Part(text=system_prompt)]))
        contents.append(types.Content(role="model", parts=[types.Part(text="Understood.")]))
    contents.append(types.Content(role="user", parts=[types.Part(text=prompt)]))

    try:
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=4096),
        )
        return response.text
    except Exception as e:
        print(f"[LLM] Generation error: {e}")
        return _mock_generate(prompt)


def extract_structured(prompt: str, schema_class, system_prompt: str = ""):
    """
    Extract structured data matching a Pydantic schema.
    Returns a dict matching the schema.
    """
    if _USE_MOCK:
        return _mock_structured(schema_class)

    from google.genai import types

    contents = []
    if system_prompt:
        contents.append(types.Content(role="user", parts=[types.Part(text=system_prompt)]))
        contents.append(types.Content(role="model", parts=[types.Part(text="Understood.")]))
    contents.append(types.Content(role="user", parts=[types.Part(text=prompt)]))

    try:
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema_class,
                temperature=0.1,
                max_output_tokens=4096,
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"[LLM] Structured extraction error: {e}")
        return _mock_structured(schema_class)


def _mock_generate(prompt: str) -> str:
    """Fallback mock text generation for demo without API key."""
    if "outreach" in prompt.lower() or "recruiter" in prompt.lower():
        return json.dumps({
            "conversation": [
                {"role": "recruiter", "message": "Hi! I came across your profile and think you'd be a great fit for this role. Would you be interested in learning more?"},
                {"role": "candidate", "message": "Thanks for reaching out! I'm definitely open to hearing more about the opportunity."},
                {"role": "recruiter", "message": "Great! The role involves building backend systems with Python and FastAPI. The compensation range is 18-28 LPA. Does that align with your expectations?"},
                {"role": "candidate", "message": "That sounds interesting and the compensation range works for me. I'd love to discuss further."},
            ]
        })
    return "Mock LLM response."


def _mock_structured(schema_class) -> dict:
    """Fallback mock structured extraction."""
    try:
        instance = schema_class()
        return instance.model_dump()
    except Exception:
        return {}
