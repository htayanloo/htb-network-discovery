"""Data collectors for network discovery."""

from typing import Dict, Any, List, Optional
from core.discovery.ssh_client import SSHClient
from core.discovery.parsers import CiscoParser
from core.models.device import DeviceInfo, InterfaceInfo, NeighborInfo, MacEntry, VlanInfo
from utils.logger import get_logger

logger = get_logger(__name__)


class DeviceCollector:
    """Collector for gathering device information."""

    def __init__(self, ssh_client: SSHClient):
        """
        Initialize collector with SSH client.

        Args:
            ssh_client: Connected SSH client
        """
        self.client = ssh_client
        self.parser = CiscoParser()

    def collect_device_info(self) -> Optional[DeviceInfo]:
        """
        Collect basic device information.

        Returns:
            DeviceInfo object or None if collection failed
        """
        try:
            # Get version information
            version_output = self.client.execute_command("show version")
            version_data = self.parser.parse_version(version_output)

            if not version_data.get("hostname"):
                logger.warning(f"Could not determine hostname for {self.client.host}")
                version_data["hostname"] = self.client.host

            device_info = DeviceInfo(
                hostname=version_data.get("hostname", self.client.host),
                ip_address=self.client.host,
                device_type="switch",  # Default, can be refined
                model=version_data.get("model"),
                ios_version=version_data.get("ios_version"),
                serial_number=version_data.get("serial_number"),
                uptime=version_data.get("uptime"),
            )

            logger.info(f"Collected device info for {device_info.hostname}")
            return device_info

        except Exception as e:
            logger.error(f"Failed to collect device info from {self.client.host}: {e}")
            return None

    def collect_interfaces(self) -> List[InterfaceInfo]:
        """
        Collect interface information.

        Returns:
            List of InterfaceInfo objects
        """
        interfaces = []

        try:
            # Get interface status
            status_output = self.client.execute_command("show interfaces status")
            status_data = self.parser.parse_interfaces_status(status_output)

            # Get trunk information
            trunk_output = self.client.execute_command("show interfaces trunk")
            trunk_data = self.parser.parse_interfaces_trunk(trunk_output)

            # Combine interface data
            for intf_data in status_data:
                name = intf_data["name"]

                # Check if this is a trunk port
                trunk_vlans = trunk_data.get(name)
                if trunk_vlans:
                    intf_data["is_trunk"] = True
                    intf_data["trunk_vlans"] = trunk_vlans

                interface = InterfaceInfo(**intf_data)
                interfaces.append(interface)

            logger.info(
                f"Collected {len(interfaces)} interfaces from {self.client.host}"
            )

        except Exception as e:
            logger.error(f"Failed to collect interfaces from {self.client.host}: {e}")

        return interfaces

    def collect_neighbors(self) -> List[NeighborInfo]:
        """
        Collect CDP/LLDP neighbor information.

        Returns:
            List of NeighborInfo objects
        """
        neighbors = []

        # Try CDP first
        try:
            cdp_output = self.client.execute_command("show cdp neighbors detail")
            cdp_data = self.parser.parse_cdp_neighbors(cdp_output)

            for neighbor_data in cdp_data:
                neighbor = NeighborInfo(**neighbor_data)
                neighbors.append(neighbor)

            logger.info(
                f"Collected {len(neighbors)} CDP neighbors from {self.client.host}"
            )

        except Exception as e:
            logger.warning(f"Failed to collect CDP neighbors from {self.client.host}: {e}")

        # Try LLDP if CDP didn't work or found nothing
        if not neighbors:
            try:
                lldp_output = self.client.execute_command("show lldp neighbors detail")
                lldp_data = self.parser.parse_lldp_neighbors(lldp_output)

                for neighbor_data in lldp_data:
                    neighbor = NeighborInfo(**neighbor_data)
                    neighbors.append(neighbor)

                logger.info(
                    f"Collected {len(neighbors)} LLDP neighbors from {self.client.host}"
                )

            except Exception as e:
                logger.warning(
                    f"Failed to collect LLDP neighbors from {self.client.host}: {e}"
                )

        return neighbors

    def collect_mac_table(self) -> List[MacEntry]:
        """
        Collect MAC address table.

        Returns:
            List of MacEntry objects
        """
        mac_entries = []

        try:
            mac_output = self.client.execute_command("show mac address-table")
            mac_data = self.parser.parse_mac_address_table(mac_output)

            for entry_data in mac_data:
                mac_entry = MacEntry(**entry_data)
                mac_entries.append(mac_entry)

            logger.info(
                f"Collected {len(mac_entries)} MAC entries from {self.client.host}"
            )

        except Exception as e:
            logger.error(
                f"Failed to collect MAC table from {self.client.host}: {e}"
            )

        return mac_entries

    def collect_vlans(self) -> List[VlanInfo]:
        """
        Collect VLAN information.

        Returns:
            List of VlanInfo objects
        """
        vlans = []

        try:
            vlan_output = self.client.execute_command("show vlan brief")
            vlan_data = self.parser.parse_vlans(vlan_output)

            for vlan_entry in vlan_data:
                vlan = VlanInfo(**vlan_entry)
                vlans.append(vlan)

            logger.info(f"Collected {len(vlans)} VLANs from {self.client.host}")

        except Exception as e:
            logger.error(f"Failed to collect VLANs from {self.client.host}: {e}")

        return vlans

    def collect_all(self, collect_mac_tables: bool = True) -> Optional[DeviceInfo]:
        """
        Collect all available information from device.

        Args:
            collect_mac_tables: Whether to collect MAC address tables

        Returns:
            Complete DeviceInfo object or None if collection failed
        """
        logger.info(f"Starting full collection from {self.client.host}")

        # Collect basic device info
        device_info = self.collect_device_info()
        if not device_info:
            return None

        # Collect interfaces
        device_info.interfaces = self.collect_interfaces()

        # Collect neighbors
        neighbors = self.collect_neighbors()
        device_info.neighbors = [n.to_dict() for n in neighbors]

        # Collect MAC table if requested
        if collect_mac_tables:
            mac_entries = self.collect_mac_table()
            device_info.mac_table = [m.to_dict() for m in mac_entries]

        # Collect VLANs
        vlans = self.collect_vlans()
        device_info.vlans = [v.to_dict() for v in vlans]

        logger.info(
            f"Completed collection from {device_info.hostname}: "
            f"{len(device_info.interfaces)} interfaces, "
            f"{len(device_info.neighbors)} neighbors, "
            f"{len(device_info.mac_table)} MAC entries"
        )

        return device_info


class NetworkDiscoveryCollector:
    """High-level collector for network-wide discovery."""

    def __init__(self, connection_params: Dict[str, Any]):
        """
        Initialize network collector.

        Args:
            connection_params: SSH connection parameters
        """
        self.connection_params = connection_params

    def collect_from_device(
        self, collect_mac_tables: bool = True
    ) -> Optional[DeviceInfo]:
        """
        Collect information from a single device.

        Args:
            collect_mac_tables: Whether to collect MAC address tables

        Returns:
            DeviceInfo object or None if collection failed
        """
        try:
            with SSHClient(**self.connection_params) as client:
                if not client.is_connected():
                    logger.error(
                        f"Failed to connect to {self.connection_params['host']}"
                    )
                    return None

                collector = DeviceCollector(client)
                return collector.collect_all(collect_mac_tables=collect_mac_tables)

        except Exception as e:
            logger.error(
                f"Error collecting from {self.connection_params['host']}: {e}"
            )
            return None
