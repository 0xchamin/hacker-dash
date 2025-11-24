import subprocess
import tempfile
from pathlib import Path
from rich.console import Console

console = Console()
MAX_RETRIES = 2

def run_dashboard(code: str, api_key: str, user_prompt: str, retry_count: int = 0):
    from . import brain
    
    # Write code to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = Path(f.name)
    
    try:
        # Try running without capture first (for TUI apps to control terminal)
        result = subprocess.run(
            ["uv", "run", str(temp_file)]
        )
        
        # If it failed, re-run with capture to get the error for self-healing
        if result.returncode != 0:
            console.print(f"[yellow]⚠ Dashboard crashed. Capturing error...[/yellow]")
            
            result = subprocess.run(
                ["uv", "run", str(temp_file)],
                capture_output=False,
                text=True
            )
            
            if retry_count < MAX_RETRIES:
                console.print(f"[yellow]Self-healing (attempt {retry_count + 1}/{MAX_RETRIES})...[/yellow]")
                
                # Get fixed code from brain
                fixed_code = brain.fix_dashboard(api_key, code, result.stderr)
                
                # Retry with fixed code
                run_dashboard(fixed_code, api_key, user_prompt, retry_count + 1)
            else:
                console.print(f"[red]✗ Failed after {MAX_RETRIES} attempts.[/red]")
                console.print(f"[red]Error:[/red]\n{result.stderr}")
    
    finally:
        if temp_file.exists():
            temp_file.unlink()
