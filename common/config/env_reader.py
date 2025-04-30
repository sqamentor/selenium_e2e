"""
env_reader.py
--------------
Loads environment variables and YAML config files dynamically based on target ENV.
"""

import yaml
import os

def load_config():
    env = os.getenv("ENV", "qa").lower()
    config_path = f"common/config/config_{env}.yaml"

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config
