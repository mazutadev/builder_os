"""
Console manager for handling console operations.
"""
from typing import Optional


class ConsoleManager:
    """
    Manages console operations and output formatting.
    """
    def __init__(self):
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

    def log(self, message: str) -> None:
        """
        Log a message to the console.

        Args:
            message: The message to log
        """
        prefix = f"[{self._prefix}] " if self._prefix else ""
        print(f"{prefix}{message}")

    def debug(self, message: str) -> None:
        """
        Log a debug message to the console.

        Args:
            message: The debug message to log
        """
        if self._is_verbose:
            self.log(f"DEBUG: {message}") 