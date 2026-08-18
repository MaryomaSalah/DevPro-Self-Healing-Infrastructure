import psutil
import time
import subprocess
import platform
from datetime import datetime

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box

import matplotlib
matplotlib.use("Agg")  # render to file, no GUI backend needed
import matplotlib.pyplot as plt

console = Console()

# ---------- History tracking ----------
history_time = []
history_cpu = []
history_mem = []
start_time = time.time()

# ---------- Visual helpers ----------

def status_color(percent):
    """Return a color name based on usage severity."""
    if percent < 50:
        return "green"
    elif percent < 80:
        return "yellow"
    else:
        return "red"

def status_label(percent):
    if percent < 50:
        return "NORMAL"
    elif percent < 80:
        return "MODERATE"
    else:
        return "HIGH"

def make_bar(percent, width=34):
    """Build a colored Rich Text progress bar."""
    color = status_color(percent)
    filled = int(width * percent / 100)
    bar = Text()
    bar.append("█" * filled, style=color)
    bar.append("░" * (width - filled), style="grey35")
    return bar

def metric_row(label, percent, extra=""):
    """One row: label | bar | percent | status badge"""
    row = Table.grid(expand=True, padding=(0, 1))
    row.add_column(width=14)          # label
    row.add_column(ratio=1)           # bar
    row.add_column(width=8, justify="right")   # percent
    row.add_column(width=10, justify="right")  # status

    color = status_color(percent)
    percent_text = Text(f"{percent:5.1f}%", style=f"bold {color}")
    status_text = Text(status_label(percent), style=f"bold {color}")

    row.add_row(Text(label, style="bold white"), make_bar(percent), percent_text, status_text)
    return row

# ---------- Frame builder ----------

def build_dashboard():
    cpu_percent = psutil.cpu_percent(interval=1)   # 1-second sample
    memory = psutil.virtual_memory()
    now = datetime.now().strftime("%H:%M:%S")

    # Record history for the end-of-session chart
    history_time.append(time.time() - start_time)
    history_cpu.append(cpu_percent)
    history_mem.append(memory.percent)

    # Header
    header = Table.grid(expand=True)
    header.add_column(justify="left")
    header.add_column(justify="right")
    header.add_row(
        Text(" DEV PRO - Monitor", style="bold cyan"),
        Text(f"{now} ", style="dim white"),
    )

    # Metric rows
    cpu_row = metric_row("CPU Usage", cpu_percent)
    mem_row = metric_row("Memory Usage", memory.percent)

    metrics_block = Table.grid(expand=True, padding=(1, 0, 0, 0))
    metrics_block.add_row(cpu_row)
    metrics_block.add_row(mem_row)

    # Footer stats
    footer = Table.grid(expand=True, padding=(0, 1))
    footer.add_column(ratio=1)
    footer.add_column(ratio=1)
    footer.add_row(
        Text(f"Memory   {memory.used / (1024**3):.2f} GB / {memory.total / (1024**3):.2f} GB", style="dim white"),
        Align.right(Text(f"CPU Cores  {psutil.cpu_count(logical=True)}", style="dim white")),
    )

    overall_color = status_color(max(cpu_percent, memory.percent))

    body = Group(
        header,
        Text(""),
        metrics_block,
        Text(""),
        Text("─" * 60, style="grey35"),
        footer,
    )

    return Panel(
        body,
        title="[bold white] System Status [/bold white]",
        subtitle="[dim]Ctrl+C to stop[/dim]",
        border_style=overall_color,
        box=box.ROUNDED,
        padding=(1, 2),
    )

# ---------- Chart generation ----------

def save_usage_chart(filename="usage_chart.png"):
    """Plot CPU & Memory usage over the session and save as a PNG."""
    if len(history_time) < 2:
        console.print("[yellow]Not enough data collected to draw a chart.[/yellow]")
        return None

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(history_time, history_cpu, label="CPU %", color="#5dd8ff", linewidth=2)
    ax.plot(history_time, history_mem, label="Memory %", color="#a5ff5d", linewidth=2)

    ax.fill_between(history_time, history_cpu, alpha=0.15, color="#5dd8ff")
    ax.fill_between(history_time, history_mem, alpha=0.15, color="#a5ff5d")

    ax.axhline(80, color="#ff5d5d", linestyle="--", linewidth=1, alpha=0.6, label="High threshold (80%)")

    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Usage (%)")
    ax.set_ylim(0, 100)
    ax.set_title("System Usage Over Session", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", framealpha=0.3)
    ax.grid(alpha=0.2)

    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    return filename

def open_file(path):
    """Open the chart automatically depending on OS."""
    try:
        if platform.system() == "Darwin":
            subprocess.run(["open", path])
        elif platform.system() == "Windows":
            subprocess.run(["start", path], shell=True)
        else:
            subprocess.run(["xdg-open", path])
    except Exception:
        pass  # opening is a convenience, not critical

# ---------- Main loop ----------

def main():
    try:
        with Live(build_dashboard(), console=console, screen=False, refresh_per_second=4) as live:
            while True:
                live.update(build_dashboard())
    except KeyboardInterrupt:
        console.print("\n[bold red]Monitoring stopped.[/bold red]")
        chart_path = save_usage_chart()
        if chart_path:
            console.print(f"[bold green]Usage chart saved:[/bold green] {chart_path}")
            open_file(chart_path)

if __name__ == "__main__":
    main()