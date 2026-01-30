"""Input validators for network discovery."""

import re
from typing import Optional


def normalize_mac(mac_address: str) -> str:
    """
    Normalize MAC address to standard format (XX:XX:XX:XX:XX:XX).

    Args:
        mac_address: MAC address in any format

    Returns:
        Normalized MAC address

    Raises:
        ValueError: If MAC address is invalid
    """
    # Remove all separators
    mac = re.sub(r"[.:\-\s]", "", mac_address.lower())

    # Validate length
    if len(mac) != 12:
        raise ValueError(f"Invalid MAC address length: {mac_address}")

    # Validate hex characters
    if not all(c in "0123456789abcdef" for c in mac):
        raise ValueError(f"Invalid MAC address characters: {mac_address}")

    # Format as XX:XX:XX:XX:XX:XX
    return ":".join(mac[i : i + 2] for i in range(0, 12, 2))


def validate_ip(ip_address: str) -> bool:
    """
    Validate IPv4 address.

    Args:
        ip_address: IP address string

    Returns:
        True if valid, False otherwise
    """
    pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    if not pattern.match(ip_address):
        return False

    octets = ip_address.split(".")
    return all(0 <= int(octet) <= 255 for octet in octets)


def validate_hostname(hostname: str) -> bool:
    """
    Validate hostname format.

    Args:
        hostname: Hostname string

    Returns:
        True if valid, False otherwise
    """
    # Basic hostname validation
    pattern = re.compile(
        r"^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])"
        r"(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$"
    )
    return bool(pattern.match(hostname)) and len(hostname) <= 253


def parse_interface_name(interface: str) -> Optional[dict]:
    """
    Parse Cisco interface name into components.

    Args:
        interface: Interface name (e.g., "GigabitEthernet1/0/24")

    Returns:
        Dict with interface type, module, slot, port or None if invalid
    """
    # Common Cisco interface patterns
    patterns = [
        # GigabitEthernet1/0/24, TenGigabitEthernet1/0/1
        r"^(?P<type>[A-Za-z]+)(?P<module>\d+)/(?P<slot>\d+)/(?P<port>\d+)$",
        # GigabitEthernet0/1, FastEthernet0/1
        r"^(?P<type>[A-Za-z]+)(?P<module>\d+)/(?P<port>\d+)$",
        # Vlan100, Port-channel1
        r"^(?P<type>[A-Za-z\-]+)(?P<number>\d+)$",
    ]

    for pattern in patterns:
        match = re.match(pattern, interface)
        if match:
            return match.groupdict()

    return None


def abbreviate_interface(interface: str) -> str:
    """
    Abbreviate Cisco interface name.

    Args:
        interface: Full interface name

    Returns:
        Abbreviated interface name
    """
    abbreviations = {
        "GigabitEthernet": "Gi",
        "TenGigabitEthernet": "Te",
        "FastEthernet": "Fa",
        "Ethernet": "Et",
        "Port-channel": "Po",
        "Vlan": "Vl",
    }

    for full, abbr in abbreviations.items():
        if interface.startswith(full):
            return interface.replace(full, abbr)

    return interface


def expand_interface(interface: str) -> str:
    """
    Expand abbreviated Cisco interface name.

    Args:
        interface: Abbreviated interface name

    Returns:
        Full interface name
    """
    expansions = {
        "Gi": "GigabitEthernet",
        "Te": "TenGigabitEthernet",
        "Fa": "FastEthernet",
        "Et": "Ethernet",
        "Po": "Port-channel",
        "Vl": "Vlan",
    }

    for abbr, full in expansions.items():
        if interface.startswith(abbr):
            return interface.replace(abbr, full, 1)

    return interface
