#!/usr/bin/env python3
"""
Main entry point for the application.
"""
import sys
from dotenv import load_dotenv
from app.core.initializer import app_initializer
from app.core.console import Console
from app.core.state_manager import StateManager
from app.core.di_container import DIContainer
from app.container.types import ContainerConfig, OSType
from app.container.manager import ContainerManager
from app.container.config import ContainerConfigManager
from app.container.exceptions import ContainerError
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
        di_container = app_initializer.get_di_container()

        

        # Use environment configuration
        console.success(f"Starting {env_config.app_name}...")
        console.debug(f"Debug mode: {env_config.debug_mode}")
        console.debug(f"Running from: {env_config.project_root}")
        # Add your main application logic here

        config_manager = ContainerConfigManager(di_container.get(StateManager))
        container_manager = ContainerManager(console, config_manager)

        config = ContainerConfig(
            os_type=OSType.UBUNTU,
            os_version='22.04',
            name='test-container',
            environment={
                "DEBIAN_FRONTEND": "noninteractive",
            },
            working_dir='/app'
        )
        try:
            console.info('Creating container')
            container_id = container_manager.create(config)

            container_manager.start()

            console.info('Testing container')

            output = container_manager.execute('apt-get update')
            console.debug(f'Update output: {output}')

            output = container_manager.execute('apt-get install -y python3 python3-pip')
            console.debug(f'Install output: {output}')

            output = container_manager.execute('python3 --version')
            console.info(f'Python version: {output}')

            container_info = container_manager.get_container_info()
            console.info(f'Container information:')
            for key, value in container_info.items():
                console.info(f'  {key}: {value}')
        except ContainerError as e:
            console.error(f'Container error: {e}')
        finally:
            console.info('Cleaning up...')
            container_manager.remove()

        



    except (InitializationError, ApplicationError) as e:
        print(
            "CRITICAL ERROR: Failed to initialize application",
            file=sys.stderr
        )
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
