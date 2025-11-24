import os
from pathlib import Path
from dotenv import load_dotenv
from platformdirs import user_config_dir
import json

load_dotenv()

CONFIG_DIR = Path(user_config_dir("hacker-dash"))
CONFIG_FILE = CONFIG_DIR / "config.json"

def get_config() -> dict:
    """Load config from file."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def get_api_key(provider: str = None) -> str:
    """Get API key for specified provider."""
    config = get_config()
    
    # Determine which provider to use
    if provider is None:
        provider = config.get("default_provider", "anthropic")
    
    # Check environment variable first
    env_var = f"{provider.upper()}_API_KEY"
    key = os.getenv(env_var)
    if key:
        return key
    
    # Check config file
    key = config.get(f"{provider}_api_key")
    if key:
        return key
    
    raise ValueError(f"No API key found for {provider}. Run 'hacker-dash config' to set it up.")

def save_config(anthropic_key: str = None, gemini_key: str = None, default_provider: str = None):
    """Save API keys and default provider."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    config = get_config()
    
    if anthropic_key:
        config["anthropic_api_key"] = anthropic_key
    if gemini_key:
        config["gemini_api_key"] = gemini_key
    if default_provider:
        config["default_provider"] = default_provider
    
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
