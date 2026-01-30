"""SSH client for connecting to network devices."""

import time
from typing import Dict, Any, Optional, List
from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
    SSHException,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class SSHClient:
    """SSH client for network device connections."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        device_type: str = "cisco_ios",
        port: int = 22,
        timeout: int = 30,
        banner_timeout: int = 15,
        **kwargs,
    ):
        """
        Initialize SSH client.

        Args:
            host: Device IP address or hostname
            username: SSH username
            password: SSH password
            device_type: Device type for Netmiko (default: cisco_ios)
            port: SSH port (default: 22)
            timeout: Connection timeout in seconds
            banner_timeout: Banner timeout in seconds
            **kwargs: Additional Netmiko connection parameters
        """
        self.host = host
        self.username = username
        self.device_type = device_type
        self.port = port
        self.timeout = timeout

        self.connection_params = {
            "device_type": device_type,
            "host": host,
            "username": username,
            "password": password,
            "port": port,
            "timeout": timeout,
            "banner_timeout": banner_timeout,
            "fast_cli": True,  # Enable fast CLI mode
            "session_log": None,  # Can be set to log file path for debugging
            **kwargs,
        }

        self.connection: Optional[ConnectHandler] = None
        self._connected = False

    def connect(self) -> bool:
        """
        Establish SSH connection to device.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to {self.host} ({self.device_type})...")
            self.connection = ConnectHandler(**self.connection_params)
            self._connected = True
            logger.info(f"Successfully connected to {self.host}")
            return True

        except NetmikoAuthenticationException as e:
            logger.error(f"Authentication failed for {self.host}: {e}")
            return False

        except NetmikoTimeoutException as e:
            logger.error(f"Connection timeout to {self.host}: {e}")
            return False

        except SSHException as e:
            logger.error(f"SSH error connecting to {self.host}: {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error connecting to {self.host}: {e}")
            return False

    def disconnect(self):
        """Close SSH connection."""
        if self.connection and self._connected:
            try:
                self.connection.disconnect()
                logger.info(f"Disconnected from {self.host}")
            except Exception as e:
                logger.warning(f"Error disconnecting from {self.host}: {e}")
            finally:
                self._connected = False

    def execute_command(
        self, command: str, delay_factor: int = 1, max_loops: int = 150
    ) -> str:
        """
        Execute a command on the device.

        Args:
            command: Command to execute
            delay_factor: Multiplier for delays (for slower devices)
            max_loops: Maximum number of loops to wait for output

        Returns:
            Command output as string

        Raises:
            ConnectionError: If not connected to device
        """
        if not self._connected or not self.connection:
            raise ConnectionError(f"Not connected to {self.host}")

        try:
            logger.debug(f"Executing command on {self.host}: {command}")
            output = self.connection.send_command(
                command, delay_factor=delay_factor, max_loops=max_loops
            )
            return output

        except Exception as e:
            logger.error(f"Error executing command '{command}' on {self.host}: {e}")
            raise

    def execute_commands(self, commands: List[str]) -> Dict[str, str]:
        """
        Execute multiple commands on the device.

        Args:
            commands: List of commands to execute

        Returns:
            Dictionary mapping command to output
        """
        results = {}

        for command in commands:
            try:
                output = self.execute_command(command)
                results[command] = output
            except Exception as e:
                logger.error(f"Failed to execute '{command}': {e}")
                results[command] = f"ERROR: {str(e)}"

        return results

    def enable_mode(self, enable_password: Optional[str] = None):
        """
        Enter enable mode on device.

        Args:
            enable_password: Enable password (if required)
        """
        if not self._connected or not self.connection:
            raise ConnectionError(f"Not connected to {self.host}")

        try:
            if enable_password:
                self.connection.enable(cmd="enable", pattern="password", re_flags=0)
                self.connection.send_command(
                    enable_password, expect_string=r"#", strip_prompt=False
                )
            else:
                self.connection.enable()
            logger.debug(f"Entered enable mode on {self.host}")

        except Exception as e:
            logger.warning(f"Could not enter enable mode on {self.host}: {e}")

    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self._connected and self.connection is not None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def __repr__(self):
        """String representation."""
        status = "connected" if self._connected else "disconnected"
        return f"<SSHClient({self.host}, {status})>"


class SSHConnectionPool:
    """Pool of SSH connections for parallel processing."""

    def __init__(self, max_connections: int = 5):
        """
        Initialize connection pool.

        Args:
            max_connections: Maximum number of concurrent connections
        """
        self.max_connections = max_connections
        self.connections: Dict[str, SSHClient] = {}
        self._active_count = 0

    def get_connection(self, connection_params: Dict[str, Any]) -> Optional[SSHClient]:
        """
        Get or create a connection from the pool.

        Args:
            connection_params: Connection parameters

        Returns:
            SSHClient instance or None if connection failed
        """
        host = connection_params.get("host")

        # Check if already connected
        if host in self.connections:
            client = self.connections[host]
            if client.is_connected():
                return client
            else:
                # Remove stale connection
                del self.connections[host]

        # Wait if pool is full
        while self._active_count >= self.max_connections:
            time.sleep(0.1)

        # Create new connection
        client = SSHClient(**connection_params)
        if client.connect():
            self.connections[host] = client
            self._active_count += 1
            return client
        else:
            return None

    def release_connection(self, host: str):
        """Release a connection back to the pool."""
        if host in self.connections:
            self.connections[host].disconnect()
            del self.connections[host]
            self._active_count = max(0, self._active_count - 1)

    def close_all(self):
        """Close all connections in the pool."""
        for host in list(self.connections.keys()):
            self.release_connection(host)

    def __del__(self):
        """Cleanup on deletion."""
        self.close_all()
