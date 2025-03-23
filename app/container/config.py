"""
Модуль конфигурации контейнеров.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import yaml

from .types import OSType, ContainerConfig
from .exceptions import ContainerConfigError
from ..core.state_manager import StateManager


@dataclass
class DockerSettings:
    """Docker settings"""
    socket_path: str = 'unix://var/run/docker.sock'
    api_version: str = 'auto'
    timeout: int = 120
    tls: bool = False
    cert_path: Optional[Path] = None


class ContainerConfigManager:
    """Manager for container configurations"""

    def __init__(self, state_manager: StateManager):
        self._state_manager = state_manager
        self._docker_settings = DockerSettings()

    def load_from_file(self, config_path: Path) -> ContainerConfig:
        """Load config from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config_data = yaml.safe_load(file)
            return self._parse_config(config_data)
        except FileNotFoundError:
            raise ContainerConfigError(
                f'Config file for container not found: {config_path}')
        except yaml.YAMLError as e:
            raise ContainerConfigError(f'Invalid YAML format: {e}')

    def _parse_config(self, config_data: Dict[str, Any]) -> ContainerConfig:
        """Parse config data into Container config YAML file"""
        try:
            if 'os_type' not in config_data or 'os_version' not in config_data:
                raise ContainerConfigError(
                    'Missing required fields: os_type and os_version'
                )

            try:
                os_type = OSType[config_data['os_type'].upper()]
            except KeyError:
                raise ContainerConfigError(
                    f'Unsupported OS type: {config_data["os_type"]}'
                )

            return ContainerConfig(
                os_type=os_type,
                os_version=config_data['os_version'],
                name=config_data.get('name'),
                volumes=config_data.get('volumes', {}),
                environment=config_data.get('environment', {}),
                working_dir=config_data.get('working_dir'),
                command=config_data.get('command')
            )
        except Exception as e:
            raise ContainerConfigError(f'Error parsing config: {e}')

    def save_to_file(self, config: ContainerConfig, config_path: Path) -> None:
        """Save container config to YAML file"""
        try:
            config_data = {
                'os_type': config.os_type.name.lower(),
                'os_version': config.os_version,
            }

            if config.name:
                config_data['name'] = config.name
            if config.volumes:
                config_data['volumes'] = config.volumes
            if config.environment:
                config_data['environment'] = config.environment
            if config.working_dir:
                config_data['working_dir'] = config.working_dir
            if config.command:
                config_data['command'] = config.command

            with open(config_path, 'w') as file:
                yaml.safe_dump(config_data, file, default_flow_style=False)
        except Exception as e:
            raise ContainerConfigError(f'Error saving config: {e}')

    def get_docker_settings(self) -> DockerSettings:
        """Get Docker settings"""
        return self._docker_settings

    def update_docker_settings(self, settings: DockerSettings) -> None:
        """Update Docker settings"""
        self._docker_settings = settings
