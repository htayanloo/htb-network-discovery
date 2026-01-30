"""Search commands for CLI."""

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command()
def mac(mac_address: str):
    """Search for a MAC address in the network."""
    from database.schema import create_database, get_session
    from database.repository import MacRepository
    from utils.config import get_database_url
    from utils.validators import normalize_mac

    try:
        # Normalize MAC address
        normalized_mac = normalize_mac(mac_address)
    except ValueError as e:
        console.print(f"[red]Invalid MAC address:[/red] {e}")
        raise typer.Exit(1)

    db_url = get_database_url()
    engine = create_database(db_url)
    session = get_session(engine)

    repo = MacRepository(session)
    entries = repo.search_mac(normalized_mac)

    if not entries:
        console.print(f"[yellow]MAC address {normalized_mac} not found[/yellow]")
        return

    # Create table
    table = Table(title=f"MAC Address: {normalized_mac}", show_header=True)
    table.add_column("Device", style="cyan")
    table.add_column("Interface", style="blue")
    table.add_column("VLAN", style="green")
    table.add_column("Type", style="magenta")
    table.add_column("Last Seen")

    for entry in entries:
        table.add_row(
            entry.device.hostname,
            entry.interface.name if entry.interface else "unknown",
            str(entry.vlan_id),
            entry.type,
            entry.last_seen.strftime("%Y-%m-%d %H:%M:%S")
            if entry.last_seen
            else "unknown",
        )

    console.print(table)
    console.print(
        f"\n[green]Found {len(entries)} location(s) for MAC address {normalized_mac}[/green]"
    )


@app.command()
def device(query: str):
    """Search for a device by hostname or IP address."""
    from database.schema import create_database, get_session
    from database.repository import DeviceRepository
    from utils.config import get_database_url

    db_url = get_database_url()
    engine = create_database(db_url)
    session = get_session(engine)

    repo = DeviceRepository(session)

    # Try exact match first
    device = repo.get_by_hostname(query)
    if not device:
        device = repo.get_by_ip(query)

    # Try fuzzy search
    if not device:
        devices = repo.search(query)
        if len(devices) == 1:
            device = devices[0]
        elif len(devices) > 1:
            console.print(f"[yellow]Multiple devices found matching '{query}':[/yellow]\n")

            # Create table
            table = Table(show_header=True)
            table.add_column("Hostname", style="cyan")
            table.add_column("IP Address", style="blue")
            table.add_column("Type", style="green")
            table.add_column("Model")

            for dev in devices:
                table.add_row(
                    dev.hostname,
                    dev.ip_address,
                    dev.device_type or "unknown",
                    dev.model or "unknown",
                )

            console.print(table)
            return

    if not device:
        console.print(f"[yellow]Device '{query}' not found[/yellow]")
        return

    # Display device details
    console.print(f"\n[bold cyan]{device.hostname}[/bold cyan]\n")

    # Create details table
    details_table = Table(show_header=False, box=None)
    details_table.add_column("Field", style="cyan")
    details_table.add_column("Value", style="white")

    details_table.add_row("IP Address", device.ip_address)
    details_table.add_row("Device Type", device.device_type or "unknown")
    details_table.add_row("Model", device.model or "unknown")
    details_table.add_row("IOS Version", device.ios_version or "unknown")
    details_table.add_row("Serial Number", device.serial_number or "unknown")
    details_table.add_row("Uptime", device.uptime or "unknown")
    details_table.add_row(
        "Last Discovered",
        device.last_discovered.strftime("%Y-%m-%d %H:%M:%S")
        if device.last_discovered
        else "unknown",
    )

    console.print(details_table)

    # Show interfaces
    if device.interfaces:
        console.print(f"\n[bold cyan]Interfaces ({len(device.interfaces)}):[/bold cyan]\n")

        interface_table = Table(show_header=True)
        interface_table.add_column("Name", style="cyan")
        interface_table.add_column("Status", style="green")
        interface_table.add_column("Speed")
        interface_table.add_column("VLAN")
        interface_table.add_column("Type")
        interface_table.add_column("Description")

        for interface in device.interfaces[:20]:  # Show first 20
            status_color = "green" if interface.status == "up" else "red"
            interface_type = "Trunk" if interface.is_trunk else "Access"

            interface_table.add_row(
                interface.name,
                f"[{status_color}]{interface.status}[/{status_color}]",
                interface.speed or "unknown",
                str(interface.vlan_id) if interface.vlan_id else "N/A",
                interface_type,
                interface.description or "",
            )

        console.print(interface_table)

        if len(device.interfaces) > 20:
            console.print(
                f"[yellow]... and {len(device.interfaces) - 20} more interfaces[/yellow]"
            )

    # Show neighbors
    from database.repository import ConnectionRepository

    conn_repo = ConnectionRepository(session)
    neighbors = conn_repo.get_neighbors(device.id)

    if neighbors:
        console.print(f"\n[bold cyan]Neighbors ({len(neighbors)}):[/bold cyan]\n")

        neighbor_table = Table(show_header=True)
        neighbor_table.add_column("Hostname", style="cyan")
        neighbor_table.add_column("IP Address", style="blue")
        neighbor_table.add_column("Type", style="green")

        for neighbor in neighbors:
            neighbor_table.add_row(
                neighbor.hostname,
                neighbor.ip_address,
                neighbor.device_type or "unknown",
            )

        console.print(neighbor_table)

    console.print()
