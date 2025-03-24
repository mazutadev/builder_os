"""Unit tests for container configuration module"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import yaml

from app.container.config import ContainerConfigManager, DockerSettings
from app.container.types import ContainerConfig, OSType
from app.container.exceptions import ContainerConfigError
from app.core.state_manager import StateManager


@pytest.fixture
def mock_state_manager():
    """Create mock state manager"""
    return Mock(spec=StateManager)


@pytest.fixture
def config_manager(mock_state_manager):
    """Create config manager instance"""
    return ContainerConfigManager(mock_state_manager)


@pytest.fixture
def sample_config_data():
    """Create sample config data"""
    return {
        'os_type': 'ubuntu',
        'os_version': '22.04',
        'name': 'test-container',
        'environment': {'TEST': 'value'},
        'working_dir': '/app'
    }


@pytest.fixture
def sample_config_file(tmp_path, sample_config_data):
    """Create sample config file"""
    config_path = tmp_path / 'container.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(sample_config_data, f)
    return config_path


def test_load_config_success(config_manager, sample_config_file):
    """Test successful config loading"""
    config = config_manager.load_from_file(sample_config_file)

    assert isinstance(config, ContainerConfig)
    assert config.os_type == OSType.UBUNTU
    assert config.os_version == '22.04'
    assert config.name == 'test-container'
    assert config.environment == {'TEST': 'value'}
    assert config.working_dir == '/app'


def test_load_config_file_not_found(config_manager):
    """Test loading non-existent config file"""
    with pytest.raises(ContainerConfigError) as exc_info:
        config_manager.load_from_file(Path('non_existent.yaml'))
    assert 'Config file for container not found' in str(exc_info.value)


def test_load_config_invalid_yaml(config_manager, tmp_path):
    """Test loading invalid YAML file"""
    config_path = tmp_path / 'invalid.yaml'
    with open(config_path, 'w') as f:
        f.write('invalid: yaml: content: -')

    with pytest.raises(ContainerConfigError) as exc_info:
        config_manager.load_from_file(config_path)
    assert 'Invalid YAML format' in str(exc_info.value)


def test_load_config_missing_required_fields(config_manager, tmp_path):
    """Test loading config with missing required fields"""
    config_path = tmp_path / 'incomplete.yaml'
    with open(config_path, 'w') as f:
        yaml.dump({'name': 'test'}, f)

    with pytest.raises(ContainerConfigError) as exc_info:
        config_manager.load_from_file(config_path)
    assert 'Missing required fields' in str(exc_info.value)


def test_load_config_invalid_os_type(config_manager, tmp_path):
    """Test loading config with invalid OS type"""
    config_path = tmp_path / 'invalid_os.yaml'
    with open(config_path, 'w') as f:
        yaml.dump({
            'os_type': 'invalid_os',
            'os_version': '22.04'
        }, f)

    with pytest.raises(ContainerConfigError) as exc_info:
        config_manager.load_from_file(config_path)
    assert 'Unsupported OS type' in str(exc_info.value)


def test_save_config_success(config_manager, tmp_path):
    """Test successful config saving"""
    config = ContainerConfig(
        os_type=OSType.UBUNTU,
        os_version='22.04',
        name='test-container',
        environment={'TEST': 'value'},
        working_dir='/app'
    )
    config_path = tmp_path / 'output.yaml'

    config_manager.save_to_file(config, config_path)

    assert config_path.exists()
    with open(config_path, 'r') as f:
        saved_data = yaml.safe_load(f)
        assert saved_data['os_type'] == 'ubuntu'
        assert saved_data['os_version'] == '22.04'
        assert saved_data['name'] == 'test-container'
        assert saved_data['environment'] == {'TEST': 'value'}
        assert saved_data['working_dir'] == '/app'


def test_save_config_failure(config_manager):
    """Test config saving failure"""
    config = ContainerConfig(
        os_type=OSType.UBUNTU,
        os_version='22.04'
    )
    config_path = Path('/invalid/path/config.yaml')

    with pytest.raises(ContainerConfigError) as exc_info:
        config_manager.save_to_file(config, config_path)
    assert 'Error saving config' in str(exc_info.value)


def test_get_docker_settings(config_manager):
    """Test getting Docker settings"""
    settings = config_manager.get_docker_settings()
    assert isinstance(settings, DockerSettings)
    assert settings.socket_path == 'unix://var/run/docker.sock'
    assert settings.api_version == 'auto'
    assert settings.timeout == 120
    assert settings.tls is False
    assert settings.cert_path is None


def test_update_docker_settings(config_manager):
    """Test updating Docker settings"""
    new_settings = DockerSettings(
        socket_path='tcp://localhost:2375',
        api_version='1.41',
        timeout=60,
        tls=True,
        cert_path=Path('/path/to/cert')
    )

    config_manager.update_docker_settings(new_settings)
    settings = config_manager.get_docker_settings()

    assert settings.socket_path == 'tcp://localhost:2375'
    assert settings.api_version == '1.41'
    assert settings.timeout == 60
    assert settings.tls is True
    assert settings.cert_path == Path('/path/to/cert') 