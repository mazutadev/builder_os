"""Unit tests for container manager module"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from docker.errors import DockerException

from app.container.manager import ContainerManager
from app.container.types import ContainerConfig, OSType, ContainerStatus
from app.container.exceptions import (
    ContainerError,
    ContainerCreateError,
    ContainerStartError,
    ContainerStopError,
    ContainerExecuteError,
    ContainerNotFoundError,
    ContainerRemoveError,
)
from app.core.console import Console
from app.container.config import ContainerConfigManager
from app.core.state_manager import StateManager


@pytest.fixture
def mock_console():
    """Create mock console"""
    return Mock(spec=Console)


@pytest.fixture
def mock_config_manager():
    """Create mock config manager"""
    return Mock(spec=ContainerConfigManager)


@pytest.fixture
def mock_docker_client():
    """Create mock docker client"""
    with patch('docker.from_env') as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def container_manager(mock_console, mock_config_manager, mock_docker_client):
    """Create container manager instance"""
    return ContainerManager(mock_console, mock_config_manager)


@pytest.fixture
def sample_config():
    """Create sample container config"""
    return ContainerConfig(
        os_type=OSType.UBUNTU,
        os_version='22.04',
        name='test-container',
        environment={'TEST': 'value'},
        working_dir='/app'
    )


def test_init_success(container_manager, mock_console, mock_config_manager):
    """Test successful initialization"""
    assert container_manager._console == mock_console
    assert container_manager._config_manager == mock_config_manager
    mock_console.success.assert_called_once_with('Docker client initialized successfully')


def test_init_failure(mock_console, mock_config_manager):
    """Test initialization failure"""
    with patch('docker.from_env') as mock:
        mock.side_effect = DockerException('Connection failed')
        with pytest.raises(ContainerError) as exc_info:
            ContainerManager(mock_console, mock_config_manager)
        assert 'Docker initialization failed' in str(exc_info.value)


def test_create_new_container(container_manager, sample_config, mock_docker_client):
    """Test creating new container"""
    mock_container = Mock()
    mock_container.id = 'test-id'
    mock_docker_client.containers.create.return_value = mock_container

    container_id = container_manager.create(sample_config)

    assert container_id == 'test-id'
    mock_docker_client.images.pull.assert_called_once_with('ubuntu:22.04')
    mock_docker_client.containers.create.assert_called_once()
    container_manager._console.success.assert_called_once()


def test_create_existing_container(container_manager, sample_config, mock_docker_client):
    """Test creating container when it already exists"""
    mock_container = Mock()
    mock_container.id = 'existing-id'
    mock_container.name = 'test-container'
    mock_docker_client.containers.list.return_value = [mock_container]

    container_id = container_manager.create(sample_config)

    assert container_id == 'existing-id'
    container_manager._console.warning.assert_called_once()


def test_create_failure(container_manager, sample_config, mock_docker_client):
    """Test container creation failure"""
    mock_docker_client.containers.create.side_effect = DockerException('Creation failed')
    
    with pytest.raises(ContainerCreateError) as exc_info:
        container_manager.create(sample_config)
    assert 'Container creation failed' in str(exc_info.value)


def test_start_container(container_manager, mock_docker_client):
    """Test starting container"""
    mock_container = Mock()
    mock_container.status = 'stopped'
    container_manager._container = mock_container

    container_manager.start()

    mock_container.start.assert_called_once()
    container_manager._console.success.assert_called_once()


def test_start_already_running(container_manager, mock_docker_client):
    """Test starting already running container"""
    mock_container = Mock()
    mock_container.status = 'running'
    container_manager._container = mock_container

    container_manager.start()

    mock_container.start.assert_not_called()
    container_manager._console.info.assert_called_once()


def test_start_no_container(container_manager):
    """Test starting non-existent container"""
    with pytest.raises(ContainerNotFoundError):
        container_manager.start()


def test_stop_container(container_manager, mock_docker_client):
    """Test stopping container"""
    mock_container = Mock()
    container_manager._container = mock_container

    container_manager.stop()

    mock_container.stop.assert_called_once()
    container_manager._console.success.assert_called_once()


def test_stop_no_container(container_manager):
    """Test stopping non-existent container"""
    with pytest.raises(ContainerNotFoundError):
        container_manager.stop()


def test_execute_command(container_manager, mock_docker_client):
    """Test executing command in container"""
    mock_container = Mock()
    mock_container.status = 'running'
    mock_container.exec_run.return_value = (0, (b'output', None))
    container_manager._container = mock_container

    result = container_manager.execute('test command')

    assert result == 'output'
    mock_container.exec_run.assert_called_once_with('test command', demux=True)


def test_execute_command_failure(container_manager, mock_docker_client):
    """Test command execution failure"""
    mock_container = Mock()
    mock_container.status = 'running'
    mock_container.exec_run.return_value = (1, (None, b'error'))
    container_manager._container = mock_container

    with pytest.raises(ContainerExecuteError) as exc_info:
        container_manager.execute('test command')
    assert 'Command failed' in str(exc_info.value)


def test_remove_container(container_manager, mock_docker_client):
    """Test removing container"""
    mock_container = Mock()
    mock_container.status = 'stopped'
    container_manager._container = mock_container

    container_manager.remove()

    mock_container.remove.assert_called_once_with(force=False)
    container_manager._console.success.assert_called_once()


def test_remove_running_container(container_manager, mock_docker_client):
    """Test removing running container"""
    mock_container = Mock()
    mock_container.status = 'running'
    container_manager._container = mock_container

    container_manager.remove()

    mock_container.stop.assert_called_once()
    mock_container.remove.assert_called_once_with(force=False)
    container_manager._console.success.assert_called()


def test_remove_no_container(container_manager):
    """Test removing non-existent container"""
    with pytest.raises(ContainerNotFoundError):
        container_manager.remove()


def test_get_status(container_manager, mock_docker_client):
    """Test getting container status"""
    mock_container = Mock()
    mock_container.status = 'running'
    container_manager._container = mock_container

    status = container_manager.get_status()

    assert status == ContainerStatus.RUNNING


def test_get_status_no_container(container_manager):
    """Test getting status of non-existent container"""
    status = container_manager.get_status()
    assert status == ContainerStatus.FAILED


def test_get_container_info(container_manager, mock_docker_client):
    """Test getting container information"""
    mock_container = Mock()
    mock_container.name = 'test'
    mock_container.id = 'test-id'
    mock_container.status = 'running'
    mock_container.image.tags = ['ubuntu:22.04']
    mock_container.attrs = {
        'Created': '2024-03-23T12:00:00Z',
        'NetworkSettings': {'networks': {}}
    }
    mock_container.ports = {}
    container_manager._container = mock_container

    info = container_manager.get_container_info()

    assert info['name'] == 'test'
    assert info['id'] == 'test-id'
    assert info['status'] == 'running'
    assert info['image'] == 'ubuntu:22.04'


def test_get_container_info_no_container(container_manager):
    """Test getting info of non-existent container"""
    with pytest.raises(ContainerNotFoundError):
        container_manager.get_container_info()


def test_get_logs(container_manager, mock_docker_client):
    """Test getting container logs"""
    mock_container = Mock()
    mock_container.logs.return_value = b'container logs'
    container_manager._container = mock_container

    logs = container_manager.get_logs()

    assert logs == 'container logs'
    mock_container.logs.assert_called_once()


def test_get_logs_no_container(container_manager):
    """Test getting logs of non-existent container"""
    with pytest.raises(ContainerNotFoundError):
        container_manager.get_logs() 