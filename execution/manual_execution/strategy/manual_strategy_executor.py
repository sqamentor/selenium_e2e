"""
manual_strategy_executor.py
---------------------------
Executes the manual automation flow.
"""

import logging
from manual_execution.flows.booking_flow import ManualBookingFlow

class ManualStrategyExecutor:
    def __init__(self, driver):
        self.driver = driver

    def execute_flow(self):
        logging.info("🚀 Starting Manual Booking Flow...")
        flow = ManualBookingFlow(self.driver)
        flow.run()
