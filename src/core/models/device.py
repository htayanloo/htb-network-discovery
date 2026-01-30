"""Device domain model."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class DeviceInfo:
    """Domain model for network device information."""

    hostname: str
    ip_address: str
    device_type: str = "switch"  # switch, router, endpoint
    model: Optional[str] = None
    ios_version: Optional[str] = None
    serial_number: Optional[str] = None
    uptime: Optional[str] = None
    last_discovered: datetime = field(default_factory=datetime.utcnow)
    interfaces: List["InterfaceInfo"] = field(default_factory=list)
    neighbors: List[Dict[str, Any]] = field(default_factory=list)
    mac_table: List[Dict[str, Any]] = field(default_factory=list)
    vlans: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "device_type": self.device_type,
            "model": self.model,
            "ios_version": self.ios_version,
            "serial_number": self.serial_number,
            "uptime": self.uptime,
            "last_discovered": self.last_discovered.isoformat(),
        }


@dataclass
class InterfaceInfo:
    """Domain model for network interface information."""

    name: str
    status: str = "unknown"
    protocol_status: str = "unknown"
    speed: Optional[str] = None
    duplex: Optional[str] = None
    vlan_id: Optional[int] = None
    is_trunk: bool = False
    trunk_vlans: Optional[List[int]] = None
    description: Optional[str] = None
    mac_address: Optional[str] = None
    mtu: Optional[int] = None
    input_rate: Optional[int] = None
    output_rate: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status,
            "protocol_status": self.protocol_status,
            "speed": self.speed,
            "duplex": self.duplex,
            "vlan_id": self.vlan_id,
            "is_trunk": self.is_trunk,
            "trunk_vlans": self.trunk_vlans,
            "description": self.description,
            "mac_address": self.mac_address,
            "mtu": self.mtu,
            "input_rate": self.input_rate,
            "output_rate": self.output_rate,
        }


@dataclass
class NeighborInfo:
    """Domain model for CDP/LLDP neighbor information."""

    local_interface: str
    remote_device: str
    remote_interface: str
    remote_ip: Optional[str] = None
    platform: Optional[str] = None
    capabilities: Optional[List[str]] = None
    protocol: str = "cdp"  # cdp or lldp

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "local_interface": self.local_interface,
            "remote_device": self.remote_device,
            "remote_interface": self.remote_interface,
            "remote_ip": self.remote_ip,
            "platform": self.platform,
            "capabilities": self.capabilities,
            "protocol": self.protocol,
        }


@dataclass
class MacEntry:
    """Domain model for MAC address table entry."""

    mac_address: str
    vlan_id: int
    interface: str
    type: str = "dynamic"  # dynamic or static

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mac_address": self.mac_address,
            "vlan_id": self.vlan_id,
            "interface": self.interface,
            "type": self.type,
        }


@dataclass
class VlanInfo:
    """Domain model for VLAN information."""

    vlan_id: int
    name: str
    status: str = "active"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vlan_id": self.vlan_id,
            "name": self.name,
            "status": self.status,
        }
