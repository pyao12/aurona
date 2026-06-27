"""基于 Rich 的彩色控制台日志。"""

from datetime import datetime

from rich.console import Console

console = Console()


def _build_message_prefix() -> str:
    """返回带时间戳的日志前缀。"""
    time = datetime.now()
    prefix = f"[{time}]"
    return prefix


def info(message: str):
    """输出一条普通信息。"""
    console.print(f"{_build_message_prefix()} [INFO] {message}", style="cyan")


def warn(message: str):
    """输出一条警告信息。"""
    console.print(f"{_build_message_prefix()} [WARN] {message}", style="yellow")


def error(message: str):
    """输出一条错误信息。"""
    console.print(f"{_build_message_prefix()} [ERROR] {message}", style="red")
