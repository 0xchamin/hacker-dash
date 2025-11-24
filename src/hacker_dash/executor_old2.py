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
        # Run with uv
        console.print(f"[dim]Running: {temp_file}[/dim]")
        console.print(f"[dim]Code preview:\n{code[:200]}...[/dim]")

        result = subprocess.run(
            ["uv", "run", str(temp_file)],
            capture_output=False,
            text=True
        )
        console.print(f"[dim]Exit code: {result.returncode}[/dim]")
        if result.stdout:
            console.print(f"[dim]Output: {result.stdout}[/dim]")
        if result.stderr:
            console.print(f"[dim]Stderr: {result.stderr}[/dim]")

        
        if result.returncode != 0 and retry_count < MAX_RETRIES:
            console.print(f"[yellow]⚠ Dashboard crashed. Self-healing (attempt {retry_count + 1}/{MAX_RETRIES})...[/yellow]")
            
            # Get fixed code from brain
            fixed_code = brain.fix_dashboard(api_key, code, result.stderr)
            
            # Retry with fixed code
            run_dashboard(fixed_code, api_key, user_prompt, retry_count + 1)
        elif result.returncode != 0:
            console.print(f"[red]✗ Failed after {MAX_RETRIES} attempts.[/red]")
            console.print(f"[red]Error:[/red]\n{result.stderr}")
        else:
            # Success - show any output
            if result.stdout:
                console.print(result.stdout)
    
    finally:
        if temp_file.exists():
            temp_file.unlink()
