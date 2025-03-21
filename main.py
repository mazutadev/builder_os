#!/usr/bin/env python3
"""
Main entry point for the application.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from app.core.di_container import di_container
from app.core.console import ConsoleManager


# Add project root directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


# Load environment variables from .env file
load_dotenv()


def setup_services():
    """
    Initialize and register application services.
    """
    # Create and register console manager
    console = ConsoleManager()
    console.set_prefix("App")
    console.set_verbose(os.getenv("DEBUG", "False").lower() == "true")
    di_container.register(ConsoleManager, console)


def main():
    """
    Main application function.
    """
    app_name = os.getenv("APP_NAME", "my_python_app")
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Setup application services
    setup_services()
    
    # Get console manager from DI container
    console = di_container.get(ConsoleManager)
    console.log(f"Starting {app_name}...")
    console.debug(f"Debug mode: {debug}")
    
    # Add your main application logic here


if __name__ == "__main__":
    main()