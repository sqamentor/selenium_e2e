# run.py - Master Test Execution Orchestrator

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Determine execution mode
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "manual").lower()

# Import strategies
from execution.manual_execution.strategy.manual_strategy_executor import run_manual_tests
from execution.ai_execution.strategy.ai_strategy_executor import run_ai_tests
# Placeholder imports for future extensions
# from common.core.api_utils.api_test_executor import run_api_tests
# from common/core/db_utils.db_test_executor import run_db_tests
# from common/security/fuzz_engine import run_security_tests
# from common/visual/visual_checker import run_visual_tests

def main():
    print(f"[INFO] Execution Mode: {EXECUTION_MODE}")

    if EXECUTION_MODE == "manual":
        try:
            print("[INFO] Starting manual test execution...")
            run_manual_tests()
        except Exception as e:
            print(f"[WARN] Manual execution failed: {e}")
            print("[INFO] Triggering AI fallback execution...")
            run_ai_tests()

    elif EXECUTION_MODE == "ai":
        print("[INFO] Starting AI test execution...")
        run_ai_tests()

    elif EXECUTION_MODE == "api":
        print("[INFO] Starting API tests...")
        # run_api_tests()

    elif EXECUTION_MODE == "db":
        print("[INFO] Starting DB validation...")
        # run_db_tests()

    elif EXECUTION_MODE == "security":
        print("[INFO] Starting Security/Fuzz tests...")
        # run_security_tests()

    elif EXECUTION_MODE == "visual":
        print("[INFO] Starting Visual UI regression checks...")
        # run_visual_tests()

    else:
        print(f"[ERROR] Unknown EXECUTION_MODE: {EXECUTION_MODE}")

if __name__ == "__main__":
    main()
