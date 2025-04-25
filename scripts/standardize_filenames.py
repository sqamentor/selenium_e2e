# scripts/standardize_filenames.py
import os, re

def to_snake_case(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower().replace('.py', '')

base_dir = "pages"
for file in os.listdir(base_dir):
    if file.endswith(".py") and not file.startswith("__"):
        new_name = to_snake_case(file) + ".py"
        os.rename(os.path.join(base_dir, file), os.path.join(base_dir, new_name))
        print(f"Renamed: {file} → {new_name}")
