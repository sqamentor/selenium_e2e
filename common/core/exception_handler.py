"""
exception_handler.py
---------------------
Provides unified exception handling decorators and custom exceptions.
"""

import logging
import functools

class ElementNotFoundException(Exception):
    pass

class PageLoadTimeoutException(Exception):
    pass

def exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ElementNotFoundException as e:
            logging.error(f"🔴 ElementNotFoundException: {e}")
            raise
        except PageLoadTimeoutException as e:
            logging.error(f"🔴 PageLoadTimeoutException: {e}")
            raise
        except Exception as e:
            logging.error(f"🔴 Unexpected Exception in {func.__name__}: {e}")
            raise
    return wrapper
