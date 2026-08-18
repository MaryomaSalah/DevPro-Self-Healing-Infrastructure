import argparse
import multiprocessing
import random
import time
from collections import deque
from datetime import datetime

import psutil
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

# ---------- Flavor log pools (picked based on current CPU level) ----------

FLAVOR_LOW = [
    "System nominal. Initializing load generation...",
    "Worker processes online, ramping up gradually...",
    "Baseline load established across all cores...",
]
FLAVOR_MED = [
    "CPU utilization increasing across allocated cores...",
    "Scheduler queue depth rising under sustained load...",
    "Resource consumption trending upward...",
]
FLAVOR_HIGH = [
    "Warning: CPU utilization approaching critical threshold.",
    "Warning: Elevated contention detected on host resources.",
    "Warning: Response latency degrading under current load.",
]
FLAVOR_CRIT = [
    "Critical: CPU saturation threshold exceeded.",
    "Critical: Sustained high load — failure condition simulated.",
    "Critical: System resources at capacity. Remediation expected.",
]

# ---------- Worker process ----------

def cpu_burner(stop_event):
    """Busy-loop doing pointless math to consume a CPU core until told to stop."""
    while not stop_event.is_set():
        x = 0
        for i in range(200_000):
            x += i * i

# ---------- Visual helpers ----------

def status_color(percent):
    if percent < 50:
        return "green"
    elif percent < 80:
        return "yellow"
    elif percent < 95:
        return "orange3"
    else:
        return "red"

def status_label(percent):
    if percent < 50:
        return "NORMAL"
    elif percent < 80:
        return "ELEVATED"
    elif percent < 95:
        return "CRITICAL"
    else:
        return "FAILURE"

def make_bar(percent, width=34, color=None):
    color = color or status_color(percent)
    filled = int(width * percent / 100)
    bar = Text()
    bar.append("█" * filled, style=color)
    bar.append("░" * (width - filled), style="grey35")
    return bar

def pick_flavor(percent):
    if percent < 50:
        pool, style = FLAVOR_LOW, "grey70"
    elif percent < 80:
        pool, style = FLAVOR_MED, "yellow"
    elif percent < 95:
        pool, style = FLAVOR_HIGH, "orange3"
    else:
        pool, style = FLAVOR_CRIT, "bold red"
    return random.choice(pool), style

# ---------- Runner ----------

class ChaosRunner:
    def __init__(self, duration, workers):
        self.duration = duration
        self.workers = workers
        self.stop_event = multiprocessing.Event()
        self.processes = []
        self.logs = deque(maxlen=8)
        self.readings = []
        self.peak_cpu = 0
        self.start_time = None

    def log(self, message, style="white"):
        ts = datetime.now().strftime("%H:%M:%S")
        line = Text(f"[{ts}] ", style="dim") + Text(message, style=style)
        self.logs.appendleft(line)

    def start_workers(self):
        for i in range(self.workers):
            p = multiprocessing.Process(target=cpu_burner, args=(self.stop_event,))
            p.start()
            self.processes.append(p)
            self.log(f"Worker-{i + 1} spawned (PID {p.pid})", "cyan")

    def stop_workers(self):
        self.stop_event.set()
        for p in self.processes:
            p.join(timeout=2)
            if p.is_alive():
                p.terminate()
        self.log("All workers terminated. Load released.", "green")

    def build_frame(self, elapsed, cpu_percent, memory_percent):
        remaining = max(0, self.duration - elapsed)
        progress_pct = min(100, (elapsed / self.duration) * 100)

        header = Table.grid(expand=True)
        header.add_column(justify="left")
        header.add_column(justify="right")
        header.add_row(
            Text(" ⚡ CHAOS INJECTOR — CPU Stress Simulation", style="bold red"),
            Text(f"{self.workers} workers ", style="dim white"),
        )

        cpu_row = Table.grid(expand=True, padding=(0, 1))
        cpu_row.add_column(width=14)
        cpu_row.add_column(ratio=1)
        cpu_row.add_column(width=8, justify="right")
        cpu_row.add_column(width=10, justify="right")
        cpu_row.add_row(
            Text("CPU Load", style="bold white"),
            make_bar(cpu_percent),
            Text(f"{cpu_percent:5.1f}%", style=f"bold {status_color(cpu_percent)}"),
            Text(status_label(cpu_percent), style=f"bold {status_color(cpu_percent)}"),
        )

        mem_row = Table.grid(expand=True, padding=(0, 1))
        mem_row.add_column(width=14)
        mem_row.add_column(ratio=1)
        mem_row.add_column(width=8, justify="right")
        mem_row.add_column(width=10, justify="right")
        mem_row.add_row(
            Text("Memory", style="bold white"),
            make_bar(memory_percent),
            Text(f"{memory_percent:5.1f}%", style=f"bold {status_color(memory_percent)}"),
            Text(status_label(memory_percent), style=f"bold {status_color(memory_percent)}"),
        )

        progress_row = Table.grid(expand=True, padding=(0, 1))
        progress_row.add_column(width=14)
        progress_row.add_column(ratio=1)
        progress_row.add_column(width=14, justify="right")
        progress_row.add_row(
            Text("Injection", style="bold white"),
            make_bar(progress_pct, color="magenta"),
            Text(f"{remaining:.0f}s left", style="dim white"),
        )

        metrics_block = Table.grid(expand=True, padding=(1, 0, 0, 0))
        metrics_block.add_row(cpu_row)
        metrics_block.add_row(mem_row)
        metrics_block.add_row(Text(""))
        metrics_block.add_row(progress_row)

        log_lines = Text("\n").join(self.logs) if self.logs else Text("Waiting for events...", style="dim")
        log_panel = Panel(log_lines, title="[bold]Event Log[/bold]", border_style="grey35",
                           box=box.ROUNDED, padding=(0, 1), height=10)

        peak_text = Text(f"Peak CPU this run: {self.peak_cpu:.1f}%", style="bold red")

        body = Group(
            header,
            Text(""),
            metrics_block,
            Text(""),
            log_panel,
            Text(""),
            peak_text,
        )

        return Panel(
            body,
            title="[bold white] Failure Simulation [/bold white]",
            subtitle="[dim]Ctrl+C to abort[/dim]",
            border_style=status_color(cpu_percent),
            box=box.ROUNDED,
            padding=(1, 2),
        )

    def run(self):
        self.start_time = time.time()
        self.log(f"Initializing chaos injection — target ~95% CPU, {self.duration}s duration", "bold red")
        self.start_workers()

        try:
            with Live(self.build_frame(0, 0, 0), console=console, refresh_per_second=4) as live:
                while True:
                    elapsed = time.time() - self.start_time
                    if elapsed >= self.duration:
                        break

                    cpu_percent = psutil.cpu_percent(interval=1)  # 1-second sample
                    memory_percent = psutil.virtual_memory().percent
                    self.readings.append(cpu_percent)
                    self.peak_cpu = max(self.peak_cpu, cpu_percent)

                    if random.random() < 0.5:
                        msg, style = pick_flavor(cpu_percent)
                        self.log(msg, style)

                    live.update(self.build_frame(elapsed, cpu_percent, memory_percent))
        except KeyboardInterrupt:
            self.log("Manual interrupt received — aborting early", "yellow")
        finally:
            self.stop_workers()

        self.print_summary()

    def print_summary(self):
        avg_cpu = sum(self.readings) / len(self.readings) if self.readings else 0
        elapsed_total = time.time() - self.start_time

        summary = Table.grid(padding=(0, 3))
        summary.add_column(justify="left")
        summary.add_column(justify="left")
        summary.add_row(Text("Duration:", style="dim"), Text(f"{elapsed_total:.1f}s", style="bold white"))
        summary.add_row(Text("Peak CPU:", style="dim"), Text(f"{self.peak_cpu:.1f}%", style="bold red"))
        summary.add_row(Text("Average CPU:", style="dim"), Text(f"{avg_cpu:.1f}%", style="bold yellow"))
        summary.add_row(Text("Workers used:", style="dim"), Text(str(self.workers), style="bold white"))

        console.print()
        console.print(Panel(summary, title="[bold]Simulation Summary[/bold]",
                             border_style="red", box=box.ROUNDED, padding=(1, 2)))
        console.print("[dim]Self-healing system should have detected and reacted to this spike.[/dim]\n")


# ---------- Entry point ----------

def positive_int(value):
    duration = int(value)
    if duration <= 0:
        raise argparse.ArgumentTypeError("duration must be greater than zero")
    return duration


def main():
    parser = argparse.ArgumentParser(description="CPU stress test for self-healing demo")
    parser.add_argument("--duration", type=positive_int, default=30, help="How long to stress the CPU, in seconds")
    parser.add_argument("--workers", type=int, default=None, help="Number of processes (default: all CPU cores)")
    args = parser.parse_args()

    workers = args.workers or multiprocessing.cpu_count()
    runner = ChaosRunner(duration=args.duration, workers=workers)
    runner.run()


if __name__ == "__main__":
    main()