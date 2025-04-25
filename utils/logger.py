# utils/logger.py
import logging

def setup_logger(name='selenium_e2e', log_file='logs/automation.log'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
