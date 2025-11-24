from anthropic import Anthropic
import re

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
/// script
dependencies = ["textual"]
///
from textual.app import App from textual.widgets import Static

class Dashboard(App): CSS = ''' Screen { background: #000; } Static { color: cyan; } '''

    def compose(self):
        yield Static("Hello Hacker")
if name == "main": Dashboard().run()


Now generate code for this request."""

def generate_dashboard(api_key: str, user_prompt: str) -> str:
    client = Anthropic(api_key=api_key)
    
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
    
    code = message.content[0].text
    
    # Strip markdown code fences
    code = re.sub(r'^```python\s*\n', '', code)
    code = re.sub(r'\n```\s*$', '', code)
    
    return code

