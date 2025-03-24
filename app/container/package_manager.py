"""Module for package management in containers"""

from .interfaces.package_manager import IPackageManager
from .interfaces.config_manager import IContainerConfigManager
from .interfaces.container_manager import IContainerManager
from .types import (PackageManagerConfig, ContainerConfig)
from .exceptions import ContainerError
from ..core.console import Console


class PackageManager(IPackageManager):
    """Base class for package managers"""

    def __init__(
            self, container_manager: IContainerManager,
            console: Console,
            config_manager: IContainerConfigManager,
            current_config: ContainerConfig) -> None:

        self._container_manager = container_manager
        self._console = console
        self._config_manager = config_manager
        self._current_config = current_config

    def _get_package_manager(self) -> PackageManagerConfig:
        """Get package manager configuration for current container"""
        if not self._current_config:
            raise ContainerError("No configuration available")
        return self._config_manager.get_package_manager(
            self._current_config.os_type)

    def update_packages(self) -> None:
        """Update package lists"""
        pkg_manager = self._get_package_manager()
        self._container_manager.execute(pkg_manager.update_cmd)

    def install_package(self, package_name: str) -> None:
        """Install package using appropriate package manager"""
        pkg_manager = self._get_package_manager()
        self._container_manager.execute(
            f"{pkg_manager.install_cmd} {package_name}")

    def remove_package(self, package_name: str) -> None:
        """Remove package using appropriate package manager"""
        pkg_manager = self._get_package_manager()
        self._container_manager.execute(
            f"{pkg_manager.remove_cmd} {package_name}")

    def search_package(self, query: str) -> str:
        """Search for package using appropriate package manager"""
        pkg_manager = self._get_package_manager()
        return self._container_manager.execute(
            f"{pkg_manager.search_cmd} {query}")

    def list_installed_packages(self) -> str:
        """List installed packages using appropriate package manager"""
        pkg_manager = self._get_package_manager()
        return self._container_manager.execute(pkg_manager.list_cmd)

    def clean_package_cache(self) -> None:
        """Clean package cache using appropriate package manager"""
        pkg_manager = self._get_package_manager()
        self._container_manager.execute(pkg_manager.clean_cmd)
