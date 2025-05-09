# utils/sys_path_helper.py

import sys
import os

def add_project_root(levels_up=1):
    """
    Adds the project root to sys.path dynamically.

    Args:
        levels_up (int): How many folders up to go from the current file.
    """
    caller_file = os.path.abspath(__file__)
    for _ in range(levels_up):
        caller_file = os.path.abspath(os.path.join(caller_file, '..'))
    project_root = os.path.abspath(caller_file)

    if project_root not in sys.path:
        sys.path.insert(0, project_root)
