import pytest
from utils.human_actions import random_mouse_movement, human_scroll

@pytest.fixture(scope="function")
def simulate_human_behavior(request):
    """
    Automatically triggers mouse movement + scroll at the beginning of any test
    or page form interaction when this fixture is used.
    """
    driver = request.getfixturevalue("browser")  # assumes a fixture named 'browser' is used
    random_mouse_movement(driver)
    human_scroll(driver)
    return True
