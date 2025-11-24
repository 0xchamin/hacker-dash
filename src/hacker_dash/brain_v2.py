from anthropic import Anthropic
import re
import time
import json
from pathlib import Path

STATS_FILE = Path.home() / ".hacker-dash-stats.json"

SYSTEM_PROMPT = """You are a code generator for terminal dashboards. Generate a single Python script using the Textual library.

REQUIREMENTS:
1. Start with PEP 723 inline script metadata:
   # /// script
   # dependencies = ["textual", "psutil"]
   # ///

2. Use Textual's CSS to apply a CYBERPUNK theme (neon colors: cyan, magenta, green)
3. Create a visually striking dashboard with panels, sparklines, or live data
4. Make it look like a movie hacker screen
5. Return ONLY executable Python code, no explanations
6. The script must be self-contained and runnable with `uv run`

Example structure:

// script
dependencies = ["textual"]
///
from textual.app import App from textual.widgets import Static

class Dashboard(App): CSS = ''' Screen { background: #000; } Static { color: cyan; } '''

Copied!
def compose(self):
    yield Static("Hello Hacker")
if name == "main": Dashboard().run()

Copied!


Now generate code for this request."""

FIX_PROMPT = """The following Python code crashed with an error. Fix the code and return ONLY the corrected Python code, no explanations.

ORIGINAL CODE:
{code}

ERROR:
{error}

Return the fixed code with the PEP 723 header intact."""

def log_inference(prompt_tokens: int, completion_tokens: int, latency: float):
    stats = []
    if STATS_FILE.exists():
        stats = json.loads(STATS_FILE.read_text())
    
    stats.append({
        "timestamp": time.time(),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "latency": latency,
        "cost": (prompt_tokens * 0.003 + completion_tokens * 0.015) / 1000
    })
    
    STATS_FILE.write_text(json.dumps(stats[-100:]))

def generate_dashboard(api_key: str, user_prompt: str, status_callback=None) -> str:
    client = Anthropic(api_key=api_key)
    
    messages_sequence = [
        ("Initializing neural matrix...", 0.4),
        ("Scanning system entropy...", 0.3),
        ("Injecting cyberpunk CSS...", 0.5),
        ("Compiling holographic widgets...", 0.4),
        ("Optimizing neon shaders...", 0.3),
        ("Generating dashboard code...", 0.6),
    ]
    
    for msg, delay in messages_sequence:
        if status_callback:
            status_callback(msg)
        time.sleep(delay)
    
    start_time = time.time()
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"{SYSTEM_PROMPT}\n\nUser request: {user_prompt}"
            }
        ]
    )
    
    latency = time.time() - start_time
    
    log_inference(
        prompt_tokens=message.usage.input_tokens,
        completion_tokens=message.usage.output_tokens,
        latency=latency
    )
    
    code = message.content[0].text
    
    code = re.sub(r'^```python\s*\n', '', code)
    code = re.sub(r'\n```\s*$', '', code)
    
    return code

def fix_dashboard(api_key: str, broken_code: str, error_message: str) -> str:
    client = Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": FIX_PROMPT.format(code=broken_code, error=error_message)
            }
        ]
    )
    
    code = message.content[0].text
    
    code = re.sub(r'^```python\s*\n', '', code)
    code = re.sub(r'\n```\s*$', '', code)
    
    return code
