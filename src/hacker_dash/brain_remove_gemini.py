from anthropic import Anthropic
import google.generativeai as genai
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
3. IMPORTANT CSS RULES - Only use these valid Textual CSS properties:
   - background, color, border, padding, margin (integers only, no decimals)
   - width, height, text-align, text-style
   - DO NOT use: font-family, box-shadow, display: grid, align-items, or decimal values
4. Create a visually striking dashboard with panels, sparklines, or live data
5. Make it look like a movie hacker screen
6. Return ONLY executable Python code, no explanations
7. The script must be self-contained and runnable with `uv run`


Example structure:

/// script
dependencies = ["textual"]
///
from textual.app import App from textual.widgets import Static

class Dashboard(App): CSS = ''' Screen { background: #000; } Static { color: cyan; } '''

Copied!
def compose(self):
    yield Static("Hello Hacker")
if name == "main": Dashboard().run()


Now generate code for this request."""

FIX_PROMPT = """The following Python code crashed with an error. Fix the code and return ONLY the corrected Python code, no explanations.

ORIGINAL CODE:
{code}

ERROR:
{error}

Return the fixed code with the PEP 723 header intact."""


def generate_with_anthropic(api_key: str, prompt: str) -> tuple:
    """Generate using Claude."""
    client = Anthropic(api_key=api_key)
    start_time = time.time()
    
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    latency = time.time() - start_time
    return (
        message.content[0].text,
        message.usage.input_tokens,
        message.usage.output_tokens,
        latency
    )

def generate_with_gemini(api_key: str, prompt: str) -> tuple:
    """Generate using Gemini."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    start_time = time.time()
    response = model.generate_content(prompt)
    latency = time.time() - start_time
    
    # Gemini token counting
    prompt_tokens = model.count_tokens(prompt).total_tokens
    completion_tokens = model.count_tokens(response.text).total_tokens
    
    return (response.text, prompt_tokens, completion_tokens, latency)

def generate_dashboard(api_key: str, user_prompt: str, provider: str = "anthropic", status_callback=None) -> str:
    """Generate dashboard using specified provider."""
    
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
    
    prompt = f"{SYSTEM_PROMPT}\n\nUser request: {user_prompt}"
    
    # Call appropriate provider
    if provider == "gemini":
        code, prompt_tokens, completion_tokens, latency = generate_with_gemini(api_key, prompt)
    else:
        code, prompt_tokens, completion_tokens, latency = generate_with_anthropic(api_key, prompt)
    
    log_inference(prompt_tokens, completion_tokens, latency)
    
    # Strip markdown code fences
    code = re.sub(r'^```python\s*\n', '', code)
    code = re.sub(r'\n```\s*$', '', code)
    
    return code
# def generate_dashboard(api_key: str, user_prompt: str, status_callback=None) -> str:
#     client = Anthropic(api_key=api_key)
    
#     messages_sequence = [
#         "Analyzing system entropy...",
#         "Injecting cyberpunk CSS...",
#         "Compiling matrix widgets...",
#         "Generating dashboard code..."
#     ]
    
#     for msg in messages_sequence:
#         if status_callback:
#             status_callback(msg)
#         time.sleep(0.3)
    
#     message = client.messages.create(
#         model="claude-sonnet-4-5-20250929",
#         max_tokens=2000,
#         messages=[
#             {
#                 "role": "user",
#                 "content": f"{SYSTEM_PROMPT}\n\nUser request: {user_prompt}"
#             }
#         ]
#     )
    
#     code = message.content[0].text
    
#     # Strip markdown code fences
#     code = re.sub(r'^```python\s*\n', '', code)
#     code = re.sub(r'\n```\s*$', '', code)
    
#     return code

def fix_dashboard(api_key: str, broken_code: str, error_message: str, provider: str = "anthropic") -> str:
    """Fix broken dashboard code using specified provider."""
    
    prompt = FIX_PROMPT.format(code=broken_code, error=error_message)
    
    if provider == "gemini":
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        code = response.text
    else:
        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        code = message.content[0].text
    
    # Strip markdown code fences
    code = re.sub(r'^```python\s*\n', '', code)
    code = re.sub(r'\n```\s*$', '', code)
    
    return code



def generate_dashboard_old(api_key: str, user_prompt: str, status_callback=None) -> str:
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

    # Track inference timing
    start_time = time.time()
    
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"{SYSTEM_PROMPT}\n\nUser request: {user_prompt}"
            }
        ]
    )

    latency = time.time() - start_time

    # Log the inference stats
    log_inference(
        prompt_tokens=message.usage.input_tokens,
        completion_tokens=message.usage.output_tokens,
        latency=latency
    )
    
    code = message.content[0].text
    
    # Strip markdown code fences
    code = re.sub(r'^```python\s*\n', '', code)
    code = re.sub(r'\n```\s*$', '', code)
    
    return code

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
        "cost": (prompt_tokens * 0.003 + completion_tokens * 0.015) / 1000  # Claude pricing
    })
    
    STATS_FILE.write_text(json.dumps(stats[-100:]))  # Keep last 100
