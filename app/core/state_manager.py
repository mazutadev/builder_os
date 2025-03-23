"""
State manager module for storing and managing application state.
"""
from typing import Any, Dict


class StateManager:
    """
    Singleton class for managing application state.
    """
    _instance = None
    _state: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
        return cls._instance

    def set_state(self, key: str, value: Any) -> None:
        """
        Set a value in the state.

        Args:
            key: The key to store the value under
            value: The value to store
        """
        self._state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the state.

        Args:
            key: The key to retrieve
            default: Default value if key doesn't exist

        Returns:
            The stored value or default if not found
        """
        return self._state.get(key, default)

    def delete_state(self, key: str) -> None:
        """
        Delete a value from the state.

        Args:
            key: The key to delete
        """
        if key in self._state:
            del self._state[key]

    def clear_state(self) -> None:
        """
        Clear all state.
        """
        self._state.clear()

    @property
    def state(self) -> Dict[str, Any]:
        """
        Get the entire state dictionary.

        Returns:
            The complete state dictionary
        """
        return self._state.copy()
