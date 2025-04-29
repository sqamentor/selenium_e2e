# ai_helpers/screenshot_analyzer.py
import pytesseract
from PIL import Image
from openai import OpenAI
import openai
import sys,os
from dotenv import load_dotenv

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_screenshot(path):
    text = pytesseract.image_to_string(Image.open(path))
    prompt = f"This error screenshot shows: {text}\n\nExplain what's likely wrong and suggest fix:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response['choices'][0]['message']['content']
