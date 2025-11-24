# /// script
# dependencies = ["textual", "psutil"]
# ///

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Label
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
import psutil
import random
from datetime import datetime

class SnowFlake(Static):
    position = reactive(0)
    column = reactive(0)
    
    def __init__(self, col: int):
        super().__init__("❄")
        self.column = col
        self.position = random.randint(-10, 0)
    
    def on_mount(self) -> None:
        self.set_interval(0.2, self.fall)
    
    def fall(self) -> None:
        self.position += 1
        if self.position > 50:
            self.position = -2
            self.column = random.randint(0, 95)
        self.styles.offset = (self.column, self.position)

class CPUStats(Static):
    cpu_percent = reactive(0.0)
    
    def on_mount(self) -> None:
        self.update_stats()
        self.set_interval(1, self.update_stats)
    
    def update_stats(self) -> None:
        self.cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        
        bars = int(self.cpu_percent / 5)
        bar_display = "█" * bars + "░" * (20 - bars)
        
        self.update(f"""
╔═══════════════════════════════════════════════╗
║           🏢 CPU MONITORING SYSTEM           ║
╠═══════════════════════════════════════════════╣
║                                               ║
║  Usage: {self.cpu_percent:5.1f}%  {bar_display}  ║
║                                               ║
║  Cores: {cpu_count}                                   ║
║  Freq:  {cpu_freq.current if cpu_freq else 0:.0f} MHz                         ║
║                                               ║
╚═══════════════════════════════════════════════╝
        """)

class RAMStats(Static):
    ram_percent = reactive(0.0)
    
    def on_mount(self) -> None:
        self.update_stats()
        self.set_interval(1, self.update_stats)
    
    def update_stats(self) -> None:
        mem = psutil.virtual_memory()
        self.ram_percent = mem.percent
        
        bars = int(self.ram_percent / 5)
        bar_display = "█" * bars + "░" * (20 - bars)
        
        used_gb = mem.used / (1024 ** 3)
        total_gb = mem.total / (1024 ** 3)
        
        self.update(f"""
╔═══════════════════════════════════════════════╗
║          💾 MEMORY MONITORING SYSTEM         ║
╠═══════════════════════════════════════════════╣
║                                               ║
║  Usage: {self.ram_percent:5.1f}%  {bar_display}  ║
║                                               ║
║  Used:  {used_gb:5.2f} GB / {total_gb:.2f} GB             ║
║  Free:  {mem.available / (1024 ** 3):5.2f} GB                           ║
║                                               ║
╚═══════════════════════════════════════════════╝
        """)

class SystemClock(Static):
    def on_mount(self) -> None:
        self.update_time()
        self.set_interval(1, self.update_time)
    
    def update_time(self) -> None:
        now = datetime.now()
        self.update(f"🌃 NYC TOWER CONTROL | {now.strftime('%H:%M:%S')} | {now.strftime('%Y-%m-%d')}")


# Injected stats widget
class StatsPanel(Static):
    """Display API usage statistics."""
    
    def __init__(self):
        stats_text = f"""[cyan]╔═══ API STATS ═══╗[/cyan]
[green]Calls:[/green] 59
[green]Tokens:[/green] 125,395
[green]Cost:[/green] $1.6877
[green]Latency:[/green] 26.51s
[cyan]╚═════════════════╝[/cyan]"""
        super().__init__(stats_text)

class Dashboard(App):
    CSS = """
    Screen {
        background: #0a1929;
        layers: base snow;
    }
    
    Header {
        background: #1a2942;
        color: #64b5f6;
        text-style: bold;
        border: solid #42a5f5;
    }
    
    Footer {
        background: #1a2942;
        color: #90caf9;
        border: solid #42a5f5;
    }
    
    #snow_container {
        width: 100%;
        height: 100%;
        layer: snow;
    }
    
    .snowflake {
        color: #e3f2fd;
        background: transparent;
        width: 1;
        height: 1;
        layer: snow;
    }
    
    #main_container {
        width: 100%;
        height: 100%;
        align: center middle;
        layer: base;
    }
    
    #clock {
        dock: top;
        height: 3;
        content-align: center middle;
        background: #0d47a1;
        color: #bbdefb;
        text-style: bold;
        border: heavy #1976d2;
        margin: 1;
    }
    
    #stats_container {
        width: auto;
        height: auto;
        align: center middle;
    }
    
    CPUStats {
        width: 51;
        height: 12;
        background: #102840;
        color: #4fc3f7;
        text-style: bold;
        border: heavy #1e88e5;
        margin: 1;
    }
    
    RAMStats {
        width: 51;
        height: 12;
        background: #102840;
        color: #29b6f6;
        text-style: bold;
        border: heavy #1e88e5;
        margin: 1;
    }
    
    #title {
        height: 7;
        content-align: center middle;
        color: #81d4fa;
        text-style: bold;
        margin-bottom: 1;
    }
    """
    
    TITLE = "NYC SKYSCRAPER MONITORING"
    
    def compose(self) -> ComposeResult:
        yield StatsPanel()
        yield Header()
        
        with Container(id="snow_container"):
            for _ in range(40):
                flake = SnowFlake(random.randint(0, 95))
                flake.add_class("snowflake")
                yield flake
        
        with Vertical(id="main_container"):
            yield SystemClock(id="clock")
            
            yield Static("""
    ╔═══════════════════════════════════════════════╗
    ║   🏙️  NEW YORK SKYSCRAPER CONTROL CENTER  🏙️  ║
    ║        ▀▄▀▄ SYSTEM DIAGNOSTICS ▄▀▄▀         ║
    ╚═══════════════════════════════════════════════╝
            """, id="title")
            
            with Vertical(id="stats_container"):
                yield CPUStats()
                yield RAMStats()
        
        yield Footer()

if __name__ == "__main__":
    app = Dashboard()
    app.run()