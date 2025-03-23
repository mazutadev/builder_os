#!/usr/bin/env python3
"""
Main entry point for the application.
"""
import sys
from dotenv import load_dotenv
from app.core.initializer import app_initializer
from app.core.exceptions import (
    ApplicationError,
    InitializationError
)


# Load environment variables from .env file
load_dotenv()


def main():
    """
    Main application function.
    """
    try:
        # Initialize all application components
        app_initializer.initialize()

        # Get initialized components
        console = app_initializer.get_console()
        env_config = app_initializer.get_env_config()

        # Use environment configuration
        console.success(f"Starting {env_config.app_name}...")
        console.debug(f"Debug mode: {env_config.debug_mode}")
        console.debug(f"Running from: {env_config.project_root}")
        # Add your main application logic here

    except (InitializationError, ApplicationError) as e:
        print(
            "CRITICAL ERROR: Failed to initialize application",
            file=sys.stderr
        )
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
