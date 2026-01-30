"""Data access layer for network discovery database."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from database.schema import (
    Device,
    Interface,
    Connection,
    MacEntry,
    Vlan,
    DiscoverySession,
)


class DeviceRepository:
    """Repository for device operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def create_or_update(self, device_data: Dict[str, Any]) -> Device:
        """
        Create or update a device.

        Args:
            device_data: Device attributes

        Returns:
            Device instance
        """
        hostname = device_data.get("hostname")
        device = self.session.query(Device).filter_by(hostname=hostname).first()

        if device:
            # Update existing device
            for key, value in device_data.items():
                if hasattr(device, key):
                    setattr(device, key, value)
            device.last_discovered = datetime.utcnow()
            device.updated_at = datetime.utcnow()
        else:
            # Create new device
            device = Device(**device_data)
            self.session.add(device)

        self.session.commit()
        return device

    def get_by_hostname(self, hostname: str) -> Optional[Device]:
        """Get device by hostname."""
        return self.session.query(Device).filter_by(hostname=hostname).first()

    def get_by_ip(self, ip_address: str) -> Optional[Device]:
        """Get device by IP address."""
        return self.session.query(Device).filter_by(ip_address=ip_address).first()

    def get_all(self) -> List[Device]:
        """Get all devices."""
        return self.session.query(Device).all()

    def get_switches(self) -> List[Device]:
        """Get all switch devices."""
        return self.session.query(Device).filter_by(device_type="switch").all()

    def search(self, query: str) -> List[Device]:
        """
        Search devices by hostname or IP.

        Args:
            query: Search query

        Returns:
            List of matching devices
        """
        return (
            self.session.query(Device)
            .filter(
                or_(
                    Device.hostname.ilike(f"%{query}%"),
                    Device.ip_address.ilike(f"%{query}%"),
                )
            )
            .all()
        )

    def delete(self, device_id: int) -> bool:
        """Delete a device."""
        device = self.session.query(Device).get(device_id)
        if device:
            self.session.delete(device)
            self.session.commit()
            return True
        return False


class InterfaceRepository:
    """Repository for interface operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def create_or_update(self, interface_data: Dict[str, Any]) -> Interface:
        """
        Create or update an interface.

        Args:
            interface_data: Interface attributes

        Returns:
            Interface instance
        """
        device_id = interface_data.get("device_id")
        name = interface_data.get("name")

        interface = (
            self.session.query(Interface)
            .filter_by(device_id=device_id, name=name)
            .first()
        )

        if interface:
            # Update existing interface
            for key, value in interface_data.items():
                if hasattr(interface, key):
                    setattr(interface, key, value)
            interface.updated_at = datetime.utcnow()
        else:
            # Create new interface
            interface = Interface(**interface_data)
            self.session.add(interface)

        self.session.commit()
        return interface

    def get_by_device(self, device_id: int) -> List[Interface]:
        """Get all interfaces for a device."""
        return self.session.query(Interface).filter_by(device_id=device_id).all()

    def get_by_id(self, interface_id: int) -> Optional[Interface]:
        """Get interface by ID."""
        return self.session.query(Interface).get(interface_id)

    def get_uplinks(self, device_id: int) -> List[Interface]:
        """Get uplink interfaces (connected to other switches)."""
        return (
            self.session.query(Interface)
            .join(Connection, Interface.id == Connection.source_interface_id)
            .filter(Interface.device_id == device_id)
            .distinct()
            .all()
        )

    def get_access_ports(self, device_id: int) -> List[Interface]:
        """Get access ports (non-trunk, non-uplink interfaces)."""
        return (
            self.session.query(Interface)
            .filter_by(device_id=device_id, is_trunk=False)
            .filter(Interface.status == "up")
            .all()
        )


class ConnectionRepository:
    """Repository for connection operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def create_or_update(self, connection_data: Dict[str, Any]) -> Connection:
        """
        Create or update a connection.

        Args:
            connection_data: Connection attributes

        Returns:
            Connection instance
        """
        source_device_id = connection_data.get("source_device_id")
        source_interface_id = connection_data.get("source_interface_id")
        dest_device_id = connection_data.get("dest_device_id")

        connection = (
            self.session.query(Connection)
            .filter_by(
                source_device_id=source_device_id,
                source_interface_id=source_interface_id,
                dest_device_id=dest_device_id,
            )
            .first()
        )

        if connection:
            # Update existing connection
            connection.last_seen = datetime.utcnow()
            for key, value in connection_data.items():
                if hasattr(connection, key) and key not in ["discovered_at"]:
                    setattr(connection, key, value)
        else:
            # Create new connection
            connection = Connection(**connection_data)
            self.session.add(connection)

        self.session.commit()
        return connection

    def get_all(self) -> List[Connection]:
        """Get all connections."""
        return self.session.query(Connection).all()

    def get_by_device(self, device_id: int) -> List[Connection]:
        """Get all connections for a device."""
        return (
            self.session.query(Connection)
            .filter(
                or_(
                    Connection.source_device_id == device_id,
                    Connection.dest_device_id == device_id,
                )
            )
            .all()
        )

    def get_neighbors(self, device_id: int) -> List[Device]:
        """Get all neighbor devices."""
        neighbors = (
            self.session.query(Device)
            .join(Connection, Device.id == Connection.dest_device_id)
            .filter(Connection.source_device_id == device_id)
            .distinct()
            .all()
        )
        return neighbors


class MacRepository:
    """Repository for MAC address table operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def add_entry(self, mac_data: Dict[str, Any]) -> MacEntry:
        """
        Add or update a MAC entry.

        Args:
            mac_data: MAC entry attributes

        Returns:
            MacEntry instance
        """
        mac_address = mac_data.get("mac_address")
        vlan_id = mac_data.get("vlan_id")
        device_id = mac_data.get("device_id")

        # Check if entry exists
        entry = (
            self.session.query(MacEntry)
            .filter_by(
                mac_address=mac_address, vlan_id=vlan_id, device_id=device_id
            )
            .first()
        )

        if entry:
            # Update last seen
            entry.last_seen = datetime.utcnow()
            for key, value in mac_data.items():
                if hasattr(entry, key) and key not in ["created_at"]:
                    setattr(entry, key, value)
        else:
            # Create new entry
            entry = MacEntry(**mac_data)
            self.session.add(entry)

        self.session.commit()
        return entry

    def search_mac(self, mac_address: str) -> List[MacEntry]:
        """
        Search for MAC address across all devices.

        Args:
            mac_address: MAC address to search

        Returns:
            List of MAC entries
        """
        return (
            self.session.query(MacEntry)
            .filter_by(mac_address=mac_address)
            .order_by(MacEntry.last_seen.desc())
            .all()
        )

    def get_by_device(self, device_id: int) -> List[MacEntry]:
        """Get all MAC entries for a device."""
        return self.session.query(MacEntry).filter_by(device_id=device_id).all()

    def get_by_interface(self, interface_id: int) -> List[MacEntry]:
        """Get all MAC entries for an interface."""
        return (
            self.session.query(MacEntry)
            .filter_by(interface_id=interface_id)
            .all()
        )

    def cleanup_old_entries(self, days: int = 30) -> int:
        """
        Remove MAC entries older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            Number of entries deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        count = (
            self.session.query(MacEntry)
            .filter(MacEntry.last_seen < cutoff_date)
            .delete()
        )
        self.session.commit()
        return count


class VlanRepository:
    """Repository for VLAN operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def create_or_update(self, vlan_data: Dict[str, Any]) -> Vlan:
        """Create or update a VLAN."""
        device_id = vlan_data.get("device_id")
        vlan_id = vlan_data.get("vlan_id")

        vlan = (
            self.session.query(Vlan)
            .filter_by(device_id=device_id, vlan_id=vlan_id)
            .first()
        )

        if vlan:
            for key, value in vlan_data.items():
                if hasattr(vlan, key):
                    setattr(vlan, key, value)
            vlan.updated_at = datetime.utcnow()
        else:
            vlan = Vlan(**vlan_data)
            self.session.add(vlan)

        self.session.commit()
        return vlan

    def get_by_device(self, device_id: int) -> List[Vlan]:
        """Get all VLANs for a device."""
        return self.session.query(Vlan).filter_by(device_id=device_id).all()


class DiscoverySessionRepository:
    """Repository for discovery session tracking."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def create_session(self, config_snapshot: Optional[Dict] = None) -> DiscoverySession:
        """Create a new discovery session."""
        session_obj = DiscoverySession(
            status="running",
            config_snapshot=config_snapshot,
        )
        self.session.add(session_obj)
        self.session.commit()
        return session_obj

    def update_session(
        self,
        session_id: int,
        status: Optional[str] = None,
        devices_count: Optional[int] = None,
        interfaces_count: Optional[int] = None,
        connections_count: Optional[int] = None,
        errors: Optional[List] = None,
    ) -> DiscoverySession:
        """Update discovery session."""
        session_obj = self.session.query(DiscoverySession).get(session_id)
        if session_obj:
            if status:
                session_obj.status = status
            if status in ["completed", "failed"]:
                session_obj.completed_at = datetime.utcnow()
            if devices_count is not None:
                session_obj.devices_discovered = devices_count
            if interfaces_count is not None:
                session_obj.interfaces_discovered = interfaces_count
            if connections_count is not None:
                session_obj.connections_discovered = connections_count
            if errors is not None:
                session_obj.errors = errors

            self.session.commit()
        return session_obj

    def get_latest(self) -> Optional[DiscoverySession]:
        """Get the latest discovery session."""
        return (
            self.session.query(DiscoverySession)
            .order_by(DiscoverySession.started_at.desc())
            .first()
        )
