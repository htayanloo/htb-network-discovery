"""CLI output parsers for Cisco commands."""

import re
from typing import List, Dict, Any, Optional
from utils.logger import get_logger
from utils.validators import normalize_mac

logger = get_logger(__name__)


class CiscoParser:
    """Parser for Cisco IOS command outputs."""

    @staticmethod
    def parse_version(output: str) -> Dict[str, Any]:
        """
        Parse 'show version' output.

        Args:
            output: Command output

        Returns:
            Dictionary with version information
        """
        info = {
            "hostname": None,
            "model": None,
            "ios_version": None,
            "serial_number": None,
            "uptime": None,
        }

        # Parse hostname
        hostname_match = re.search(r"^(\S+)\s+uptime", output, re.MULTILINE)
        if hostname_match:
            info["hostname"] = hostname_match.group(1)

        # Parse model/platform
        model_patterns = [
            r"cisco\s+(\S+)\s+\(.*?\)\s+processor",
            r"Model\s+[Nn]umber\s*:\s*(\S+)",
            r"cisco\s+([A-Z0-9\-]+)\s+",
        ]
        for pattern in model_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                info["model"] = match.group(1)
                break

        # Parse IOS version
        version_patterns = [
            r"Version\s+([\d.]+[A-Z0-9().,\-\s]+)",
            r"Cisco\s+IOS.*?Version\s+([\d.]+)",
        ]
        for pattern in version_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                info["ios_version"] = match.group(1).strip()
                break

        # Parse serial number
        serial_patterns = [
            r"Processor\s+board\s+ID\s+(\S+)",
            r"System\s+[Ss]erial\s+[Nn]umber\s*:\s*(\S+)",
        ]
        for pattern in serial_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                info["serial_number"] = match.group(1)
                break

        # Parse uptime
        uptime_match = re.search(
            r"uptime\s+is\s+(.*?)(?:\n|$)", output, re.IGNORECASE
        )
        if uptime_match:
            info["uptime"] = uptime_match.group(1).strip()

        return info

    @staticmethod
    def parse_cdp_neighbors(output: str) -> List[Dict[str, Any]]:
        """
        Parse 'show cdp neighbors detail' output.

        Args:
            output: Command output

        Returns:
            List of neighbor dictionaries
        """
        neighbors = []

        # Split by device entries (starts with "Device ID:")
        entries = re.split(r"^-+\s*$", output, flags=re.MULTILINE)

        for entry in entries:
            if "Device ID:" not in entry:
                continue

            neighbor = {}

            # Device ID
            device_id_match = re.search(
                r"Device\s+ID:\s*(\S+)", entry, re.IGNORECASE
            )
            if device_id_match:
                neighbor["remote_device"] = device_id_match.group(1)

            # IP Address
            ip_match = re.search(
                r"IP\s+[Aa]ddress:\s*([\d.]+)", entry
            )
            if ip_match:
                neighbor["remote_ip"] = ip_match.group(1)

            # Platform
            platform_match = re.search(
                r"Platform:\s*([^,]+)", entry, re.IGNORECASE
            )
            if platform_match:
                neighbor["platform"] = platform_match.group(1).strip()

            # Capabilities
            cap_match = re.search(
                r"Capabilities:\s*([^\n]+)", entry, re.IGNORECASE
            )
            if cap_match:
                capabilities = cap_match.group(1).strip()
                neighbor["capabilities"] = [c.strip() for c in capabilities.split()]

            # Local Interface
            local_int_match = re.search(
                r"Interface:\s*(\S+)", entry, re.IGNORECASE
            )
            if local_int_match:
                neighbor["local_interface"] = local_int_match.group(1).rstrip(",")

            # Remote Interface (Port ID)
            remote_int_match = re.search(
                r"Port\s+ID\s*\(outgoing\s+port\):\s*(\S+)", entry, re.IGNORECASE
            )
            if remote_int_match:
                neighbor["remote_interface"] = remote_int_match.group(1)

            neighbor["protocol"] = "cdp"

            if neighbor.get("remote_device"):
                neighbors.append(neighbor)

        return neighbors

    @staticmethod
    def parse_lldp_neighbors(output: str) -> List[Dict[str, Any]]:
        """
        Parse 'show lldp neighbors detail' output.

        Args:
            output: Command output

        Returns:
            List of neighbor dictionaries
        """
        neighbors = []

        # Split by device entries
        entries = re.split(r"^-+\s*$", output, flags=re.MULTILINE)

        for entry in entries:
            if "System Name:" not in entry and "Chassis id:" not in entry:
                continue

            neighbor = {}

            # System Name
            name_match = re.search(
                r"System\s+Name:\s*(\S+)", entry, re.IGNORECASE
            )
            if name_match:
                neighbor["remote_device"] = name_match.group(1)

            # Management Address
            ip_match = re.search(
                r"Management\s+Addresses.*?\n\s+IP:\s*([\d.]+)",
                entry,
                re.IGNORECASE | re.DOTALL,
            )
            if ip_match:
                neighbor["remote_ip"] = ip_match.group(1)

            # System Description (Platform)
            desc_match = re.search(
                r"System\s+Description:\s*\n\s*([^\n]+)", entry, re.IGNORECASE
            )
            if desc_match:
                neighbor["platform"] = desc_match.group(1).strip()

            # Capabilities
            cap_match = re.search(
                r"System\s+Capabilities:\s*([^\n]+)", entry, re.IGNORECASE
            )
            if cap_match:
                capabilities = cap_match.group(1).strip()
                neighbor["capabilities"] = [c.strip() for c in capabilities.split(",")]

            # Local Interface
            local_int_match = re.search(
                r"Local\s+Intf:\s*(\S+)", entry, re.IGNORECASE
            )
            if local_int_match:
                neighbor["local_interface"] = local_int_match.group(1)

            # Remote Interface (Port id)
            remote_int_match = re.search(
                r"Port\s+id:\s*(\S+)", entry, re.IGNORECASE
            )
            if remote_int_match:
                neighbor["remote_interface"] = remote_int_match.group(1)

            neighbor["protocol"] = "lldp"

            if neighbor.get("remote_device"):
                neighbors.append(neighbor)

        return neighbors

    @staticmethod
    def parse_mac_address_table(output: str) -> List[Dict[str, Any]]:
        """
        Parse 'show mac address-table' output.

        Args:
            output: Command output

        Returns:
            List of MAC entry dictionaries
        """
        mac_entries = []

        # Pattern for MAC table entries
        # Format: VLAN  MAC Address       Type      Ports
        # Example: 100   0050.7966.6801   DYNAMIC   Gi1/0/1
        pattern = re.compile(
            r"^\s*(\d+)\s+"  # VLAN
            r"([0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})\s+"  # MAC
            r"(\w+)\s+"  # Type
            r"(\S+)",  # Interface
            re.MULTILINE,
        )

        for match in pattern.finditer(output):
            vlan_id = int(match.group(1))
            mac_address = match.group(2)
            entry_type = match.group(3).lower()
            interface = match.group(4)

            try:
                # Normalize MAC address
                normalized_mac = normalize_mac(mac_address)

                mac_entries.append(
                    {
                        "vlan_id": vlan_id,
                        "mac_address": normalized_mac,
                        "type": entry_type,
                        "interface": interface,
                    }
                )
            except ValueError as e:
                logger.warning(f"Invalid MAC address: {mac_address}: {e}")

        return mac_entries

    @staticmethod
    def parse_interfaces_status(output: str) -> List[Dict[str, Any]]:
        """
        Parse 'show interfaces status' output.

        Args:
            output: Command output

        Returns:
            List of interface dictionaries
        """
        interfaces = []

        # Pattern for interface status
        # Format: Port  Name  Status  Vlan  Duplex  Speed  Type
        pattern = re.compile(
            r"^(\S+)\s+"  # Interface name
            r"(.*?)\s+"  # Description (may be empty)
            r"(connected|notconnect|disabled|err-disabled)\s+"  # Status
            r"(\d+|trunk|routed)\s+"  # VLAN
            r"(\S+)\s+"  # Duplex
            r"(\S+)\s*"  # Speed
            r"(.*)$",  # Type
            re.MULTILINE,
        )

        for match in pattern.finditer(output):
            name = match.group(1)
            description = match.group(2).strip() or None
            status = match.group(3)
            vlan = match.group(4)
            duplex = match.group(5)
            speed = match.group(6)

            # Parse VLAN
            is_trunk = vlan == "trunk"
            vlan_id = None
            if vlan.isdigit():
                vlan_id = int(vlan)

            interfaces.append(
                {
                    "name": name,
                    "description": description,
                    "status": "up" if status == "connected" else "down",
                    "vlan_id": vlan_id,
                    "is_trunk": is_trunk,
                    "duplex": duplex if duplex != "auto" else None,
                    "speed": speed if speed not in ["auto", "a-"] else None,
                }
            )

        return interfaces

    @staticmethod
    def parse_interfaces_trunk(output: str) -> Dict[str, List[int]]:
        """
        Parse 'show interfaces trunk' output.

        Args:
            output: Command output

        Returns:
            Dictionary mapping interface to list of allowed VLANs
        """
        trunk_vlans = {}

        # Find the section with allowed VLANs
        allowed_section = re.search(
            r"Port\s+Vlans allowed on trunk\s*\n(.+?)(?:\n\n|\Z)",
            output,
            re.DOTALL | re.IGNORECASE,
        )

        if not allowed_section:
            return trunk_vlans

        # Parse each line in the allowed VLANs section
        for line in allowed_section.group(1).split("\n"):
            match = re.match(r"^(\S+)\s+(.+)$", line.strip())
            if match:
                interface = match.group(1)
                vlans_str = match.group(2).strip()

                # Parse VLAN list (e.g., "1-4094" or "10,20,30-40")
                vlans = CiscoParser._parse_vlan_list(vlans_str)
                trunk_vlans[interface] = vlans

        return trunk_vlans

    @staticmethod
    def _parse_vlan_list(vlan_str: str) -> List[int]:
        """
        Parse VLAN list string into list of VLAN IDs.

        Args:
            vlan_str: VLAN string (e.g., "1-4094" or "10,20,30-40")

        Returns:
            List of VLAN IDs
        """
        vlans = []

        # Split by comma
        parts = vlan_str.split(",")

        for part in parts:
            part = part.strip()

            if "-" in part:
                # Range (e.g., "10-20")
                try:
                    start, end = part.split("-")
                    start = int(start.strip())
                    end = int(end.strip())
                    vlans.extend(range(start, end + 1))
                except (ValueError, AttributeError):
                    pass
            else:
                # Single VLAN
                try:
                    vlans.append(int(part))
                except ValueError:
                    pass

        return sorted(set(vlans))  # Remove duplicates and sort

    @staticmethod
    def parse_vlans(output: str) -> List[Dict[str, Any]]:
        """
        Parse 'show vlan brief' output.

        Args:
            output: Command output

        Returns:
            List of VLAN dictionaries
        """
        vlans = []

        # Pattern for VLAN entries
        # Format: VLAN  Name  Status  Ports
        pattern = re.compile(
            r"^(\d+)\s+"  # VLAN ID
            r"(\S+)\s+"  # Name
            r"(active|suspended|act/lshut|sus/lshut)",  # Status
            re.MULTILINE | re.IGNORECASE,
        )

        for match in pattern.finditer(output):
            vlan_id = int(match.group(1))
            name = match.group(2)
            status = match.group(3).lower()

            vlans.append(
                {
                    "vlan_id": vlan_id,
                    "name": name,
                    "status": "active" if "active" in status else "suspended",
                }
            )

        return vlans
