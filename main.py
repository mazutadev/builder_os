#!/usr/bin/env python3
"""
Main entry point for the application.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


# Add project root directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))


# Load environment variables from .env file
load_dotenv()


def main():
    """
    Main application function.
    """
    app_name = os.getenv("APP_NAME", "my_python_app")
    debug = os.getenv("DEBUG", "False").lower() == "true"

    print(f"Starting {app_name}...")
    print(f"Debug mode: {debug}")

    # Add your main application logic here


if __name__ == "__main__":
    main() 