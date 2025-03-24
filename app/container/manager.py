"""Module for managing containers"""

from typing import Optional, Dict, Any
import docker
from docker.models.containers import Container
from docker.errors import DockerException

from .types import ContainerStatus, ContainerConfig, PackageManagerConfig
from .config import ContainerConfigManager
from .exceptions import (
    ContainerError,
    ContainerCreateError,
    ContainerStartError,
    ContainerStopError,
    ContainerExecuteError,
    ContainerNotFoundError,
    ContainerRemoveError,
)
from ..core.console import Console


class ContainerManager:
    """Manager for container operations"""
    def __init__(
            self,
            console: Console,
            config_manager: ContainerConfigManager) -> None:
        """Container Manager initialization"""
        self._console = console
        self._config_manager = config_manager
        self._container: Optional[Container] = None
        self._current_config: Optional[ContainerConfig] = None

        try:
            docker_settings = config_manager.get_docker_settings()
            self._client = docker.from_env(
                timeout=docker_settings.timeout,
                version=docker_settings.api_version,
            )
            self._console.success('Docker client initialized successfully')
        except DockerException as e:
            self._console.error(f'Failed to initialize Docker client: {e}')
            raise ContainerError(f'Docker initialization failed: {e}')

    def create(self, config: ContainerConfig) -> str:
        """Create a new container"""
        self._current_config = config
        image_name = f'{config.os_type.value}:{config.os_version}'

        try:
            if config.name:
                existing_container = self._client.containers.list(
                    all=True,
                    filters={'name': config.name}
                )
                if existing_container:
                    existing_container = existing_container[0]
                    self._container = existing_container
                    self._console.warning(f'Container: {self._container.name} '
                                          'already exists'
                                          )
                    return self._container.id

            self._console.info(f'Pulling image: {image_name}')
            self._client.images.pull(image_name)

            if config.volumes:
                volumes = {
                    host_path: {
                        'bind': container_path,
                        'mode': 'rw'
                    }
                    for host_path, container_path in config.volumes.items()
                }

            self._console.info(f'Creating container from {image_name}')
            self._container = self._client.containers.create(
                image=image_name,
                name=config.name,
                volumes=volumes,
                environment=config.environment,
                working_dir=config.working_dir,
                command='sleep infinity',
                detach=True,
            )

            container_id = self._container.id
            self._console.success(
                f'Container created successfully: {container_id}')
            return container_id

        except DockerException as e:
            self._console.error(f'Failed to create container: {e}')
            raise ContainerCreateError(f'Container creation failed: {e}')
        
    def remove(self, force: bool = False) -> None:
        """Remove the container"""
        if not self._container:
            raise ContainerNotFoundError('No container created')
        try:
            self._console.info(f'Removing container: {self._container.name}')

            if not force:
                self._container.reload()
                if self._container.status == 'running':
                    self._console.info('Stopping container before removal...')
                    self._container.stop()
                    self._console.success('Container stopped successfully')

            self._container.remove(force=force)
            self._console.success('Container removed successfully')
            self._container = None
            self._current_config = None

        except DockerException as e:
            self._console.error(f'Failed to remove container: {e}')
            raise ContainerRemoveError(f'Container removal failed: {e}')

    def start(self) -> None:
        """Start the container"""
        if not self._container:
            raise ContainerNotFoundError('No container created')
        try:
            self._console.info('Starting container...')

            self._container.reload()
            if self._container.status == 'running':
                self._console.info('Container is already running')
                return

            self._container.start()

            self._console.success('Container started successfully')
        except DockerException as e:
            self._console.error(f'Failed to start container: {e}')
            raise ContainerStartError(f'Container start failed: {e}')

    def stop(self) -> None:
        """Strop the container"""
        if not self._container:
            raise ContainerNotFoundError('No container created')
        try:
            self._console.info('Stopping container...')
            self._container.stop()
            self._console.success('Container stopped successfully')
        except DockerException as e:
            self._console.error(f'Failed to stop container: {e}')
            raise ContainerStopError(f'Container stop failed: {e}')

    def execute(self, command: str) -> str:
        """Execute a command in the container"""
        if not self._container:
            raise ContainerNotFoundError('No container created')
        try:
            self._container.reload()
            if self._container.status != 'running':
                self._console.warning(
                    'Container is {self._container.status}, '
                    'attempting to start...')
                self._container.start()
                self._console.success('Container started successfully')
            self._console.debug(f'Executing command: {command}')
            exit_code, output = self._container.exec_run(
                command,
                demux=True
            )

            if exit_code != 0:
                error_message = output[1].decode() if output[1] else output[0].decode()
                raise ContainerExecuteError(
                    f'Command failed with exit code '
                    f'{exit_code}: {error_message}'
                )

            result = output[0].decode().strip() if output[0] else ''
            self._console.debug(f'Command output: {result}')
            return result
        except DockerException as e:
            self._console.error(f'Failed to execute command: {e}')
            raise ContainerExecuteError(f'Command execution failed: {e}')

    def get_status(self) -> ContainerStatus:
        """Get the status of the container"""
        if not self._container:
            return ContainerStatus.FAILED
        try:
            self._container.reload()
            return ContainerStatus(self._container.status)
        except DockerException:
            return ContainerStatus.FAILED

    def get_container_info(self) -> Dict[str, Any]:
        """Get container information"""
        if not self._container:
            raise ContainerNotFoundError('No container created')
        try:
            self._container.reload()
            return {
                'id': self._container.id,
                'name': self._container.name,
                'status': self._container.status,
                'image': self._container.image.tags[0],
                'created': self._container.attrs['Created'],
                'ports': self._container.ports,
                'network_setting': self._container.attrs['NetworkSettings']
            }
        except DockerException as e:
            self._console.error(f'Failed to get container info: {e}')

    def get_logs(self) -> str:
        """Get container logs"""
        if not self._container:
            raise ContainerNotFoundError('No container created')
        try:
            return self._container.logs().decode()
        except DockerException as e:
            self._console.error(f'Failed to get logs: {e}')
            return ''

    def _get_package_manager(self) -> PackageManagerConfig:
        """Get package manager configuration for current container"""
        if not self._current_config:
            raise ContainerError("No configuration available")
        return self._config_manager.get_package_manager(
            self._current_config.os_type)

    def update_packages(self) -> None:
        """Update package lists"""
        pkg_manager = self._get_package_manager()
        self.execute(pkg_manager.update_cmd)

    def install_package(self, package_name: str) -> None:
        """Install package using appropriate package manager"""
        pkg_manager = self._get_package_manager()
        self.execute(f"{pkg_manager.install_cmd} {package_name}")

    def remove_package(self, package_name: str) -> None:
        """Remove package using appropriate package manager"""
        pkg_manager = self._get_package_manager()
        self.execute(f"{pkg_manager.remove_cmd} {package_name}")

    def search_package(self, query: str) -> str:
        """Search for package using appropriate package manager"""
        pkg_manager = self._get_package_manager()
        return self.execute(f"{pkg_manager.search_cmd} {query}")

    def list_installed_packages(self) -> str:
        """List installed packages using appropriate package manager"""
        pkg_manager = self._get_package_manager()
        return self.execute(pkg_manager.list_cmd)

    def clean_package_cache(self) -> None:
        """Clean package cache using appropriate package manager"""
        pkg_manager = self._get_package_manager()
        self.execute(pkg_manager.clean_cmd)
