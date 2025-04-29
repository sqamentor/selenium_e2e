import os
import logging
from dotenv import load_dotenv

load_dotenv()
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "manual")

from imports_manager import imports

def run_test():
    try:
        logging.info(f"Starting test in {EXECUTION_MODE} mode.")
        page = imports['BookslotPage']()
        page.execute_test()
    except Exception as e:
        logging.error(f"{EXECUTION_MODE.capitalize()} execution failed: {e}")
        if EXECUTION_MODE == "manual":
            logging.info("Falling back to AI execution.")
            os.environ["EXECUTION_MODE"] = "ai"
            from imports_manager import imports as ai_imports
            ai_page = ai_imports['BookslotPage']()
            ai_page.execute_test()
        else:
            logging.error("AI execution also failed. Test aborted.")

if __name__ == "__main__":
    run_test()
