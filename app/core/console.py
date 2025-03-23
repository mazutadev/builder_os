"""
Console manager for handling console operations.
"""
from typing import Optional
from rich.console import Console
from enum import Enum


class ConsoleColors(Enum):
    """
    Colors for console output.
    """
    SUCCESS = "[bold green]"
    WARNING = "[bold yellow]"
    ERROR = "[bold red]"
    INFO = "[bold blue]"
    DEBAG = "[bold magenta]"
    HEADER = "[bold cyan]"
    STANDARD = "[bold white]"


class ConsoleManager:
    """
    Manages console operations and output formatting.
    """
    def __init__(self):
        self._console = Console()
        self._prefix: Optional[str] = None
        self._is_verbose: bool = False

    def set_prefix(self, prefix: str) -> None:
        """
        Set the prefix for console output.

        Args:
            prefix: The prefix to use for console output
        """
        self._prefix = prefix

    def set_verbose(self, verbose: bool) -> None:
        """
        Set verbose mode for console output.

        Args:
            verbose: Whether to enable verbose output 
        """
        self._is_verbose = verbose

    def log(
            self, message: str,
            color: ConsoleColors = ConsoleColors.STANDARD) -> None:
        """
        Log a message to the console.

        Args:
            message: The message to log
            color: The color to use for the message
        """
        prefix = (
            f"{color.value}[{self._prefix}] "
            if self._prefix else ""
        )
        self._console.print(f"{prefix}{message}[/]")

    def info(
            self, message: str,
            color: ConsoleColors = ConsoleColors.INFO) -> None:
        """
        Log an info message to the console.
        """
        prefix = f"{ConsoleColors.INFO.value}[INFO] "
        self.log(f"{prefix}{message}", color)

    def debug(
            self, message: str,
            color: ConsoleColors = ConsoleColors.DEBAG) -> None:
        """
        Log a debug message to the console.

        Args:
            message: The debug message to log
        """
        prefix = f"{ConsoleColors.DEBAG.value}[DEBAG] "
        if self._is_verbose:
            self.log(f"{prefix}{message}", color)

    def warning(
            self, message: str,
            color: ConsoleColors = ConsoleColors.WARNING) -> None:
        """
        Log a warning message to the console.

        Args:
            message: The waning message to log
        """
        prefix = f"{ConsoleColors.WARNING.value}[WARNING] "
        if self._is_verbose:
            self.log(f"{prefix}{message}", color)

    def error(
            self, message: str,
            color: ConsoleColors = ConsoleColors.ERROR) -> None:
        """
        Log an error message to the console.
        """
        prefix = f"{ConsoleColors.ERROR.value}[ERROR] "
        self.log(f"{prefix}{message}", color)

    def success(
            self, message: str,
            color: ConsoleColors = ConsoleColors.SUCCESS) -> None:
        """
        Log a success message to the console.
        """
        prefix = f"{ConsoleColors.SUCCESS.value}[SUCCESS] "
        self.log(f"{prefix}{message}", color)
