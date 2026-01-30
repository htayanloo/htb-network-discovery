"""Search API routes."""

from flask import Blueprint, jsonify, request

from database.schema import create_database, get_session
from database.repository import MacRepository, DeviceRepository
from utils.config import get_database_url
from utils.validators import normalize_mac
from utils.logger import get_logger

logger = get_logger(__name__)

bp = Blueprint("search", __name__)


def get_db_session():
    """Get database session."""
    db_url = get_database_url()
    engine = create_database(db_url)
    return get_session(engine)


@bp.route("/search/mac/<mac_address>", methods=["GET"])
def search_mac(mac_address):
    """
    Search for a MAC address.

    Args:
        mac_address: MAC address to search

    Returns:
        JSON with MAC address locations
    """
    try:
        # Normalize MAC address
        try:
            normalized_mac = normalize_mac(mac_address)
        except ValueError as e:
            return jsonify({"error": f"Invalid MAC address: {e}"}), 400

        session = get_db_session()
        repo = MacRepository(session)

        entries = repo.search_mac(normalized_mac)

        if not entries:
            return (
                jsonify(
                    {
                        "mac_address": normalized_mac,
                        "found": False,
                        "locations": [],
                    }
                ),
                404,
            )

        locations = []
        for entry in entries:
            locations.append(
                {
                    "device": entry.device.hostname,
                    "device_id": entry.device_id,
                    "device_ip": entry.device.ip_address,
                    "interface": entry.interface.name if entry.interface else "unknown",
                    "interface_id": entry.interface_id,
                    "vlan_id": entry.vlan_id,
                    "type": entry.type,
                    "last_seen": entry.last_seen.isoformat()
                    if entry.last_seen
                    else None,
                }
            )

        return (
            jsonify(
                {
                    "mac_address": normalized_mac,
                    "found": True,
                    "count": len(locations),
                    "locations": locations,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error searching MAC: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/search/device", methods=["GET"])
def search_device():
    """
    Search for devices by hostname or IP.

    Query params:
        - q: Search query

    Returns:
        JSON with matching devices
    """
    try:
        query = request.args.get("q")

        if not query:
            return jsonify({"error": "Query parameter 'q' required"}), 400

        session = get_db_session()
        repo = DeviceRepository(session)

        # Try exact match first
        device = repo.get_by_hostname(query)
        if device:
            devices = [device]
        else:
            device = repo.get_by_ip(query)
            if device:
                devices = [device]
            else:
                # Fuzzy search
                devices = repo.search(query)

        if not devices:
            return (
                jsonify({"query": query, "found": False, "devices": []}),
                404,
            )

        device_list = []
        for device in devices:
            device_list.append(
                {
                    "id": device.id,
                    "hostname": device.hostname,
                    "ip_address": device.ip_address,
                    "device_type": device.device_type,
                    "model": device.model,
                    "ios_version": device.ios_version,
                }
            )

        return (
            jsonify(
                {
                    "query": query,
                    "found": True,
                    "count": len(device_list),
                    "devices": device_list,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error searching devices: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/search/interface", methods=["GET"])
def search_interface():
    """
    Search for interfaces by name.

    Query params:
        - q: Interface name query
        - device_id: Optional device ID filter

    Returns:
        JSON with matching interfaces
    """
    try:
        query = request.args.get("q")
        device_id = request.args.get("device_id", type=int)

        if not query:
            return jsonify({"error": "Query parameter 'q' required"}), 400

        session = get_db_session()

        from database.schema import Interface, Device

        # Build query
        db_query = session.query(Interface).join(Device)

        if device_id:
            db_query = db_query.filter(Interface.device_id == device_id)

        # Search for interface name
        db_query = db_query.filter(Interface.name.ilike(f"%{query}%"))

        interfaces = db_query.all()

        if not interfaces:
            return (
                jsonify({"query": query, "found": False, "interfaces": []}),
                404,
            )

        interface_list = []
        for interface in interfaces:
            interface_list.append(
                {
                    "id": interface.id,
                    "name": interface.name,
                    "device": interface.device.hostname,
                    "device_id": interface.device_id,
                    "status": interface.status,
                    "vlan_id": interface.vlan_id,
                    "is_trunk": interface.is_trunk,
                    "description": interface.description,
                }
            )

        return (
            jsonify(
                {
                    "query": query,
                    "found": True,
                    "count": len(interface_list),
                    "interfaces": interface_list,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error searching interfaces: {e}")
        return jsonify({"error": str(e)}), 500
