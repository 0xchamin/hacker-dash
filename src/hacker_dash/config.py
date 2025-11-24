import os
from pathlib import Path
from dotenv import load_dotenv
from platformdirs import user_config_dir

load_dotenv()

CONFIG_DIR = Path(user_config_dir("hacker-dash"))
CONFIG_FILE = CONFIG_DIR / "config.env"

def get_api_key() -> str:
    # Check environment variable first
    key = os.getenv("ANTHROPIC_API_KEY")
    if key:
        return key
    
    # Check config file
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            for line in f:
                if line.startswith("ANTHROPIC_API_KEY="):
                    return line.split("=", 1)[1].strip()
    
    raise ValueError("No API key found. Run 'hacker-dash config' to set it up.")

def save_api_key(key: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write(f"ANTHROPIC_API_KEY={key}\n")
