import os
import sys

def ensure_project_root_in_sys_path(relative_levels_up=4, print_debug=True):
    """
    Ensures that the project root is in sys.path for clean module imports.
    Typically called at the top of every script.
    """
    current_file_path = os.path.abspath(__file__)
    for _ in range(relative_levels_up):
        current_file_path = os.path.dirname(current_file_path)
    
    project_root = os.path.abspath(current_file_path)

    if project_root not in sys.path:
        if print_debug:
            print(f"[INFO] Adding {project_root} to sys.path")
        sys.path.insert(0, project_root)
    elif print_debug:
        print(f"[INFO] Project root already in sys.path")

    if print_debug:
        print("\n[DEBUG] sys.path:")
        for p in sys.path:
            print("   ", p)
