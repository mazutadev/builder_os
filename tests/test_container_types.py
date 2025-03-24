"""Unit tests for container types and exceptions"""

import pytest
from app.container.types import ContainerConfig, OSType, ContainerStatus
from app.container.exceptions import (
    ContainerError,
    ContainerCreateError,
    ContainerStartError,
    ContainerStopError,
    ContainerExecuteError,
    ContainerNotFoundError,
    ContainerConfigError,
    ContainerRestartError,
    ContainerRemoveError,
)


def test_container_config_creation():
    """Test ContainerConfig creation"""
    config = ContainerConfig(
        os_type=OSType.UBUNTU,
        os_version='22.04',
        name='test-container',
        environment={'TEST': 'value'},
        working_dir='/app'
    )

    assert config.os_type == OSType.UBUNTU
    assert config.os_version == '22.04'
    assert config.name == 'test-container'
    assert config.environment == {'TEST': 'value'}
    assert config.working_dir == '/app'
    assert config.volumes == {}


def test_container_config_optional_fields():
    """Test ContainerConfig with optional fields"""
    config = ContainerConfig(
        os_type=OSType.UBUNTU,
        os_version='22.04'
    )

    assert config.os_type == OSType.UBUNTU
    assert config.os_version == '22.04'
    assert config.name is None
    assert config.environment == {}
    assert config.working_dir is None
    assert config.volumes == {}


def test_os_type_values():
    """Test OSType enum values"""
    assert OSType.UBUNTU.value == 'ubuntu'
    assert OSType.DEBIAN.value == 'debian'
    assert OSType.CENTOS.value == 'centos'
    assert OSType.FEDORA.value == 'fedora'
    assert OSType.ALPINE.value == 'alpine'


def test_container_status_values():
    """Test ContainerStatus enum values"""
    assert ContainerStatus.CREATED.value == 'created'
    assert ContainerStatus.RUNNING.value == 'running'
    assert ContainerStatus.STOPPED.value == 'stopped'
    assert ContainerStatus.PAUSED.value == 'paused'
    assert ContainerStatus.RESTARTING.value == 'restarting'
    assert ContainerStatus.REMOVING.value == 'removing'
    assert ContainerStatus.EXITED.value == 'exited'
    assert ContainerStatus.DEAD.value == 'dead'
    assert ContainerStatus.FAILED.value == 'failed'


def test_container_error():
    """Test ContainerError exception"""
    error = ContainerError("Test error")
    assert str(error) == "Test error"


def test_container_create_error():
    """Test ContainerCreateError exception"""
    error = ContainerCreateError("Failed to create container")
    assert str(error) == "Failed to create container"
    assert isinstance(error, ContainerError)


def test_container_start_error():
    """Test ContainerStartError exception"""
    error = ContainerStartError("Failed to start container")
    assert str(error) == "Failed to start container"
    assert isinstance(error, ContainerError)


def test_container_stop_error():
    """Test ContainerStopError exception"""
    error = ContainerStopError("Failed to stop container")
    assert str(error) == "Failed to stop container"
    assert isinstance(error, ContainerError)


def test_container_execute_error():
    """Test ContainerExecuteError exception"""
    error = ContainerExecuteError("Failed to execute command")
    assert str(error) == "Failed to execute command"
    assert isinstance(error, ContainerError)


def test_container_not_found_error():
    """Test ContainerNotFoundError exception"""
    error = ContainerNotFoundError("Container not found")
    assert str(error) == "Container not found"
    assert isinstance(error, ContainerError)


def test_container_config_error():
    """Test ContainerConfigError exception"""
    error = ContainerConfigError("Invalid configuration")
    assert str(error) == "Invalid configuration"
    assert isinstance(error, ContainerError)


def test_container_restart_error():
    """Test ContainerRestartError exception"""
    error = ContainerRestartError("Failed to restart container")
    assert str(error) == "Failed to restart container"
    assert isinstance(error, ContainerError)


def test_container_remove_error():
    """Test ContainerRemoveError exception"""
    error = ContainerRemoveError("Failed to remove container")
    assert str(error) == "Failed to remove container"
    assert isinstance(error, ContainerError) 