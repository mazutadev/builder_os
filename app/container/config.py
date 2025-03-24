"""
Модуль конфигурации контейнеров.
"""
from typing import Dict, Any
from pathlib import Path
import yaml

from .types import (
    OSType, ContainerConfig,
    PackageManager, PackageManagerConfig,
    DockerSettings
)
from .exceptions import ContainerConfigError
from ..core.state_manager import StateManager
from .interfaces.config_manager import IContainerConfigManager


class ContainerConfigManager(IContainerConfigManager):
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

    def get_package_manager(self, os_type: OSType) -> PackageManagerConfig:
        """Get package manager configuration for OS type"""
        pkg_manager_type = OS_PACKAGE_MANAGER_MAPPING.get(os_type)
        if not pkg_manager_type:
            raise ContainerConfigError(f"Unsupported OS type: {os_type}")

        return PACKAGE_MANAGER_CONFIGS[pkg_manager_type]


# Package manager configuration
PACKAGE_MANAGER_CONFIGS: Dict[PackageManager, PackageManagerConfig] = {
    PackageManager.APT: PackageManagerConfig(
        update_cmd="apt update",
        install_cmd="apt install -y",
        remove_cmd="apt remove -y",
        upgrade_cmd="apt upgrade -y",
        search_cmd="apt search",
        list_cmd="apt list",
        show_cmd="apt show",
        clean_cmd="apt clean",
        require_packages=[
            "apt", "apt-utils", "apt-transport-https", 
            "ca-certificates", "curl", "gnupg-agent", 
            "software-properties-common"]
    ),
    PackageManager.YUM: PackageManagerConfig(
        update_cmd="yum update -y",
        install_cmd="yum install -y",
        remove_cmd="yum remove -y",
        upgrade_cmd="yum upgrade -y",
        search_cmd="yum search",
        list_cmd="yum list",
        show_cmd="yum show",
        clean_cmd="yum clean",
        require_packages=[
            "yum", "yum-utils", "epel-release",
            "python3", "python3-pip"]
    ),
    PackageManager.DNF: PackageManagerConfig(
        update_cmd="dnf update -y",
        install_cmd="dnf install -y",
        remove_cmd="dnf remove -y",
        upgrade_cmd="dnf upgrade -y",
        search_cmd="dnf search",
        list_cmd="dnf list",
        show_cmd="dnf show",
        clean_cmd="dnf clean",
        require_packages=["dnf", "python3", "python3-pip"]
    ),
    PackageManager.PACMAN: PackageManagerConfig(
        update_cmd="pacman -Syu --noconfirm",
        install_cmd="pacman -S --noconfirm",
        remove_cmd="pacman -Rns --noconfirm",
        upgrade_cmd="pacman -Su --noconfirm",
        search_cmd="pacman -Ss",
        list_cmd="pacman -Ql",
        show_cmd="pacman -Qi",
        clean_cmd="pacman -Sc",
        require_packages=["pacman", "python3", "python3-pip"]
    ),
    PackageManager.ZYPPER: PackageManagerConfig(
        update_cmd="zypper refresh",
        install_cmd="zypper install -y",
        remove_cmd="zypper remove -y",
        upgrade_cmd="zypper update -y",
        search_cmd="zypper search",
        list_cmd="zypper list",
        show_cmd="zypper info",
        clean_cmd="zypper clean",
        require_packages=["zypper", "python3", "python3-pip"]
    ),
    PackageManager.APK: PackageManagerConfig(
        update_cmd="apk update",
        install_cmd="apk add",
        remove_cmd="apk del",
        upgrade_cmd="apk upgrade",
        search_cmd="apk search",
        list_cmd="apk list",
        show_cmd="apk info",
        clean_cmd="apk cache clean",
        require_packages=["apk-tools", "python3", "python3-pip"]
    )
}

OS_PACKAGE_MANAGER_MAPPING: Dict[OSType, PackageManager] = {
    OSType.UBUNTU: PackageManager.APT,
    OSType.DEBIAN: PackageManager.APT,
    OSType.CENTOS: PackageManager.YUM,
    OSType.FEDORA: PackageManager.DNF,
    OSType.ALPINE: PackageManager.APK,
    OSType.ARCHLINUX: PackageManager.PACMAN
}