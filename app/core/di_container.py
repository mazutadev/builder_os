"""
Dependency Injection Container for managing global application objects.
"""
from typing import Any, Dict, Type, TypeVar, Optional


T = TypeVar('T')


class DIContainer:
    """
    Singleton class for managing application dependencies.
    """
    _instance = None
    _services: Dict[str, Any] = {}
    _factories: Dict[str, callable] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DIContainer, cls).__new__(cls)
        return cls._instance

    def register(self, service_type: Type[T], instance: T) -> None:
        """
        Register a service instance.

        Args:
            service_type: The type of the service
            instance: The service instance to register
        """
        self._services[service_type.__name__] = instance

    def register_factory(
        self, service_type: Type[T], factory: callable
    ) -> None:
        """
        Register a factory function for creating service instances.

        Args:
            service_type: The type of the service
            factory: Factory function that creates service instances
        """
        self._factories[service_type.__name__] = factory

    def get(self, service_type: Type[T]) -> Optional[T]:
        """
        Get a service instance by type.

        Args:
            service_type: The type of the service to retrieve

        Returns:
            The service instance if found, None otherwise
        """
        service_name = service_type.__name__

        # Check if we have a registered instance
        if service_name in self._services:
            return self._services[service_name]

        # Check if we have a factory
        if service_name in self._factories:
            instance = self._factories[service_name]()
            self._services[service_name] = instance
            return instance

        return None

    def remove(self, service_type: Type[T]) -> None:
        """
        Remove a service from the container.

        Args:
            service_type: The type of the service to remove
        """
        service_name = service_type.__name__
        if service_name in self._services:
            del self._services[service_name]
        if service_name in self._factories:
            del self._factories[service_name]

    def clear(self) -> None:
        """
        Clear all registered services and factories.
        """
        self._services.clear()
        self._factories.clear()
