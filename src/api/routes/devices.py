"""Device API routes."""

from flask import Blueprint, jsonify, request

from database.schema import create_database, get_session
from database.repository import DeviceRepository, InterfaceRepository, VlanRepository
from utils.config import get_database_url
from utils.logger import get_logger

logger = get_logger(__name__)

bp = Blueprint("devices", __name__)


def get_db_session():
    """Get database session."""
    db_url = get_database_url()
    engine = create_database(db_url)
    return get_session(engine)


def device_to_dict(device):
    """Convert device to dictionary."""
    return {
        "id": device.id,
        "hostname": device.hostname,
        "ip_address": device.ip_address,
        "device_type": device.device_type,
        "model": device.model,
        "ios_version": device.ios_version,
        "serial_number": device.serial_number,
        "uptime": device.uptime,
        "last_discovered": device.last_discovered.isoformat()
        if device.last_discovered
        else None,
        "interfaces_count": len(device.interfaces) if device.interfaces else 0,
    }


def interface_to_dict(interface):
    """Convert interface to dictionary."""
    return {
        "id": interface.id,
        "name": interface.name,
        "status": interface.status,
        "protocol_status": interface.protocol_status,
        "speed": interface.speed,
        "duplex": interface.duplex,
        "vlan_id": interface.vlan_id,
        "is_trunk": interface.is_trunk,
        "trunk_vlans": interface.trunk_vlans,
        "description": interface.description,
        "mac_address": interface.mac_address,
        "mtu": interface.mtu,
        "input_rate": interface.input_rate,
        "output_rate": interface.output_rate,
    }


@bp.route("/devices", methods=["GET"])
def list_devices():
    """
    Get list of all devices.

    Query params:
        - type: Filter by device type

    Returns:
        JSON list of devices
    """
    try:
        session = get_db_session()
        repo = DeviceRepository(session)

        device_type = request.args.get("type")

        if device_type:
            devices = [d for d in repo.get_all() if d.device_type == device_type]
        else:
            devices = repo.get_all()

        device_list = [device_to_dict(d) for d in devices]

        return jsonify({"devices": device_list, "count": len(device_list)}), 200

    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/devices/<int:device_id>", methods=["GET"])
def get_device(device_id):
    """
    Get detailed information about a device.

    Args:
        device_id: Device ID

    Returns:
        JSON with device details
    """
    try:
        session = get_db_session()
        repo = DeviceRepository(session)

        device = session.query(
            repo.session.query(repo.session.query.__self__).get_bind()
        ).get(device_id)

        if not device:
            return jsonify({"error": "Device not found"}), 404

        device_data = device_to_dict(device)

        # Add interfaces
        if device.interfaces:
            device_data["interfaces"] = [
                interface_to_dict(i) for i in device.interfaces
            ]

        return jsonify(device_data), 200

    except Exception as e:
        logger.error(f"Error getting device: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/devices/<int:device_id>/interfaces", methods=["GET"])
def get_device_interfaces(device_id):
    """
    Get interfaces for a device.

    Args:
        device_id: Device ID

    Returns:
        JSON with interface list
    """
    try:
        session = get_db_session()
        repo = InterfaceRepository(session)

        interfaces = repo.get_by_device(device_id)

        interface_list = [interface_to_dict(i) for i in interfaces]

        return (
            jsonify({"device_id": device_id, "interfaces": interface_list, "count": len(interface_list)}),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting interfaces: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/devices/<int:device_id>/vlans", methods=["GET"])
def get_device_vlans(device_id):
    """
    Get VLANs for a device.

    Args:
        device_id: Device ID

    Returns:
        JSON with VLAN list
    """
    try:
        session = get_db_session()
        repo = VlanRepository(session)

        vlans = repo.get_by_device(device_id)

        vlan_list = [
            {
                "vlan_id": v.vlan_id,
                "name": v.name,
                "status": v.status,
            }
            for v in vlans
        ]

        return jsonify({"device_id": device_id, "vlans": vlan_list, "count": len(vlan_list)}), 200

    except Exception as e:
        logger.error(f"Error getting VLANs: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/devices/hostname/<hostname>", methods=["GET"])
def get_device_by_hostname(hostname):
    """
    Get device by hostname.

    Args:
        hostname: Device hostname

    Returns:
        JSON with device details
    """
    try:
        session = get_db_session()
        repo = DeviceRepository(session)

        device = repo.get_by_hostname(hostname)

        if not device:
            return jsonify({"error": "Device not found"}), 404

        device_data = device_to_dict(device)

        # Add interfaces
        if device.interfaces:
            device_data["interfaces"] = [
                interface_to_dict(i) for i in device.interfaces
            ]

        return jsonify(device_data), 200

    except Exception as e:
        logger.error(f"Error getting device: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/vlans", methods=["GET"])
def list_all_vlans():
    """
    Get list of all VLANs across all devices.

    Returns:
        JSON with VLAN list
    """
    try:
        session = get_db_session()

        from database.schema import Vlan, Device

        vlans = session.query(Vlan).join(Device).all()

        vlan_list = [
            {
                "vlan_id": v.vlan_id,
                "name": v.name,
                "status": v.status,
                "device": v.device_id,
                "device_hostname": session.query(Device)
                .filter_by(id=v.device_id)
                .first()
                .hostname,
            }
            for v in vlans
        ]

        return jsonify({"vlans": vlan_list, "count": len(vlan_list)}), 200

    except Exception as e:
        logger.error(f"Error listing VLANs: {e}")
        return jsonify({"error": str(e)}), 500
