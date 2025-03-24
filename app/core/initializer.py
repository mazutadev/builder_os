"""
Application initializer for setting up all core components.
"""
import os
import sys
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass
from .di_container import DIContainer
from .console import ConsoleManager
from .command_manager import CommandManager
from .state_manager import StateManager
from .exceptions import (
    ProjectRootNotFoundError,
    ConfigurationError,
    InitializationError
)


@dataclass
class EnvironmentConfig:
    """
    Configuration class for environment variables and paths.
    """
    # Базовые параметры
    app_name: str
    debug_mode: bool
    environment: str  # prod/dev/test

    # Основные пути
    project_root: Path
    python_path: str

    # Директории приложения
    app_dir: Path
    config_dir: Path
    logs_dir: Path
    tmp_dir: Path
    output_dir: Path

    # Переменные окружения
    env_vars: Dict[str, str]

    # Параметры логирования
    verbose_logging: bool
    log_level: str


class AppInitializer:
    """
    Initializes and configures all application components.
    """
    # Маркер корня проекта
    PROJECT_ROOT_MARKER = ".project_root"
    # Основной файл приложения
    MAIN_FILE = "main.py"
    # Обязательные директории
    REQUIRED_DIRS = ["config", "logs", "tmp", "output"]

    def __init__(self):
        """
        Initialize the application initializer.
        """
        self._di_container: Optional[DIContainer] = None
        self._console: Optional[ConsoleManager] = None
        self._command_manager: Optional[CommandManager] = None
        self._env_config: Optional[EnvironmentConfig] = None
        self._state_manager: Optional[StateManager] = None

    def initialize(self) -> None:
        """
        Initialize all application components.

        Raises:
            ProjectRootNotFoundError: If project root directory cannot be found
            ConfigurationError: If required directories cannot be created
        """
        try:
            self._setup_all_components()
            self._setup_environment()
            self._log_initialization_status()
        except (ProjectRootNotFoundError, ConfigurationError) as e:
            if self._console:
                self._console.error(
                    "CRITICAL ERROR: Cannot initialize application"
                )
                self._console.error(str(e))
            raise

    def _setup_all_components(self) -> None:
        """
        Setup all components.
        """
        self._setup_console()
        self._setup_state_manager()
        self._setup_command_manager()
        self._setup_di_container()
        self._add_components_to_di_container()

    def _add_components_to_di_container(self) -> None:
        """
        Add components to di container.
        """
        self._di_container.register(StateManager, self._state_manager)
        self._console.success("State manager added to di container")
        self._di_container.register(CommandManager, self._command_manager)
        self._console.success("Command manager added to di container")
        self._di_container.register(ConsoleManager, self._console)
        self._console.success("Console manager added to di container")

    def _ensure_directory(self, path: Path, dir_name: str) -> None:
        """
        Ensure directory exists and is writable.

        Args:
            path: Directory path
            dir_name: Directory name for error messages

        Raises:
            ConfigurationError: If directory cannot be created or is not
            writable
        """
        try:
            path.mkdir(exist_ok=True)
            # Проверяем права на запись, создав временный файл
            test_file = path / ".write_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            msg = (
                f"Cannot create or write to {dir_name} directory "
                f"at {path}: {str(e)}"
            )
            raise ConfigurationError(msg)

    def _setup_required_directories(
        self, project_root: Path
    ) -> Dict[str, Path]:
        """
        Setup required application directories.

        Args:
            project_root: Project root directory

        Returns:
            Dictionary with directory paths

        Raises:
            ConfigurationError: If directories cannot be created
        """
        dirs = {}

        # Настраиваем все необходимые директории
        for dir_name in self.REQUIRED_DIRS:
            dir_path = project_root / dir_name
            self._ensure_directory(dir_path, dir_name)
            dirs[f"{dir_name}_dir"] = dir_path
            self._console.debug(
                f"Initialized {dir_name} directory: {dir_path}"
            )

        # Добавляем директорию приложения
        dirs["app_dir"] = project_root / "app"

        return dirs

    def _setup_di_container(self) -> None:
        """
        Setup and configure di_container.
        """
        self._di_container = DIContainer()
        self._console.success("DI container initialized")

    def _setup_console(self) -> None:
        """
        Setup and configure console manager.
        """
        try:
            self._console = ConsoleManager()
            self._console.set_prefix("App")
            self._console.set_verbose(
                os.getenv("DEBUG", "False").lower() == "true"
            )
            self._console.success("Console manager initialized")
        except InitializationError as e:
            self._console.error(f"Error initializing console manager: {e}")
            raise

    def _setup_command_manager(self) -> None:
        """
        Setup and configure command manager.
        """
        try:
            self._command_manager = CommandManager()
            self._command_manager.set_console(self._console)
            self._console.success("Command manager initialized")
        except InitializationError as e:
            self._console.error(f"Error initializing command manager: {e}")
            raise

    def _setup_state_manager(self) -> None:
        """
        Setup and configure state manager.
        """
        try:
            self._state_manager = StateManager()
            self._console.success("State manager initialized")
        except InitializationError as e:
            self._console.error(f"Error initializing state manager: {e}")
            raise

    def _find_project_root(self) -> Path:
        """
        Find project root directory by looking for main.py or marker file.

        Returns:
            Path to project root directory

        Raises:
            ProjectRootNotFoundError: If project root directory cannot be found
        """
        # Сначала проверяем переменную окружения
        env_root = os.getenv("PROJECT_ROOT")
        if env_root:
            root_path = Path(env_root)
            if root_path.exists():
                self._console.debug("Using PROJECT_ROOT from environment")
                return root_path.resolve()
            else:
                raise ProjectRootNotFoundError(
                    f"PROJECT_ROOT path does not exist: {env_root}"
                )

        # Начинаем поиск от текущей директории
        current_dir = Path.cwd()

        # Ищем файл-маркер или main.py
        while current_dir.parent != current_dir:  # До корня файловой системы
            # Проверяем наличие файла-маркера
            marker_file = current_dir / self.PROJECT_ROOT_MARKER
            if marker_file.exists():
                self._console.debug(
                    f"Found project root by marker: {marker_file.name}"
                )
                return current_dir

            # Проверяем наличие main.py
            main_file = current_dir / self.MAIN_FILE
            if main_file.exists():
                self._console.debug(
                    f"Found project root by file: {main_file.name}"
                )
                return current_dir

            current_dir = current_dir.parent

        # Если не нашли - это критическая ошибка
        msg = (
            "Cannot find project root directory. "
            f"Make sure either {self.PROJECT_ROOT_MARKER} "
            f"or {self.MAIN_FILE} exists in the project root, "
            "or set PROJECT_ROOT environment variable."
        )
        raise ProjectRootNotFoundError(msg)

    def _setup_environment(self) -> None:
        """
        Setup environment variables and paths.

        Raises:
            ProjectRootNotFoundError: If project root cannot be found
            ConfigurationError: If required directories cannot be created
        """
        # Get project root
        project_root = self._find_project_root()

        # Setup required directories
        dirs = self._setup_required_directories(project_root)

        # Collect environment variables
        env_vars = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("_")
        }

        # Create environment config
        self._env_config = EnvironmentConfig(
            # Базовые параметры
            app_name=os.getenv("APP_NAME", "my_python_app"),
            debug_mode=os.getenv("DEBUG", "False").lower() == "true",
            environment=os.getenv("ENVIRONMENT", "dev"),

            # Основные пути
            project_root=project_root,
            python_path=sys.executable,

            # Директории приложения
            app_dir=dirs["app_dir"],
            config_dir=dirs["config_dir"],
            logs_dir=dirs["logs_dir"],
            tmp_dir=dirs["tmp_dir"],
            output_dir=dirs["output_dir"],

            # Переменные окружения
            env_vars=env_vars,

            # Параметры логирования
            verbose_logging=os.getenv("VERBOSE", "False").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO").upper()
        )

        # Store in state manager
        self._state_manager.set_state("env_config", self._env_config)

        # Log environment setup
        self._console.info("Environment configuration initialized")
        self._console.debug(f"Project root: {project_root}")
        self._console.debug(f"Environment: {self._env_config.environment}")
        self._console.debug(f"App directory: {self._env_config.app_dir}")
        self._console.debug(f"Config directory: {self._env_config.config_dir}")
        self._console.debug(f"Logs directory: {self._env_config.logs_dir}")
        self._console.debug(f"Temporary directory: {self._env_config.tmp_dir}")
        self._console.debug(f"Output directory: {self._env_config.output_dir}")
        self._console.debug(f"Log level: {self._env_config.log_level}")

    def _log_initialization_status(self) -> None:
        """
        Log the status of all initialized components.
        """
        self._console.success("Application initialization completed")
        self._console.debug("Initialized components:")
        self._console.debug("- Console Manager")
        self._console.debug("- Command Manager")
        self._console.debug("- State Manager")
        self._console.debug("- DI Container")
        self._console.debug("- Environment Configuration")

    def get_console(self) -> ConsoleManager:
        """
        Get the console manager instance.

        Returns:
            ConsoleManager instance
        """
        return self._console

    def get_command_manager(self) -> CommandManager:
        """
        Get the command manager instance.

        Returns:
            CommandManager instance
        """
        return self._command_manager

    def get_env_config(self) -> EnvironmentConfig:
        """
        Get the environment configuration.

        Returns:
            EnvironmentConfig instance
        """
        return self._env_config

    def get_state_manager(self) -> StateManager:
        """
        Get the state manager instance.
        """
        return self._state_manager

    def get_di_container(self) -> DIContainer:
        """
        Get the di container instance.
        """
        return self._di_container


# Create a global instance
app_initializer = AppInitializer()
