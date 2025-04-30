import sys, os

current = os.path.dirname(__file__)
root = os.path.abspath(os.path.join(current, '..'))  # Adjust levels here only if necessary

if root not in sys.path:
    sys.path.insert(0, root)

from imports_manager import imports


print("✅ Successfully imported imports_manager.")
