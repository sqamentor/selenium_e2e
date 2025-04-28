import openai
import os
import re
from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Map common user-friendly labels to expected field intents
LABEL_ALIASES = {
    "otp": "Code",
    "one time password": "Code",
    "verify otp": "Code",
    "verify code": "Verify Code",
    "submit otp": "Verify Code",
    "text message": "Text",
    "phone": "Cell Phone Number",
    "email address": "E-mail",
    "zip": "Zip Code",
    "postal code": "Zip Code"
}

def normalize_label(label):
    label = label.lower().strip()
    return LABEL_ALIASES.get(label, label)

def openai_match_field(candidates, user_label: str, field_type: str):
    user_label = normalize_label(user_label)
    # Filter and prioritize input-like fields and select/button
    filtered = [c for c in candidates if c["tag"].lower() in ["input", "button", "select", "textarea"]]
    trimmed = filtered[:30]  # Limit to top 30 for token limits

    # Improve prompt quality
    prompt = f"""
You are a smart DOM element matcher. Match the user's requested label and interaction type to the most appropriate DOM element.

Label: "{user_label}"
Expected interaction type: "{field_type}" (e.g. textbox, dropdown, click)

Each DOM element includes fields like:
  - tag
  - id
  - formcontrolname
  - name
  - class
  - aria_label
  - label (from associated <label>)
  - placeholder
  - text (innerText)
  - xpath

Candidates:
{trimmed}

Only return the index (number). Do NOT return text or explanation.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.5-preview",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()

        match = re.search(r'(\\d+)', answer)
        if match:
            idx = int(match.group(1))
            return trimmed[idx] if 0 <= idx < len(trimmed) else None
        else:
            return None
    except Exception as e:
        print("❌ OpenAI matching failed:", e)
        return None