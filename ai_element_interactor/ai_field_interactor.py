import os
import json
from .dom_extractor import extract_all_elements
from .label_matcher import openai_match_field
from .selector_ranker import rank_selectors
from .interaction_engine import try_selectors
import logging

CACHE_PATH = "ai_element_interactor/selector_cache.json"

def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}

def save_cache(data):
    with open(CACHE_PATH, "w") as f:
        json.dump(data, f, indent=2)

def cache_lookup(url, label, field_type):
    key = f"{label}:{field_type}"
    cache = load_cache()
    return cache.get(url, {}).get(key)

def cache_store(url, label, field_type, selector_type, selector_value):
    key = f"{label}:{field_type}"
    cache = load_cache()
    if url not in cache:
        cache[url] = {}
    cache[url][key] = {
        "type": selector_type,
        "value": selector_value
    }
    save_cache(cache)

def interact_by_label(driver, label, field_type, value=None):
    url = driver.current_url.split("?")[0]

    cached = cache_lookup(url, label, field_type)
    if cached:
        return try_selectors(driver, [(cached['type'], cached['value'], 1.0)], field_type, value, label)

    elements = extract_all_elements(driver)
    best_match = openai_match_field(elements, label, field_type)

    if not best_match:
        raise Exception("No matching field found for: " + label)

    selector_candidates = rank_selectors(best_match)
    result = try_selectors(driver, selector_candidates, field_type, value, label)

    sel = result['selector']
    cache_store(url, label, field_type, sel["type"], sel["value"])

    return {
        "element_info": best_match,
        "selector": sel,
        "action": field_type,
        "value_entered": value,
        "source": "AI Ranker or Fallback"
    }

def fallback_find_code_field(driver, input_value):
    """Special fallback: Locate OTP/Code fields even if AI matching fails."""
    logging.info("[FALLBACK] Trying fallback to locate OTP/Code input...")
    try:
        otp_inputs = driver.find_elements(By.CSS_SELECTOR, "input.otp-field")
        for otp in otp_inputs:
            if otp.is_displayed() and otp.is_enabled():
                logging.info("[FALLBACK] OTP input field found! Attempting to fill...")
                otp.clear()
                otp.send_keys(input_value)
                logging.info(f"[FALLBACK] ✅ Entered OTP Code: {input_value}")
                return True
    except Exception as e:
        logging.error(f"[FALLBACK] ❌ Failed during OTP fallback: {e}")
    return False
