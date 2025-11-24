import re
import json
from pathlib import Path

STATS_FILE = Path.home() / ".hacker-dash-stats.json"

def inject_stats_panel(code: str) -> str:
    """Inject a stats panel into generated Textual code."""
    
    # Load stats
    stats_data = []
    if STATS_FILE.exists():
        stats_data = json.loads(STATS_FILE.read_text())
    
    total_calls = len(stats_data)
    total_tokens = sum(s["total_tokens"] for s in stats_data) if stats_data else 0
    total_cost = sum(s["cost"] for s in stats_data) if stats_data else 0
    avg_latency = (sum(s["latency"] for s in stats_data) / len(stats_data)) if stats_data else 0
    
    stats_widget = f'''
# Injected stats widget
class StatsPanel(Static):
    """Display API usage statistics."""
    
    def __init__(self):
        stats_text = f"""[cyan]╔═══ API STATS ═══╗[/cyan]
[green]Calls:[/green] {total_calls}
[green]Tokens:[/green] {total_tokens:,}
[green]Cost:[/green] ${total_cost:.4f}
[green]Latency:[/green] {avg_latency:.2f}s
[cyan]╚═════════════════╝[/cyan]"""
        super().__init__(stats_text)
'''
    
    # Find the imports section and add Static if not present
    if "from textual.widgets import" in code:
        # Add Static to existing imports
        code = re.sub(
            r'(from textual\.widgets import [^)]+)',
            r'\1, Static',
            code
        )
        # Remove duplicate if it was already there
        code = re.sub(r'Static,\s*Static', 'Static', code)
    else:
        # Add new import line after textual.app import
        code = re.sub(
            r'(from textual\.app import [^\n]+\n)',
            r'\1from textual.widgets import Static\n',
            code
        )
    
    # Find the Dashboard class and inject stats widget before it
    code = re.sub(
        r'(class \w+\(App\):)',
        f'{stats_widget}\n\\1',
        code
    )
    
    # Find the compose method and add stats panel
    # Look for "def compose(self):" and inject after the first yield or at the start
    #compose_pattern = r'(def compose\(self\):.*?)(yield )'
    if "yield Header()" in code:
        code = code.replace("yield Header()", "yield StatsPanel()\n        yield Header()")
    elif "def compose(self)" in code:
        # Fallback: add after compose definition
        code = re.sub(
            r'(def compose\(self\).*?:)\n',
            r'\1\n        yield StatsPanel()\n',
            code,
            flags=re.DOTALL
        )
    return code
