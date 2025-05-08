"""
auto_importer.py
----------------
Smart dynamic importer for Python projects.

✔ Automatically detects project root (multi-strategy).
✔ Dynamically adds project root to sys.path.
✔ Allows importing modules from any location using dot-paths.
✔ Gracefully handles missing imports.
✔ Fallback-safe with multiple detection mechanisms.
"""

import importlib
import sys
import os
import pathlib
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def detect_project_root():
    """
    Tries all known strategies to detect the project root:
    - .git directory
    - pyproject.toml
    - requirements.txt
    - auto_importer.py (fallback)
    - Parent traversal (fixed depth fallback)
    """
    current_file = pathlib.Path(__file__).resolve()
    indicators = [".git", "pyproject.toml", "requirements.txt", "auto_importer.py"]

    # Strategy 1: Marker-based root detection
    for parent in current_file.parents:
        for marker in indicators:
            if (parent / marker).exists():
                _add_to_sys_path(str(parent))
                return str(parent)

    # Strategy 2: Depth-based fallback (auto_importer.py is usually 4-5 levels deep)
    try:
        fallback_root = str(current_file.parents[4])
        _add_to_sys_path(fallback_root)
        return fallback_root
    except IndexError:
        pass

    raise RuntimeError("❌ Could not detect project root using known strategies.")


def _add_to_sys_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)
        logging.info(f"✅ Project root added to sys.path: {path}")


# Detect and store root
PROJECT_ROOT = detect_project_root()


def smart_import(dot_path):
    """
    Dynamically import a module or attribute by dot notation.
    Example:
        smart_import("package.module.ClassName")

    Returns:
        Imported module or object, or None if not found.
    """
    try:
        module_path, _, attr = dot_path.rpartition(".")
        if not module_path:
            return importlib.import_module(dot_path)

        mod = importlib.import_module(module_path)
        return getattr(mod, attr)
    except ModuleNotFoundError as e:
        logging.error(f"❌ ModuleNotFoundError: {e}")
    except AttributeError as e:
        logging.error(f"❌ AttributeError: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected import error: {e}")
    return None
