"""Topology API routes."""

from flask import Blueprint, jsonify, request

from database.schema import create_database, get_session
from core.topology.builder import TopologyBuilder, TopologyAnalyzer
from utils.config import get_database_url
from utils.logger import get_logger

logger = get_logger(__name__)

bp = Blueprint("topology", __name__)


def get_db_session():
    """Get database session."""
    db_url = get_database_url()
    engine = create_database(db_url)
    return get_session(engine)


@bp.route("/topology", methods=["GET"])
def get_topology():
    """
    Get full network topology.

    Returns:
        JSON with nodes, edges, and statistics
    """
    try:
        session = get_db_session()
        builder = TopologyBuilder(session)
        builder.build_graph()

        topology_data = builder.get_topology_json()

        return jsonify(topology_data), 200

    except Exception as e:
        logger.error(f"Error getting topology: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/topology/stats", methods=["GET"])
def get_topology_stats():
    """
    Get topology statistics.

    Returns:
        JSON with topology statistics
    """
    try:
        session = get_db_session()
        builder = TopologyBuilder(session)
        builder.build_graph()

        stats = builder.get_statistics()

        return jsonify(stats), 200

    except Exception as e:
        logger.error(f"Error getting topology stats: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/topology/path", methods=["GET"])
def find_path():
    """
    Find shortest path between two devices.

    Query params:
        - source: Source device hostname
        - target: Target device hostname

    Returns:
        JSON with path information
    """
    try:
        source = request.args.get("source")
        target = request.args.get("target")

        if not source or not target:
            return jsonify({"error": "source and target parameters required"}), 400

        session = get_db_session()
        builder = TopologyBuilder(session)
        builder.build_graph()

        path = builder.find_path(source, target)

        if path:
            return jsonify({"source": source, "target": target, "path": path}), 200
        else:
            return (
                jsonify(
                    {
                        "error": f"No path found between {source} and {target}",
                        "source": source,
                        "target": target,
                    }
                ),
                404,
            )

    except Exception as e:
        logger.error(f"Error finding path: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/topology/neighbors/<device>", methods=["GET"])
def get_neighbors(device):
    """
    Get neighbors of a device.

    Args:
        device: Device hostname

    Returns:
        JSON with neighbor list
    """
    try:
        session = get_db_session()
        builder = TopologyBuilder(session)
        builder.build_graph()

        neighbors = builder.get_neighbors(device)

        return jsonify({"device": device, "neighbors": neighbors}), 200

    except Exception as e:
        logger.error(f"Error getting neighbors: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/topology/analysis", methods=["GET"])
def analyze_topology():
    """
    Analyze topology for insights.

    Returns:
        JSON with topology analysis
    """
    try:
        session = get_db_session()
        builder = TopologyBuilder(session)
        graph = builder.build_graph()

        analyzer = TopologyAnalyzer(graph)

        analysis = {
            "core_switches": analyzer.identify_core_switches(),
            "access_switches": analyzer.identify_access_switches(),
            "redundant_paths": analyzer.detect_redundancy(),
        }

        return jsonify(analysis), 200

    except Exception as e:
        logger.error(f"Error analyzing topology: {e}")
        return jsonify({"error": str(e)}), 500
