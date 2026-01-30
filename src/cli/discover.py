"""Discovery commands for CLI."""

import typer
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer()
console = Console()


@app.command()
def run(
    config: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    max_depth: Optional[int] = typer.Option(
        None, "--max-depth", "-d", help="Maximum discovery depth"
    ),
    max_workers: Optional[int] = typer.Option(
        None, "--max-workers", "-w", help="Maximum parallel workers"
    ),
):
    """Run network discovery."""
    from core.discovery.engine import DiscoveryEngine
    from rich.panel import Panel

    console.print(
        Panel.fit(
            "[bold cyan]Network Discovery Tool[/bold cyan]\n"
            "Starting discovery process...",
            border_style="cyan",
        )
    )

    try:
        # Initialize discovery engine
        engine = DiscoveryEngine(
            config_path=config, max_depth=max_depth, max_workers=max_workers
        )

        # Start discovery
        summary = engine.start_discovery()

        # Display summary
        console.print(
            Panel.fit(
                f"[green]✓ Discovery completed successfully![/green]\n\n"
                f"[cyan]Devices discovered:[/cyan] {summary['devices_discovered']}\n"
                f"[cyan]Total interfaces:[/cyan] {summary['total_interfaces']}\n"
                f"[cyan]Total connections:[/cyan] {summary['total_connections']}\n"
                f"[cyan]Total MAC entries:[/cyan] {summary['total_mac_entries']}\n"
                f"[yellow]Errors:[/yellow] {summary['errors']}",
                title="[bold green]Discovery Summary[/bold green]",
                border_style="green",
            )
        )

        # Show errors if any
        if summary["errors"] > 0:
            console.print(
                "\n[yellow]Some errors occurred during discovery:[/yellow]"
            )
            for error in summary["error_list"][:10]:  # Show first 10
                console.print(f"  [red]•[/red] {error.get('device')}: {error.get('error')}")

    except FileNotFoundError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Discovery failed:[/red] {e}")
        console.print("[yellow]Check logs for more details[/yellow]")
        raise typer.Exit(1)


@app.command()
def status():
    """Show last discovery session status."""
    from database.schema import create_database, get_session
    from database.repository import DiscoverySessionRepository
    from utils.config import get_database_url
    from rich.table import Table

    db_url = get_database_url()
    engine = create_database(db_url)
    session = get_session(engine)

    repo = DiscoverySessionRepository(session)
    last_session = repo.get_latest()

    if not last_session:
        console.print("[yellow]No discovery sessions found[/yellow]")
        return

    # Create status table
    table = Table(title="Last Discovery Session", show_header=False, box=None)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Session ID", str(last_session.id))
    table.add_row("Status", last_session.status)
    table.add_row(
        "Started At",
        last_session.started_at.strftime("%Y-%m-%d %H:%M:%S")
        if last_session.started_at
        else "unknown",
    )

    if last_session.completed_at:
        table.add_row(
            "Completed At", last_session.completed_at.strftime("%Y-%m-%d %H:%M:%S")
        )

        # Calculate duration
        duration = last_session.completed_at - last_session.started_at
        table.add_row("Duration", str(duration))

    table.add_row("Devices Discovered", str(last_session.devices_discovered))
    table.add_row("Interfaces Discovered", str(last_session.interfaces_discovered))
    table.add_row("Connections Discovered", str(last_session.connections_discovered))

    console.print(table)

    # Show errors if any
    if last_session.errors:
        console.print("\n[yellow]Errors:[/yellow]")
        for error in last_session.errors[:5]:  # Show first 5
            console.print(f"  [red]•[/red] {error}")
