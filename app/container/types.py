from enum import Enum
from typing import Dict, Optional, Any
from dataclasses import dataclass


class ContainerType(Enum):
    """Container status types"""
    CREATED = "created"
    RUNNING = "running"
    EXITED = "exited"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    ERROR = "error"
    UNKNOWN = "unknown"


class OSType(Enum):
    """Operating system types"""
    UBUNTU = "ubuntu"
    DEBIAN = "debian"
    CENTOS = "centos"
    ALPINE = "alpine"


@dataclass
class ContainerConfig:
    """Container configuration settings"""
    os_type: OSType
    os_version: Optional[str] = None
    name: Optional[str] = None
    volumes: Optional[Dict[str, str]] = None
    environment: Optional[Dict[str, str]] = None
    working_dir: Optional[str] = None
    command: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContainerConfig':
        """Create ContainerConfig from dictionary"""
        return cls(
            os_type=OSType(data['os_type']),
            os_version=data.get('os_version'),
            name=data.get('name'),
            volumes=data.get('volumes'),
            environment=data.get('environment'),
            working_dir=data.get('working_dir'),
            command=data.get('command')
        )
