# utils/retry_utils.py
# Smart Retry with Loader Waiting

import functools
import time
import logging

from selenium_utils.BrowserUtils.loader_utils import wait_for_loader_to_disappear

def smart_retry(exceptions, tries=3, delay=1, backoff=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mtries, mdelay = tries, delay
            driver = kwargs.get("driver") or (args[0] if args else None)

            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logging.warning(f"[SMART RETRY] {func.__name__} failed with {e}, retrying after loaders clear and {mdelay}s wait...")

                    if driver:
                        try:
                            wait_for_loader_to_disappear(driver)
                        except Exception as loader_err:
                            logging.warning(f"[SMART RETRY] Loader check failed: {loader_err}")

                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff

            return func(*args, **kwargs)
        return wrapper
    return decorator
