import typer
from rich.console import Console
from rich.status import Status
from . import config, brain, executor

app = typer.Typer()
console = Console()

BANNER = """
[cyan]
██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗     ██████╗  █████╗ ███████╗██╗  ██╗
██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗    ██╔══██╗██╔══██╗██╔════╝██║  ██║
███████║███████║██║     █████╔╝ █████╗  ██████╔╝    ██║  ██║███████║███████╗███████║
██╔══██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗    ██║  ██║██╔══██║╚════██║██╔══██║
██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║    ██████╔╝██║  ██║███████║██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
[/cyan]
[green]╔══════════════════════════════════════════════════════════════════╗[/green]
[green]║  Lovable for Terminal - Prompt-to-Product for the Terminal  ║[/green]
[green]╚══════════════════════════════════════════════════════════════════╝[/green]

"""

@app.command()
def generate(prompt: str):
    """Generate a hacker dashboard from a prompt."""
    console.print(BANNER)
    
    try:
        api_key = config.get_api_key()
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return
    
    with Status("[cyan]Initializing...[/cyan]", console=console, spinner="dots") as status:
        def update_status(msg):
            status.update(f"[cyan]{msg}[/cyan]")
        
        code = brain.generate_dashboard(api_key, prompt, status_callback=update_status)
    
    console.print("[green]✓[/green] Code generated successfully!")
    console.print("[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]")
    console.print("[magenta]🚀 Launching dashboard...[/magenta]")
    
    executor.run_dashboard(code, api_key, prompt)

@app.command(name="config")
def config_cmd():
    """Configure your Anthropic API key."""
    console.print("[cyan]Enter your Anthropic API key:[/cyan]")
    key = typer.prompt("API Key", hide_input=True)
    config.save_api_key(key)
    console.print("[green]✓[/green] API key saved successfully!")

if __name__ == "__main__":
    app()
