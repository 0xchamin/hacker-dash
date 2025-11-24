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
[green]Lovable for Terminal - Prompt-to-Product for the Terminal[/green]
"""


@app.command()
def generate(prompt: str, provider: str = None):
    """Generate a hacker dashboard from a prompt."""
    console.print(BANNER)

    # Get provider from flag or config
    if provider is None:
        cfg = config.get_config()
        provider = cfg.get("default_provider", "anthropic")
    
    try:
        api_key = config.get_api_key(provider)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        return
    
    with Status("[cyan]Initializing...[/cyan]", console=console, spinner="dots") as status:
        def update_status(msg):
            status.update(f"[cyan]{msg}[/cyan]")
        
        #code = brain.generate_dashboard(api_key, prompt, status_callback=update_status)
        code = brain.generate_dashboard(api_key, prompt, provider=provider, status_callback=update_status)
    
    #console.print("[green]✓[/green] Code generated. Launching dashboard...")
    console.print("[green]✓[/green] Code generated successfully!")
    console.print("[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]")
    console.print("[magenta]🚀 Launching dashboard...[/magenta]")

    #executor.run_dashboard(code, api_key, prompt)
    executor.run_dashboard(code, api_key, prompt, provider=provider)

@app.command(name="config")
def config_cmd():
    """Configure your API keys and default provider."""
    console.print("[cyan]═══ Hacker Dash Configuration ═══[/cyan]\n")
    
    # Ask for Anthropic key
    console.print("[green]Anthropic (Claude) API Key[/green]")
    console.print("[dim]Press Enter to skip if you don't have one[/dim]")
    anthropic_key = typer.prompt("API Key", default="", hide_input=True)
    
    # Ask for Gemini key
    console.print("\n[green]Google Gemini API Key[/green]")
    console.print("[dim]Press Enter to skip if you don't have one[/dim]")
    gemini_key = typer.prompt("API Key", default="", hide_input=True)
    
    # Validate at least one key provided
    if not anthropic_key and not gemini_key:
        console.print("[red]✗ You must provide at least one API key![/red]")
        return
    
    # Ask for default provider
    if anthropic_key and gemini_key:
        console.print("\n[cyan]Which provider should be the default?[/cyan]")
        console.print("1. Anthropic (Claude)")
        console.print("2. Google (Gemini)")
        choice = typer.prompt("Choice", default="1")
        default_provider = "anthropic" if choice == "1" else "gemini"
    elif anthropic_key:
        default_provider = "anthropic"
    else:
        default_provider = "gemini"
    
    config.save_config(
        anthropic_key=anthropic_key or None,
        gemini_key=gemini_key or None,
        default_provider=default_provider
    )
    
    console.print(f"\n[green]✓[/green] Configuration saved!")
    console.print(f"[green]✓[/green] Default provider: {default_provider}")


@app.command()
def stats():
    """View your inference statistics."""
    from . import brain
    import json
    
    if not brain.STATS_FILE.exists():
        console.print("[yellow]No stats yet. Generate some dashboards first![/yellow]")
        return
    
    stats_data = json.loads(brain.STATS_FILE.read_text())
    
    total_tokens = sum(s["total_tokens"] for s in stats_data)
    total_cost = sum(s["cost"] for s in stats_data)
    avg_latency = sum(s["latency"] for s in stats_data) / len(stats_data)
    
    console.print("\n[cyan]═══ HACKER DASH INFERENCE STATS ═══[/cyan]\n")
    console.print(f"[green]Total Generations:[/green] {len(stats_data)}")
    console.print(f"[green]Total Tokens:[/green] {total_tokens:,}")
    console.print(f"[green]Total Cost:[/green] ${total_cost:.4f}")
    console.print(f"[green]Avg Latency:[/green] {avg_latency:.2f}s\n")
    
    # Now generate a dashboard to visualize this
    console.print("[magenta]Generating stats dashboard...[/magenta]")
    
    api_key = config.get_api_key()
    code = brain.generate_dashboard(
        api_key, 
        f"Create a dashboard showing inference statistics: {len(stats_data)} calls, {total_tokens} tokens, ${total_cost:.4f} cost, {avg_latency:.2f}s avg latency"
    )
    executor.run_dashboard(code, api_key, "stats")


if __name__ == "__main__":
    app()


