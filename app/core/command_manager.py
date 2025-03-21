"""
Command manager for executing shell commands with sudo support.
"""
import subprocess
from dataclasses import dataclass
from typing import Optional, List, Union, Dict
from enum import Enum


class CommandStatus(Enum):
    """
    Enumeration of possible command execution statuses.
    """
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    INTERRUPTED = "interrupted"


@dataclass
class CommandResult:
    """
    Data class for storing command execution results.
    """
    status: CommandStatus
    return_code: int
    stdout: str
    stderr: str
    command: str
    execution_time: float
    error: Optional[str] = None


class CommandManager:
    """
    Manager for executing shell commands with sudo support.
    """
    def __init__(
        self, use_sudo: bool = False, sudo_user: Optional[str] = None
    ):
        """
        Initialize the command manager.

        Args:
            use_sudo: Whether to execute commands with sudo
            sudo_user: User to execute sudo commands as
        """
        self.use_sudo = use_sudo
        self.sudo_user = sudo_user
        self._console = None  # Will be set by DI container

    def set_console(self, console) -> None:
        """
        Set the console manager for logging.

        Args:
            console: Console manager instance
        """
        self._console = console

    def _build_command(self, command: Union[str, List[str]]) -> List[str]:
        """
        Build the command with sudo if needed.

        Args:
            command: Command to execute

        Returns:
            List of command parts
        """
        if isinstance(command, str):
            command_parts = command.split()
        else:
            command_parts = command

        if self.use_sudo:
            sudo_cmd = ["sudo"]
            if self.sudo_user:
                sudo_cmd.extend(["-u", self.sudo_user])
            return sudo_cmd + command_parts
        return command_parts

    def execute(
        self,
        command: Union[str, List[str]],
        timeout: Optional[float] = None,
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[str] = None,
        shell: bool = False
    ) -> CommandResult:
        """
        Execute a command and return the result.

        Args:
            command: Command to execute
            timeout: Command execution timeout in seconds
            env: Environment variables for command execution
            cwd: Working directory for command execution
            shell: Whether to execute command in shell

        Returns:
            CommandResult object with execution details
        """
        import time
        start_time = time.time()

        try:
            command_parts = self._build_command(command)
            
            if self._console:
                self._console.debug(
                    f"Executing command: {' '.join(command_parts)}"
                )

            process = subprocess.Popen(
                command_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=cwd,
                shell=shell,
                text=True
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                execution_time = time.time() - start_time

                if process.returncode == 0:
                    status = CommandStatus.SUCCESS
                else:
                    status = CommandStatus.FAILED

                return CommandResult(
                    status=status,
                    return_code=process.returncode,
                    stdout=stdout,
                    stderr=stderr,
                    command=" ".join(command_parts),
                    execution_time=execution_time
                )

            except subprocess.TimeoutExpired:
                process.kill()
                execution_time = time.time() - start_time
                return CommandResult(
                    status=CommandStatus.TIMEOUT,
                    return_code=-1,
                    stdout="",
                    stderr="",
                    command=" ".join(command_parts),
                    execution_time=execution_time,
                    error="Command timed out"
                )

        except Exception as e:
            execution_time = time.time() - start_time
            return CommandResult(
                status=CommandStatus.FAILED,
                return_code=-1,
                stdout="",
                stderr="",
                command=" ".join(command_parts),
                execution_time=execution_time,
                error=str(e)
            )

    def execute_sudo(
        self,
        command: Union[str, List[str]],
        sudo_user: Optional[str] = None,
        **kwargs
    ) -> CommandResult:
        """
        Execute a command with sudo.

        Args:
            command: Command to execute
            sudo_user: User to execute sudo command as
            **kwargs: Additional arguments for execute method

        Returns:
            CommandResult object with execution details
        """
        original_sudo = self.use_sudo
        original_user = self.sudo_user
        
        try:
            self.use_sudo = True
            self.sudo_user = sudo_user
            return self.execute(command, **kwargs)
        finally:
            self.use_sudo = original_sudo
            self.sudo_user = original_user 