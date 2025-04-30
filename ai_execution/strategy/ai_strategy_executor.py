"""
ai_strategy_executor.py
-----------------------
Executes the AI-powered automation flow.
"""

import logging
from ai_execution.flows.booking_flow import AIBookingFlow

class AIStrategyExecutor:
    def __init__(self, driver):
        self.driver = driver

    def execute_flow(self):
        logging.info("🧠 Starting AI Booking Flow...")
        flow = AIBookingFlow(self.driver)
        flow.run()
