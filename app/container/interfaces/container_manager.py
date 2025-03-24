"""Container Manager Interface"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from .package_manager import IPackageManager
from ..types import ContainerConfig, ContainerStatus


class IContainerManager(ABC):
    """Interface for container manager"""

    @property
    @abstractmethod
    def package_manager(self) -> IPackageManager:
        pass

    @abstractmethod
    def create(self, config: ContainerConfig) -> str:
        pass

    @abstractmethod
    def remove(self, force: bool = False) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def execute(self, command: str) -> str:
        pass

    @abstractmethod
    def get_status(self) -> ContainerStatus:
        pass

    @abstractmethod
    def get_container_info(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_logs(self) -> str:
        pass
