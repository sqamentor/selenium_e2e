# ai_utils.py
from openai import OpenAI
import os
import logging
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup  # for minimal HTML cleaning
#from shutil import which

#if which("tesseract") is None:
#    logging.error("Tesseract not found. Please install and add to PATH.")

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def explain_error_with_ai(error_message: str):
    if os.getenv("USE_AI", "true").lower() != "true":
        logging.info("[AI] Skipping AI explanation (disabled).")
        return

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4.5-preview-2025-02-27",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"I'm running a Chrome automation script with Selenium and encountered this error:\n\n"
                        f"{error_message}\n\n"
                        "What likely caused it and what can I do to fix it?"
                    )
                }
            ],
            temperature=1.0,
            max_tokens=300
        )

        explanation = response.choices[0].message.content.strip()
        logging.warning("[AI] Diagnostic Suggestion:\n" + explanation)

    except Exception as e:
        logging.warning(f"[AI] Failed to get AI explanation: {e}")


def summarize_logs_with_ai(log_file_path: str):
    if os.getenv("USE_AI", "true").lower() != "true":
        logging.info("[AI] Skipping log summarization (disabled via config).")
        return

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            lines = log_file.readlines()[-150:]
            log_tail = ''.join(lines)

        prompt = (
            "You are a test automation assistant. Summarize the following Selenium logs. "
            "Highlight errors, timeouts, ChromeDriver issues,anything suspicious or flaky behaviors::\n\n"
            f"{log_tail}"
        )

        response = client.chat.completions.create(
            model="gpt-4.5-preview-2025-02-27",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=1.0,
            max_tokens=300
        )

        summary = response.choices[0].message.content.strip()
        logging.info("[AI] Run Summary:\n" + summary)

    except Exception as e:
        logging.warning(f"[AI] Log summarization failed: {e}")


def analyze_screenshot_with_gpt(screenshot_path: str):
    """Extract text from screenshot and use GPT to analyze what went wrong."""
    try:
        # Step 1: OCR
        logging.info(f"[AI] Extracting text from screenshot: {screenshot_path}")
        text = pytesseract.image_to_string(Image.open(screenshot_path))

        if not text.strip():
            logging.warning("[AI] No readable text found in screenshot.")
            return

        # Step 2: AI Diagnostic
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = (
            "TThe following text was extracted from a screenshot during a Selenium Automation of Chrome's screenshot:\n\n"
            f"{text}\n\n"
            "What problem is shown, and what might be the cause/fix in Selenium ?"
        )

        response = client.chat.completions.create(
            model="gpt-4.5-preview-2025-02-27",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,
            max_tokens=300
        )

        result = response.choices[0].message.content.strip()
        logging.warning("[AI] Screenshot Diagnosis:\n" + result)

    except Exception as e:
        logging.warning(f"[AI] Screenshot analysis failed: {e}")

def verify_page_with_ai(driver, url):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        html = driver.page_source

        # Optional: Minimize HTML size
        soup = BeautifulSoup(html, "html.parser")
        text_only = soup.get_text(separator="\n")
        cleaned_text = "\n".join(text_only.splitlines()[:100])  # Only first 100 lines

        prompt = (
            f"You're a smart QA assistant. Analyze this content returned when visiting {url} in Selenium:\n\n"
            f"{cleaned_text}\n\n"
            "Does this look like a real page, a login screen, or a browser/network error? "
            "Give a short explanation and confidence score out of 10."
        )

        response = client.chat.completions.create(
            model="gpt-4.5-preview-2025-02-27",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,
            max_tokens=300
        )

        analysis = response.choices[0].message.content.strip()
        logging.info(f"[AI] Page Verification Result:\n{analysis}")

    except Exception as e:
        logging.warning(f"[AI] Page verification failed: {e}")