import time
from chrome_automation_launcher import run_chrome_automation
from firefox_automation_launcher import run_firefox_automation
from edge_automation_launcher import run_edge_automation
#from browser_ai_utils import explain_error_with_ai, summarize_logs_with_ai,analyze_screenshot_with_gpt,verify_page_with_ai

# Target URL to open in all browsers
target = "https://google.com"

def safe_run_browser(fn, label):
    try:
        print(f"\n[INFO] Launching {label}...")
        fn(target)
    except Exception as e:
        print(f"[ERROR] Failed to run {label}: {e}")
    finally:
        print(f"[INFO] Completed {label}. Waiting before next...\n")
        time.sleep(3)

# Run Chrome
safe_run_browser(run_chrome_automation, "Chrome")

# Run Firefox
safe_run_browser(run_firefox_automation, "Firefox")

# Run Edge
safe_run_browser(run_edge_automation, "Edge")

print("[DONE] All browsers launched and closed sequentially.")
