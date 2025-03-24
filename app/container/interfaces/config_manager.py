"""Container Config Manager Interface"""
from abc import ABC, abstractmethod
from ..types import (
    OSType, ContainerConfig, PackageManagerConfig, DockerSettings
)
from typing import Dict, Any
from pathlib import Path


class IContainerConfigManager(ABC):
    """Interface for container config manager"""

    @abstractmethod
    def load_from_file(self, config_path: Path) -> ContainerConfig:
        pass

    @abstractmethod
    def save_to_file(self, config: ContainerConfig, config_path: Path) -> None:
        pass

    @abstractmethod
    def _parse_config(self, config_data: Dict[str, Any]) -> ContainerConfig:
        pass

    @abstractmethod
    def get_docker_settings(self) -> DockerSettings:
        pass

    @abstractmethod
    def update_docker_settings(self, settings: DockerSettings) -> None:
        pass

    def get_package_manager(self, os_type: OSType) -> PackageManagerConfig:
        pass
