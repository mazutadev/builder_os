"""
Application initializer for setting up all core components.
"""
import os
from typing import Optional
from .di_container import di_container
from .console import ConsoleManager
from .command_manager import CommandManager


class AppInitializer:
    """
    Initializes and configures all application components.
    """
    def __init__(self):
        """
        Initialize the application initializer.
        """
        self._console: Optional[ConsoleManager] = None
        self._command_manager: Optional[CommandManager] = None

    def initialize(self) -> None:
        """
        Initialize all application components.
        """
        self._setup_console()
        self._setup_command_manager()
        self._setup_state_manager()
        self._log_initialization_status()

    def _setup_console(self) -> None:
        """
        Setup and configure console manager.
        """
        self._console = ConsoleManager()
        self._console.set_prefix("App")
        self._console.set_verbose(
            os.getenv("DEBUG", "False").lower() == "true"
        )
        di_container.register(ConsoleManager, self._console)
        self._console.log("Console manager initialized")

    def _setup_command_manager(self) -> None:
        """
        Setup and configure command manager.
        """
        self._command_manager = CommandManager()
        self._command_manager.set_console(self._console)
        di_container.register(CommandManager, self._command_manager)
        self._console.log("Command manager initialized")

    def _setup_state_manager(self) -> None:
        """
        Setup and configure state manager.
        """
        # State manager is already a singleton, just log its initialization
        self._console.log("State manager initialized")

    def _log_initialization_status(self) -> None:
        """
        Log the status of all initialized components.
        """
        self._console.log("Application initialization completed")
        self._console.debug("Initialized components:")
        self._console.debug("- Console Manager")
        self._console.debug("- Command Manager")
        self._console.debug("- State Manager")
        self._console.debug("- DI Container")

    def get_console(self) -> ConsoleManager:
        """
        Get the console manager instance.

        Returns:
            ConsoleManager instance
        """
        return self._console

    def get_command_manager(self) -> CommandManager:
        """
        Get the command manager instance.

        Returns:
            CommandManager instance
        """
        return self._command_manager


# Create a global instance
app_initializer = AppInitializer()