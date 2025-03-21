"""
Application-wide exceptions.
"""


class ApplicationError(Exception):
    """Base exception for all application errors."""
    pass


class InitializationError(ApplicationError):
    """Base exception for initialization errors."""
    pass


class ProjectRootNotFoundError(InitializationError):
    """Exception raised when project root directory cannot be found."""
    pass


class ConfigurationError(InitializationError):
    """Exception raised when there is a configuration error."""
    pass


class ServiceNotFoundError(InitializationError):
    """Exception raised when a required service is not found."""
    pass


class StateError(ApplicationError):
    """Exception raised when there is a state management error."""
    pass


class CommandError(ApplicationError):
    """Exception raised when there is a command execution error."""
    pass 