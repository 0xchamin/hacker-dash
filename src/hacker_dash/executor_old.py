import subprocess
import tempfile
from pathlib import Path
from rich.console import Console
from . import brain

console = Console()
MAX_RETRIES = 2

def run_dashboard(code: str, retry_count: int = 0):
    # Write code to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = Path(f.name)
    
    try:
        # Run with uv
        result = subprocess.run(
            ["uv", "run", str(temp_file)],
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0 and retry_count < MAX_RETRIES:
            console.print(f"[yellow]Dashboard crashed. Attempting self-heal (attempt {retry_count + 1}/{MAX_RETRIES})...[/yellow]")
            # Note: Self-healing requires passing error back to brain - simplified for now
            console.print("[red]Self-healing not yet implemented. Check the generated code.[/red]")
    
    finally:
        temp_file.unlink()
