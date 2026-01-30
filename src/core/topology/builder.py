"""Topology builder using NetworkX."""

from typing import Dict, Any, List, Optional
import networkx as nx
from sqlalchemy.orm import Session

from database.schema import Device, Interface, Connection
from database.repository import DeviceRepository, ConnectionRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class TopologyBuilder:
    """Builds network topology graph from database."""

    def __init__(self, session: Session):
        """
        Initialize topology builder.

        Args:
            session: Database session
        """
        self.session = session
        self.device_repo = DeviceRepository(session)
        self.connection_repo = ConnectionRepository(session)
        self.graph: Optional[nx.Graph] = None

    def build_graph(self, directed: bool = False) -> nx.Graph:
        """
        Build NetworkX graph from database.

        Args:
            directed: Whether to create directed graph

        Returns:
            NetworkX graph
        """
        logger.info("Building topology graph...")

        # Create graph
        if directed:
            self.graph = nx.DiGraph()
        else:
            self.graph = nx.Graph()

        # Add nodes (devices)
        devices = self.device_repo.get_all()
        for device in devices:
            self.graph.add_node(
                device.hostname,
                id=device.id,
                ip=device.ip_address,
                type=device.device_type,
                model=device.model,
                ios_version=device.ios_version,
                serial=device.serial_number,
                interfaces_count=len(device.interfaces),
            )

        logger.info(f"Added {len(devices)} nodes to graph")

        # Add edges (connections)
        connections = self.connection_repo.get_all()
        edge_count = 0

        for conn in connections:
            source_hostname = conn.source_device.hostname
            dest_hostname = conn.dest_device.hostname

            # Get interface details
            source_interface = conn.source_interface.name if conn.source_interface else None
            dest_interface = conn.dest_interface.name if conn.dest_interface else None

            # Add edge with attributes
            self.graph.add_edge(
                source_hostname,
                dest_hostname,
                source_interface=source_interface,
                dest_interface=dest_interface,
                link_type=conn.link_type,
                source_interface_id=conn.source_interface_id,
                dest_interface_id=conn.dest_interface_id,
            )
            edge_count += 1

        logger.info(f"Added {edge_count} edges to graph")
        logger.info(f"Graph has {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")

        return self.graph

    def get_topology_json(self) -> Dict[str, Any]:
        """
        Export topology as JSON for visualization.

        Returns:
            Dictionary with nodes and edges
        """
        if self.graph is None:
            self.build_graph()

        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": node_id,
                "type": data.get("type", "unknown"),
                "ip": data.get("ip"),
                "model": data.get("model"),
                "ios_version": data.get("ios_version"),
                "interfaces_count": data.get("interfaces_count", 0),
            })

        edges = []
        for source, dest, data in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": dest,
                "source_interface": data.get("source_interface"),
                "dest_interface": data.get("dest_interface"),
                "link_type": data.get("link_type", "unknown"),
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": self.get_statistics(),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate topology statistics.

        Returns:
            Dictionary with topology statistics
        """
        if self.graph is None:
            self.build_graph()

        stats = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "is_connected": nx.is_connected(self.graph),
            "number_of_components": nx.number_connected_components(self.graph),
        }

        # Calculate density
        if self.graph.number_of_nodes() > 1:
            stats["density"] = nx.density(self.graph)

        # Calculate average degree
        if self.graph.number_of_nodes() > 0:
            degrees = [d for n, d in self.graph.degree()]
            stats["average_degree"] = sum(degrees) / len(degrees)

        # Find central nodes
        if self.graph.number_of_nodes() > 0:
            try:
                centrality = nx.degree_centrality(self.graph)
                sorted_nodes = sorted(
                    centrality.items(), key=lambda x: x[1], reverse=True
                )
                stats["most_central_nodes"] = [
                    {"node": node, "centrality": cent}
                    for node, cent in sorted_nodes[:5]
                ]
            except Exception as e:
                logger.warning(f"Could not calculate centrality: {e}")

        return stats

    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find shortest path between two devices.

        Args:
            source: Source device hostname
            target: Target device hostname

        Returns:
            List of hostnames in path or None if no path exists
        """
        if self.graph is None:
            self.build_graph()

        try:
            path = nx.shortest_path(self.graph, source, target)
            return path
        except (nx.NodeNotFound, nx.NetworkXNoPath) as e:
            logger.warning(f"No path from {source} to {target}: {e}")
            return None

    def get_neighbors(self, device: str) -> List[str]:
        """
        Get neighbors of a device.

        Args:
            device: Device hostname

        Returns:
            List of neighbor hostnames
        """
        if self.graph is None:
            self.build_graph()

        try:
            return list(self.graph.neighbors(device))
        except nx.NodeNotFound:
            logger.warning(f"Device not found: {device}")
            return []

    def find_loops(self) -> List[List[str]]:
        """
        Find loops/cycles in the topology.

        Returns:
            List of cycles (each cycle is a list of hostnames)
        """
        if self.graph is None:
            self.build_graph()

        try:
            cycles = nx.cycle_basis(self.graph)
            return cycles
        except Exception as e:
            logger.warning(f"Could not find cycles: {e}")
            return []

    def get_spanning_tree(self) -> nx.Graph:
        """
        Calculate minimum spanning tree.

        Returns:
            Spanning tree graph
        """
        if self.graph is None:
            self.build_graph()

        return nx.minimum_spanning_tree(self.graph)

    def export_graphml(self, output_file: str):
        """
        Export topology as GraphML format.

        Args:
            output_file: Output file path
        """
        if self.graph is None:
            self.build_graph()

        nx.write_graphml(self.graph, output_file)
        logger.info(f"Exported topology to {output_file}")

    def export_gexf(self, output_file: str):
        """
        Export topology as GEXF format.

        Args:
            output_file: Output file path
        """
        if self.graph is None:
            self.build_graph()

        nx.write_gexf(self.graph, output_file)
        logger.info(f"Exported topology to {output_file}")


class TopologyAnalyzer:
    """Analyzes network topology for insights."""

    def __init__(self, graph: nx.Graph):
        """
        Initialize analyzer.

        Args:
            graph: NetworkX graph
        """
        self.graph = graph

    def identify_core_switches(self) -> List[Dict[str, Any]]:
        """
        Identify core switches based on centrality.

        Returns:
            List of core switch candidates
        """
        if self.graph.number_of_nodes() == 0:
            return []

        # Calculate betweenness centrality
        centrality = nx.betweenness_centrality(self.graph)

        # Sort by centrality
        sorted_devices = sorted(
            centrality.items(), key=lambda x: x[1], reverse=True
        )

        # Top devices are likely core switches
        core_switches = []
        for device, score in sorted_devices[:3]:  # Top 3
            node_data = self.graph.nodes[device]
            core_switches.append({
                "hostname": device,
                "centrality_score": score,
                "degree": self.graph.degree(device),
                "type": node_data.get("type"),
            })

        return core_switches

    def identify_access_switches(self) -> List[str]:
        """
        Identify access switches (edge devices with low connectivity).

        Returns:
            List of access switch hostnames
        """
        access_switches = []

        for node in self.graph.nodes():
            degree = self.graph.degree(node)

            # Access switches typically have low degree (1-2 uplinks)
            if degree <= 2:
                access_switches.append(node)

        return access_switches

    def detect_redundancy(self) -> List[Dict[str, Any]]:
        """
        Detect redundant paths in the network.

        Returns:
            List of redundant path groups
        """
        redundant_paths = []

        for node in self.graph.nodes():
            neighbors = list(self.graph.neighbors(node))

            if len(neighbors) >= 2:
                # Check if there are alternate paths between neighbors
                for i, neighbor1 in enumerate(neighbors):
                    for neighbor2 in neighbors[i + 1 :]:
                        # Find path that doesn't go through current node
                        temp_graph = self.graph.copy()
                        temp_graph.remove_node(node)

                        if nx.has_path(temp_graph, neighbor1, neighbor2):
                            redundant_paths.append({
                                "device": node,
                                "neighbors": [neighbor1, neighbor2],
                                "redundancy": "loop_detected",
                            })

        return redundant_paths
