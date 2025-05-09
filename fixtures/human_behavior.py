import pytest
import random
import time
from utils.human_actions import (
    random_mouse_movement,
    human_scroll_behavior,
    human_type,
    human_click,
    random_page_interaction,
    simulate_idle
)

@pytest.fixture(scope="function")
def simulate_human_behavior(request):
    """
    Automatically triggers human-like behavior (mouse movement, scrolling, typing, etc.)
    at the beginning of any test or page form interaction when this fixture is used.
    """
    driver = request.getfixturevalue("browser")  # assumes a fixture named 'browser' is used

    # Simulate random mouse movement
    random_mouse_movement(driver)

    # Perform human-like scrolling
    human_scroll_behavior(driver)

    # Perform random page interactions (e.g., clicking checkboxes, dropdowns)
    random_page_interaction(driver)

    # Simulate idle time to mimic natural pauses
    simulate_idle(driver)

    return driver
