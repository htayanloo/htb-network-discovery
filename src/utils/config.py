"""Configuration management for network discovery."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DeviceConfig(BaseModel):
    """Configuration for a network device."""
    hostname: str
    ip: str
    device_type: str = "cisco_ios"
    username: Optional[str] = None
    password: Optional[str] = None
    port: int = 22
    secret: Optional[str] = None  # Enable password


class CredentialsConfig(BaseModel):
    """Default credentials configuration."""
    username: str = Field(default_factory=lambda: os.getenv("SSH_USERNAME", "admin"))
    password: str = Field(default_factory=lambda: os.getenv("SSH_PASSWORD", ""))
    use_keys: bool = False
    key_file: Optional[str] = None


class DiscoveryOptions(BaseModel):
    """Discovery configuration options."""
    recursive: bool = True
    max_depth: int = 10
    timeout: int = 30
    banner_timeout: int = 15
    collect_mac_tables: bool = True
    collect_arp_tables: bool = False
    collect_interface_stats: bool = True
    protocols: List[str] = ["cdp", "lldp"]


class FilterConfig(BaseModel):
    """Device filtering configuration."""
    exclude_hostnames: List[str] = []
    include_types: Optional[List[str]] = None


class ParallelConfig(BaseModel):
    """Parallel processing configuration."""
    max_workers: int = 5
    queue_size: int = 100


class NetworkConfig(BaseModel):
    """Complete network discovery configuration."""
    seed_devices: List[DeviceConfig]
    credentials: CredentialsConfig = Field(default_factory=CredentialsConfig)
    discovery_options: DiscoveryOptions = Field(default_factory=DiscoveryOptions)
    filters: FilterConfig = Field(default_factory=FilterConfig)
    parallel: ParallelConfig = Field(default_factory=ParallelConfig)

    @validator("seed_devices")
    def validate_seed_devices(cls, v):
        """Ensure at least one seed device is configured."""
        if not v:
            raise ValueError("At least one seed device must be configured")
        return v


class AppConfig:
    """Application configuration manager."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path or os.getenv(
            "CONFIG_PATH", "config/devices.yaml"
        )
        self._config: Optional[NetworkConfig] = None

    def load(self) -> NetworkConfig:
        """
        Load configuration from YAML file.

        Returns:
            NetworkConfig: Parsed and validated configuration

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If configuration is invalid
        """
        config_file = Path(self.config_path)

        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_file}\n"
                f"Copy config/devices.yaml.example to {config_file} and configure your devices."
            )

        with open(config_file, "r") as f:
            data = yaml.safe_load(f)

        self._config = NetworkConfig(**data)
        return self._config

    @property
    def config(self) -> NetworkConfig:
        """Get loaded configuration."""
        if self._config is None:
            self.load()
        return self._config

    def get_device_credentials(self, device: DeviceConfig) -> Dict[str, Any]:
        """
        Get complete credentials for a device.

        Args:
            device: Device configuration

        Returns:
            Dict with username, password, and other connection parameters
        """
        username = device.username or self.config.credentials.username
        password = device.password or self.config.credentials.password

        credentials = {
            "device_type": device.device_type,
            "host": device.ip,
            "username": username,
            "password": password,
            "port": device.port,
            "timeout": self.config.discovery_options.timeout,
            "banner_timeout": self.config.discovery_options.banner_timeout,
        }

        # Add enable password if configured
        if device.secret:
            credentials["secret"] = device.secret

        # Add SSH key if configured
        if self.config.credentials.use_keys and self.config.credentials.key_file:
            credentials["use_keys"] = True
            credentials["key_file"] = os.path.expanduser(
                self.config.credentials.key_file
            )

        return credentials


# Singleton instance
_config_instance: Optional[AppConfig] = None


def get_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Get configuration singleton instance.

    Args:
        config_path: Optional path to configuration file

    Returns:
        AppConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig(config_path)
    return _config_instance


# Database configuration
def get_database_url() -> str:
    """Get database URL from environment or use default."""
    return os.getenv("DATABASE_URL", "sqlite:///network_discovery.db")


# API configuration
def get_api_config() -> Dict[str, Any]:
    """Get API server configuration."""
    return {
        "host": os.getenv("API_HOST", "0.0.0.0"),
        "port": int(os.getenv("API_PORT", "5000")),
        "debug": os.getenv("API_DEBUG", "false").lower() == "true",
    }


# Logging configuration
def get_log_config() -> Dict[str, Any]:
    """Get logging configuration."""
    return {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "file": os.getenv("LOG_FILE", "logs/discovery.log"),
    }
