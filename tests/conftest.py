"""Common test fixtures and configuration"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from app.core.console import Console
from app.core.state_manager import StateManager
from app.container.config import ContainerConfigManager
from app.container.manager import ContainerManager


@pytest.fixture
def mock_console():
    """Create mock console"""
    return Mock(spec=Console)


@pytest.fixture
def mock_state_manager():
    """Create mock state manager"""
    return Mock(spec=StateManager)


@pytest.fixture
def mock_config_manager(mock_state_manager):
    """Create mock config manager"""
    return Mock(spec=ContainerConfigManager)


@pytest.fixture
def mock_docker_client():
    """Create mock docker client"""
    with pytest.MonkeyPatch.context() as mp:
        client = Mock()
        mp.setattr('docker.from_env', lambda **kwargs: client)
        yield client


@pytest.fixture
def container_manager(mock_console, mock_config_manager, mock_docker_client):
    """Create container manager instance"""
    return ContainerManager(mock_console, mock_config_manager)


@pytest.fixture
def test_data_dir(tmp_path):
    """Create temporary directory for test data"""
    data_dir = tmp_path / 'test_data'
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def sample_config_file(test_data_dir):
    """Create sample container config file"""
    config_path = test_data_dir / 'container.yaml'
    config_path.write_text("""
os_type: ubuntu
os_version: '22.04'
name: test-container
environment:
  TEST: value
working_dir: /app
    """)
    return config_path 