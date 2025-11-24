import subprocess
import tempfile
from pathlib import Path
from rich.console import Console
from . import injector

console = Console()
MAX_RETRIES = 2

def run_dashboard(code: str, api_key: str, user_prompt: str, retry_count: int = 0):
    from . import brain
    
    # Inject stats panel into the code
    code = injector.inject_stats_panel(code)
    
    # Debug save
    Path("debug_injected.py").write_text(code)
    console.print("[dim]Injected code saved to debug_injected.py[/dim]")
    
    # Write code to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = Path(f.name)
    
    try:
        # Try running without capture first
        result = subprocess.run(
            ["uv", "run", str(temp_file)]
        )
        
        # If it failed, re-run with capture to get the error
        if result.returncode != 0:
            console.print(f"[yellow]⚠ Dashboard crashed. Capturing error...[/yellow]")
            
            result = subprocess.run(
                ["uv", "run", str(temp_file)],
                capture_output=True,
                text=True
            )
            
            if retry_count < MAX_RETRIES:
                console.print(f"[yellow]Self-healing (attempt {retry_count + 1}/{MAX_RETRIES})...[/yellow]")
                
                fixed_code = brain.fix_dashboard(api_key, code, result.stderr)
                run_dashboard(fixed_code, api_key, user_prompt, retry_count + 1)
            else:
                console.print(f"[red]✗ Failed after {MAX_RETRIES} attempts.[/red]")
                console.print(f"[red]Error:[/red]\n{result.stderr}")
    
    finally:
        if temp_file.exists():
            temp_file.unlink()
