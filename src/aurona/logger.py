from rich.console import Console
from datetime import datetime

console = Console()


def _build_message_prefix() -> str:
    time = datetime.now()
    prefix = f"[{time}]"
    return prefix


def info(message: str):
    console.print(f"{_build_message_prefix()} [INFO] {message}", style="cyan")


def warn(message: str):
    console.print(f"{_build_message_prefix()} [WARN] {message}", style="yellow")


def error(message: str):
    console.print(f"{_build_message_prefix()} [ERROR] {message}", style="red")
