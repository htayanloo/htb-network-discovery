"""Network discovery engine - orchestrates the discovery process."""

from typing import Dict, Any, List, Set, Optional
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from core.discovery.collectors import NetworkDiscoveryCollector
from core.models.device import DeviceInfo
from database.schema import create_database, get_session
from database.repository import (
    DeviceRepository,
    InterfaceRepository,
    ConnectionRepository,
    MacRepository,
    VlanRepository,
    DiscoverySessionRepository,
)
from utils.config import get_config, get_database_url, DeviceConfig
from utils.logger import get_logger

logger = get_logger(__name__)


class DiscoveryEngine:
    """Main discovery engine for network topology discovery."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        max_depth: Optional[int] = None,
        max_workers: Optional[int] = None,
    ):
        """
        Initialize discovery engine.

        Args:
            config_path: Path to configuration file
            max_depth: Maximum recursion depth (overrides config)
            max_workers: Maximum parallel workers (overrides config)
        """
        # Load configuration
        self.app_config = get_config(config_path)
        self.config = self.app_config.load()

        # Discovery settings
        self.max_depth = max_depth or self.config.discovery_options.max_depth
        self.max_workers = max_workers or self.config.parallel.max_workers
        self.collect_mac_tables = self.config.discovery_options.collect_mac_tables

        # Initialize database
        db_url = get_database_url()
        self.engine = create_database(db_url)
        self.session = get_session(self.engine)

        # Repositories
        self.device_repo = DeviceRepository(self.session)
        self.interface_repo = InterfaceRepository(self.session)
        self.connection_repo = ConnectionRepository(self.session)
        self.mac_repo = MacRepository(self.session)
        self.vlan_repo = VlanRepository(self.session)
        self.session_repo = DiscoverySessionRepository(self.session)

        # Discovery state
        self.discovered_devices: Set[str] = set()  # Hostnames
        self.discovery_queue: Queue = Queue()
        self.device_data: Dict[str, DeviceInfo] = {}
        self.errors: List[Dict[str, str]] = []

    def start_discovery(self) -> Dict[str, Any]:
        """
        Start network discovery process.

        Returns:
            Discovery summary
        """
        logger.info("=" * 60)
        logger.info("Starting Network Discovery")
        logger.info("=" * 60)

        # Create discovery session
        discovery_session = self.session_repo.create_session(
            config_snapshot={
                "max_depth": self.max_depth,
                "max_workers": self.max_workers,
                "collect_mac_tables": self.collect_mac_tables,
            }
        )

        # Add seed devices to queue
        for seed_device in self.config.seed_devices:
            self.discovery_queue.put((seed_device, 0))  # (device_config, depth)

        logger.info(f"Added {len(self.config.seed_devices)} seed devices to queue")

        # Process discovery queue
        try:
            self._process_discovery_queue()

            # Store collected data in database
            self._store_discovery_data()

            # Update session status
            self.session_repo.update_session(
                discovery_session.id,
                status="completed",
                devices_count=len(self.device_data),
                errors=self.errors if self.errors else None,
            )

            summary = self._generate_summary()
            logger.info("=" * 60)
            logger.info("Discovery Completed Successfully")
            logger.info("=" * 60)
            self._print_summary(summary)

            return summary

        except Exception as e:
            logger.error(f"Discovery failed: {e}", exc_info=True)
            self.session_repo.update_session(
                discovery_session.id, status="failed", errors=[{"error": str(e)}]
            )
            raise

    def _process_discovery_queue(self):
        """Process the discovery queue with parallel workers."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            while not self.discovery_queue.empty() or futures:
                # Submit new tasks from queue
                while not self.discovery_queue.empty() and len(futures) < self.max_workers:
                    device_config, depth = self.discovery_queue.get()

                    # Skip if already discovered
                    if device_config.hostname in self.discovered_devices:
                        continue

                    # Skip if max depth reached
                    if depth >= self.max_depth:
                        logger.info(
                            f"Max depth reached for {device_config.hostname}, skipping"
                        )
                        continue

                    # Mark as discovered
                    self.discovered_devices.add(device_config.hostname)

                    # Submit discovery task
                    future = executor.submit(
                        self._discover_device, device_config, depth
                    )
                    futures.append(future)

                # Wait for at least one task to complete
                if futures:
                    done, futures = self._wait_for_completion(futures)

                    # Process completed discoveries
                    for future in done:
                        try:
                            device_info, depth = future.result()
                            if device_info:
                                self._process_discovered_device(device_info, depth)
                        except Exception as e:
                            logger.error(f"Discovery task failed: {e}")

    def _wait_for_completion(self, futures):
        """Wait for at least one future to complete."""
        done = set()
        pending = set(futures)

        for future in as_completed(futures):
            done.add(future)
            pending.remove(future)
            break  # Return after first completion

        return done, list(pending)

    def _discover_device(
        self, device_config: DeviceConfig, depth: int
    ) -> tuple[Optional[DeviceInfo], int]:
        """
        Discover a single device.

        Args:
            device_config: Device configuration
            depth: Current recursion depth

        Returns:
            Tuple of (DeviceInfo, depth) or (None, depth) if failed
        """
        logger.info(
            f"Discovering device: {device_config.hostname} ({device_config.ip}) [depth={depth}]"
        )

        try:
            # Get connection parameters
            conn_params = self.app_config.get_device_credentials(device_config)

            # Collect device information
            collector = NetworkDiscoveryCollector(conn_params)
            device_info = collector.collect_from_device(
                collect_mac_tables=self.collect_mac_tables
            )

            if device_info:
                return device_info, depth
            else:
                self.errors.append(
                    {
                        "device": device_config.hostname,
                        "error": "Failed to collect device information",
                    }
                )
                return None, depth

        except Exception as e:
            logger.error(f"Error discovering {device_config.hostname}: {e}")
            self.errors.append({"device": device_config.hostname, "error": str(e)})
            return None, depth

    def _process_discovered_device(self, device_info: DeviceInfo, depth: int):
        """
        Process a discovered device and queue its neighbors.

        Args:
            device_info: Discovered device information
            depth: Current recursion depth
        """
        # Store device data
        self.device_data[device_info.hostname] = device_info

        logger.info(
            f"Processed device: {device_info.hostname} with {len(device_info.neighbors)} neighbors"
        )

        # Queue neighbors for discovery
        if depth < self.max_depth - 1:
            for neighbor in device_info.neighbors:
                neighbor_hostname = neighbor.get("remote_device")
                neighbor_ip = neighbor.get("remote_ip")

                if not neighbor_hostname or neighbor_hostname in self.discovered_devices:
                    continue

                # Check if this is a switch (has capabilities)
                capabilities = neighbor.get("capabilities", [])
                if not any(
                    cap in ["Switch", "Router", "switch", "router"]
                    for cap in capabilities
                ):
                    logger.debug(
                        f"Skipping {neighbor_hostname} - not a switch/router"
                    )
                    continue

                # Create device config for neighbor
                neighbor_config = DeviceConfig(
                    hostname=neighbor_hostname,
                    ip=neighbor_ip or neighbor_hostname,
                    device_type=self.config.seed_devices[0].device_type,
                )

                # Add to queue
                self.discovery_queue.put((neighbor_config, depth + 1))
                logger.info(
                    f"Queued neighbor: {neighbor_hostname} [depth={depth + 1}]"
                )

    def _store_discovery_data(self):
        """Store all discovered data in the database."""
        logger.info("Storing discovery data in database...")

        device_id_map = {}  # hostname -> device_id
        interface_id_map = {}  # (hostname, interface_name) -> interface_id

        # Store devices and interfaces
        for hostname, device_info in self.device_data.items():
            try:
                # Store device
                device = self.device_repo.create_or_update(device_info.to_dict())
                device_id_map[hostname] = device.id

                # Store interfaces
                for interface in device_info.interfaces:
                    interface_data = interface.to_dict()
                    interface_data["device_id"] = device.id

                    intf = self.interface_repo.create_or_update(interface_data)
                    interface_id_map[(hostname, interface.name)] = intf.id

                # Store VLANs
                for vlan_data in device_info.vlans:
                    vlan_data["device_id"] = device.id
                    self.vlan_repo.create_or_update(vlan_data)

                # Store MAC entries
                for mac_data in device_info.mac_table:
                    mac_data["device_id"] = device.id

                    # Find interface_id
                    interface_name = mac_data.pop("interface")
                    interface_id = interface_id_map.get((hostname, interface_name))

                    if interface_id:
                        mac_data["interface_id"] = interface_id
                        self.mac_repo.add_entry(mac_data)

                logger.info(f"Stored data for device: {hostname}")

            except Exception as e:
                logger.error(f"Error storing device {hostname}: {e}")
                self.errors.append({"device": hostname, "error": f"Storage error: {e}"})

        # Store connections
        for hostname, device_info in self.device_data.items():
            source_device_id = device_id_map.get(hostname)
            if not source_device_id:
                continue

            for neighbor in device_info.neighbors:
                try:
                    remote_hostname = neighbor.get("remote_device")
                    dest_device_id = device_id_map.get(remote_hostname)

                    if not dest_device_id:
                        continue

                    local_interface = neighbor.get("local_interface")
                    source_interface_id = interface_id_map.get(
                        (hostname, local_interface)
                    )

                    if not source_interface_id:
                        continue

                    # Try to find remote interface
                    remote_interface = neighbor.get("remote_interface")
                    dest_interface_id = None
                    if remote_interface:
                        dest_interface_id = interface_id_map.get(
                            (remote_hostname, remote_interface)
                        )

                    # Create connection
                    connection_data = {
                        "source_device_id": source_device_id,
                        "source_interface_id": source_interface_id,
                        "dest_device_id": dest_device_id,
                        "dest_interface_id": dest_interface_id,
                        "link_type": neighbor.get("protocol", "cdp"),
                    }

                    self.connection_repo.create_or_update(connection_data)

                except Exception as e:
                    logger.error(
                        f"Error storing connection from {hostname} to {neighbor.get('remote_device')}: {e}"
                    )

        logger.info("Successfully stored all discovery data")

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate discovery summary."""
        total_interfaces = sum(
            len(d.interfaces) for d in self.device_data.values()
        )
        total_connections = sum(
            len(d.neighbors) for d in self.device_data.values()
        )
        total_mac_entries = sum(
            len(d.mac_table) for d in self.device_data.values()
        )

        return {
            "devices_discovered": len(self.device_data),
            "total_interfaces": total_interfaces,
            "total_connections": total_connections,
            "total_mac_entries": total_mac_entries,
            "errors": len(self.errors),
            "error_list": self.errors,
        }

    def _print_summary(self, summary: Dict[str, Any]):
        """Print discovery summary."""
        logger.info(f"Devices discovered: {summary['devices_discovered']}")
        logger.info(f"Total interfaces: {summary['total_interfaces']}")
        logger.info(f"Total connections: {summary['total_connections']}")
        logger.info(f"Total MAC entries: {summary['total_mac_entries']}")

        if summary["errors"] > 0:
            logger.warning(f"Errors encountered: {summary['errors']}")
            for error in summary["error_list"][:5]:  # Show first 5 errors
                logger.warning(f"  - {error}")
