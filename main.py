#!/usr/bin/env python3
"""
Main entry point for the application.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from app.core.initializer import app_initializer


# Add project root directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


# Load environment variables from .env file
load_dotenv()


def main():
    """
    Main application function.
    """
    app_name = os.getenv("APP_NAME", "app")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Initialize all application components
    app_initializer.initialize()
    
    # Get console manager from DI container
    console = app_initializer.get_console()
    console.log(f"Starting {app_name}...")
    console.debug(f"Debug mode: {debug}")
    
    # Example of using command manager
    cmd_manager = app_initializer.get_command_manager()
    result = cmd_manager.execute("ls -la")
    console.log(f"Command result: {result.status.value}")
    if result.stdout:
        console.log(f"Output: {result.stdout}")
    if result.stderr:
        console.log(f"Errors: {result.stderr}")
    
    # Add your main application logic here


if __name__ == "__main__":
    main()