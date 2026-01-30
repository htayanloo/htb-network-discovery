"""Main CLI application entry point."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

from cli import discover, search

console = Console()
app = typer.Typer(
    name="network-discovery",
    help="Network Discovery and Visualization Tool",
    add_completion=False,
)

# Add sub-commands
app.add_typer(discover.app, name="discover", help="Discover network topology")
app.add_typer(search.app, name="search", help="Search devices and MAC addresses")


@app.command()
def list_devices(
    device_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Filter by device type (switch, router, endpoint)"
    ),
):
    """List all discovered devices."""
    from database.schema import create_database, get_session
    from database.repository import DeviceRepository
    from utils.config import get_database_url

    db_url = get_database_url()
    engine = create_database(db_url)
    session = get_session(engine)

    repo = DeviceRepository(session)

    if device_type:
        devices = [d for d in repo.get_all() if d.device_type == device_type]
    else:
        devices = repo.get_all()

    if not devices:
        console.print("[yellow]No devices found[/yellow]")
        return

    # Create table
    table = Table(title="Discovered Devices", show_header=True)
    table.add_column("Hostname", style="cyan")
    table.add_column("IP Address", style="blue")
    table.add_column("Type", style="green")
    table.add_column("Model", style="magenta")
    table.add_column("IOS Version")
    table.add_column("Last Discovered")

    for device in devices:
        table.add_row(
            device.hostname,
            device.ip_address,
            device.device_type or "unknown",
            device.model or "unknown",
            device.ios_version or "unknown",
            device.last_discovered.strftime("%Y-%m-%d %H:%M:%S")
            if device.last_discovered
            else "unknown",
        )

    console.print(table)
    console.print(f"\n[green]Total devices: {len(devices)}[/green]")


@app.command()
def list_connections():
    """List all connections between devices."""
    from database.schema import create_database, get_session
    from database.repository import ConnectionRepository
    from utils.config import get_database_url

    db_url = get_database_url()
    engine = create_database(db_url)
    session = get_session(engine)

    repo = ConnectionRepository(session)
    connections = repo.get_all()

    if not connections:
        console.print("[yellow]No connections found[/yellow]")
        return

    # Create table
    table = Table(title="Network Connections", show_header=True)
    table.add_column("Source Device", style="cyan")
    table.add_column("Source Interface", style="blue")
    table.add_column("Destination Device", style="cyan")
    table.add_column("Dest Interface", style="blue")
    table.add_column("Protocol", style="green")

    for conn in connections:
        table.add_row(
            conn.source_device.hostname,
            conn.source_interface.name if conn.source_interface else "unknown",
            conn.dest_device.hostname,
            conn.dest_interface.name if conn.dest_interface else "unknown",
            conn.link_type,
        )

    console.print(table)
    console.print(f"\n[green]Total connections: {len(connections)}[/green]")


@app.command()
def export(
    format: str = typer.Option(
        "json", "--format", "-f", help="Export format (json, graphml, gexf)"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
):
    """Export topology data."""
    import json
    from database.schema import create_database, get_session
    from core.topology.builder import TopologyBuilder
    from utils.config import get_database_url

    db_url = get_database_url()
    engine = create_database(db_url)
    session = get_session(engine)

    builder = TopologyBuilder(session)
    builder.build_graph()

    if format == "json":
        topology_data = builder.get_topology_json()
        json_output = json.dumps(topology_data, indent=2)

        if output:
            with open(output, "w") as f:
                f.write(json_output)
            console.print(f"[green]Exported topology to {output}[/green]")
        else:
            console.print(json_output)

    elif format == "graphml":
        if not output:
            output = "topology.graphml"
        builder.export_graphml(output)
        console.print(f"[green]Exported topology to {output}[/green]")

    elif format == "gexf":
        if not output:
            output = "topology.gexf"
        builder.export_gexf(output)
        console.print(f"[green]Exported topology to {output}[/green]")

    else:
        console.print(f"[red]Unsupported format: {format}[/red]")
        raise typer.Exit(1)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="API host"),
    port: int = typer.Option(5000, "--port", "-p", help="API port"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
):
    """Start web dashboard server."""
    from api.app import create_app

    console.print("[green]Starting web dashboard...[/green]")
    console.print(f"[cyan]API: http://{host}:{port}[/cyan]")
    console.print(f"[cyan]Dashboard: Open web/index.html in browser[/cyan]")
    console.print("\n[yellow]Press Ctrl+C to stop[/yellow]\n")

    app = create_app()
    app.run(host=host, port=port, debug=debug)


@app.command()
def stats():
    """Show topology statistics."""
    from database.schema import create_database, get_session
    from core.topology.builder import TopologyBuilder
    from utils.config import get_database_url

    db_url = get_database_url()
    engine = create_database(db_url)
    session = get_session(engine)

    builder = TopologyBuilder(session)
    builder.build_graph()

    statistics = builder.get_statistics()

    console.print("\n[bold cyan]Topology Statistics[/bold cyan]\n")

    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Nodes", str(statistics.get("total_nodes", 0)))
    table.add_row("Total Edges", str(statistics.get("total_edges", 0)))
    table.add_row(
        "Is Connected", "Yes" if statistics.get("is_connected") else "No"
    )
    table.add_row(
        "Connected Components", str(statistics.get("number_of_components", 0))
    )

    if "density" in statistics:
        table.add_row("Network Density", f"{statistics['density']:.4f}")

    if "average_degree" in statistics:
        table.add_row("Average Degree", f"{statistics['average_degree']:.2f}")

    console.print(table)

    # Show central nodes
    if "most_central_nodes" in statistics:
        console.print("\n[bold cyan]Most Central Nodes[/bold cyan]\n")

        central_table = Table(show_header=True)
        central_table.add_column("Node", style="cyan")
        central_table.add_column("Centrality", style="green")

        for node_info in statistics["most_central_nodes"]:
            central_table.add_row(
                node_info["node"], f"{node_info['centrality']:.4f}"
            )

        console.print(central_table)

    console.print()


if __name__ == "__main__":
    app()
