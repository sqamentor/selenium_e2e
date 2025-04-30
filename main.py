"""
main.py
-----------------------------
Centralized test runner that:
- Loads .env configuration
- Executes either manual or AI-driven page interaction
- Falls back to AI if manual execution fails
------------------------------
Allows execution with:
    --mode ai/manual
    --browser chrome/firefox
    --env dev/qa/prod
"""
import argparse
import os
import logging
from dotenv import load_dotenv
from imports_manager import imports
from common.drivers.driver_factory import get_driver
from common.core.logger_setup import setup_logger

# Load environment variables
load_dotenv()
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "manual").lower()

setup_logger()

def parse_args():
    parser = argparse.ArgumentParser(description="Selenium AI+Manual Hybrid Runner")
    parser.add_argument("--mode", default=os.getenv("EXECUTION_MODE", "manual"), help="Execution mode: ai/manual")
    parser.add_argument("--browser", default=os.getenv("BROWSER", "chrome"), help="Browser: chrome/firefox")
    parser.add_argument("--env", default=os.getenv("ENV", "qa"), help="Target environment: dev/qa/prod")
    return parser.parse_args()

def main():
    args = parse_args()
    logging.info(f"🔧 Execution Mode: {args.mode}, Browser: {args.browser}, Env: {args.env}")
    driver = get_driver(browser=args.browser)
    executor = None

    if args.mode == "manual":
        from manual_execution.strategy.manual_strategy_executor import ManualStrategyExecutor
        executor = ManualStrategyExecutor(driver)
    elif args.mode == "ai":
        from ai_execution.strategy.ai_strategy_executor import AIStrategyExecutor
        executor = AIStrategyExecutor(driver)
    else:
        logging.error("❌ Invalid mode provided. Use 'manual' or 'ai'.")
        return

    executor.execute_flow()
    driver.quit()

if __name__ == "__main__":
    main()
