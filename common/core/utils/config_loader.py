import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def get_env_browser():
    return os.getenv("BROWSER", "chrome").lower()

def get_yaml_config(path="config/settings.yaml"):
    if os.path.exists(path):
        with open(path, 'r') as file:
            return yaml.safe_load(file)
    return {}
