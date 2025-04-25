
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_match_field(candidates, user_label: str, field_type: str):
    prompt = f"""
You are a form field identifier AI. Match the following user request with the best DOM element.

User label: "{user_label}"
Expected type: "{field_type}"

Candidates:
{candidates}

Return the index of the best matching field (starting from 0), or -1 if none match.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{ "role": "user", "content": prompt }]
    )
    answer = response["choices"][0]["message"]["content"]
    try:
        idx = int(answer.strip())
        return candidates[idx] if 0 <= idx < len(candidates) else None
    except:
        return None
