"""Database schema definitions using SQLAlchemy."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

Base = declarative_base()


class Device(Base):
    """Network device model."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)  # Support IPv4/IPv6
    device_type = Column(String(50), default="switch")  # switch, router, endpoint
    model = Column(String(100))
    ios_version = Column(String(100))
    serial_number = Column(String(100), unique=True, index=True)
    uptime = Column(String(100))
    last_discovered = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interfaces = relationship(
        "Interface", back_populates="device", cascade="all, delete-orphan"
    )
    mac_entries = relationship(
        "MacEntry", back_populates="device", cascade="all, delete-orphan"
    )
    source_connections = relationship(
        "Connection",
        foreign_keys="Connection.source_device_id",
        back_populates="source_device",
        cascade="all, delete-orphan",
    )
    dest_connections = relationship(
        "Connection",
        foreign_keys="Connection.dest_device_id",
        back_populates="dest_device",
    )

    def __repr__(self):
        return f"<Device(hostname={self.hostname}, ip={self.ip_address})>"


class Interface(Base):
    """Network interface model."""

    __tablename__ = "interfaces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)  # e.g., GigabitEthernet1/0/1
    status = Column(String(20))  # up, down, admin down
    protocol_status = Column(String(20))  # up, down
    speed = Column(String(20))  # 10, 100, 1000, 10000 (Mbps)
    duplex = Column(String(20))  # full, half, auto
    vlan_id = Column(Integer)
    is_trunk = Column(Boolean, default=False)
    trunk_vlans = Column(JSON)  # List of allowed VLANs on trunk
    description = Column(String(255))
    mac_address = Column(String(17))  # Interface MAC address
    mtu = Column(Integer)
    last_input = Column(String(50))  # Time since last input
    last_output = Column(String(50))  # Time since last output
    input_rate = Column(Integer)  # Bits per second
    output_rate = Column(Integer)  # Bits per second
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    device = relationship("Device", back_populates="interfaces")
    mac_entries = relationship(
        "MacEntry", back_populates="interface", cascade="all, delete-orphan"
    )
    source_connections = relationship(
        "Connection",
        foreign_keys="Connection.source_interface_id",
        back_populates="source_interface",
        cascade="all, delete-orphan",
    )
    dest_connections = relationship(
        "Connection",
        foreign_keys="Connection.dest_interface_id",
        back_populates="dest_interface",
    )

    __table_args__ = (
        UniqueConstraint("device_id", "name", name="uix_device_interface"),
        Index("ix_interface_status", "status"),
    )

    def __repr__(self):
        return f"<Interface(name={self.name}, status={self.status})>"


class Connection(Base):
    """Network connection/link between devices."""

    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    source_interface_id = Column(Integer, ForeignKey("interfaces.id"), nullable=False)
    dest_device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    dest_interface_id = Column(Integer, ForeignKey("interfaces.id"))
    link_type = Column(String(20), default="cdp")  # cdp, lldp, inferred
    discovered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    source_device = relationship(
        "Device", foreign_keys=[source_device_id], back_populates="source_connections"
    )
    dest_device = relationship(
        "Device", foreign_keys=[dest_device_id], back_populates="dest_connections"
    )
    source_interface = relationship(
        "Interface",
        foreign_keys=[source_interface_id],
        back_populates="source_connections",
    )
    dest_interface = relationship(
        "Interface",
        foreign_keys=[dest_interface_id],
        back_populates="dest_connections",
    )

    __table_args__ = (
        UniqueConstraint(
            "source_device_id",
            "source_interface_id",
            "dest_device_id",
            name="uix_connection",
        ),
        Index("ix_connection_devices", "source_device_id", "dest_device_id"),
    )

    def __repr__(self):
        return f"<Connection(source={self.source_device_id}, dest={self.dest_device_id})>"


class MacEntry(Base):
    """MAC address table entry."""

    __tablename__ = "mac_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mac_address = Column(String(17), nullable=False, index=True)  # XX:XX:XX:XX:XX:XX
    vlan_id = Column(Integer, nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    interface_id = Column(Integer, ForeignKey("interfaces.id"), nullable=False, index=True)
    type = Column(String(20), default="dynamic")  # dynamic, static
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    device = relationship("Device", back_populates="mac_entries")
    interface = relationship("Interface", back_populates="mac_entries")

    __table_args__ = (
        Index("ix_mac_lookup", "mac_address", "vlan_id"),
        Index("ix_mac_device", "device_id", "interface_id"),
    )

    def __repr__(self):
        return f"<MacEntry(mac={self.mac_address}, vlan={self.vlan_id})>"


class Vlan(Base):
    """VLAN information."""

    __tablename__ = "vlans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vlan_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100))
    status = Column(String(20))  # active, suspended
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("device_id", "vlan_id", name="uix_device_vlan"),
    )

    def __repr__(self):
        return f"<Vlan(id={self.vlan_id}, name={self.name})>"


class DiscoverySession(Base):
    """Discovery session tracking."""

    __tablename__ = "discovery_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    status = Column(String(20), default="running")  # running, completed, failed
    devices_discovered = Column(Integer, default=0)
    interfaces_discovered = Column(Integer, default=0)
    connections_discovered = Column(Integer, default=0)
    errors = Column(JSON)  # List of errors encountered
    config_snapshot = Column(JSON)  # Configuration used for this session
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<DiscoverySession(id={self.id}, status={self.status})>"


# Database initialization functions
def create_database(database_url: str):
    """
    Create database and tables.

    Args:
        database_url: SQLAlchemy database URL
    """
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine) -> Session:
    """
    Get database session.

    Args:
        engine: SQLAlchemy engine

    Returns:
        Database session
    """
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
