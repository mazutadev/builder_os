"""Package Manager Interface"""

from abc import ABC, abstractmethod
from .config_manager import IContainerConfigManager


class IPackageManager(ABC):
    """Package Manager Interface"""

    @abstractmethod
    def _get_package_manager(self) -> IContainerConfigManager:
        pass

    @abstractmethod
    def update_packages(self) -> None:
        pass

    @abstractmethod
    def install_package(self, package_name: str) -> None:
        pass

    @abstractmethod
    def remove_package(self, package_name: str) -> None:
        pass

    @abstractmethod
    def search_package(self, query: str) -> str:
        pass

    @abstractmethod
    def list_installed_packages(self) -> str:
        pass

    @abstractmethod
    def clean_package_cache(self) -> None:
        pass
