"""pvctl schedule — sync hub schedules to cron and manage them."""

from __future__ import annotations

from typing import Annotated

import typer

from pvctl.api.client import HubClient, HubError
from pvctl.config import get_hub_ip, load_config
from pvctl.display import console, error, print_json, success
from pvctl.schedule_manager import (
    get_pvctl_cron_entries,
    hub_events_to_entries,
    install_sync_cron,
    load_sync_config,
    save_default_schedule_config,
    sync_schedule,
    uninstall_all,
)

app = typer.Typer(no_args_is_help=True)


@app.command()
def install():
    """Set up cron to sync hub schedules every N minutes.

    Creates the sync config file if it doesn't exist, fetches hub schedules,
    installs them as cron entries, and adds a sync cron to keep them updated.
    """
    config = load_config()
    ip = get_hub_ip(config)

    # Ensure schedule config exists
    config_path = save_default_schedule_config()
    sync_config = load_sync_config()
    interval = sync_config["interval"]

    # Fetch and sync hub schedules
    try:
        with HubClient(ip) as client:
            events = client.get_scheduled_events()
            collections = client.get_scene_collections()
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None

    collection_map = {c.id: c.name for c in collections}
    entries = hub_events_to_entries(events, collection_map)

    console.print(f"\n  Syncing {len(entries)} hub schedules to crontab...")
    results = sync_schedule(entries)

    active = 0
    for name, cron_expr, enabled in results:
        if enabled:
            success(f"{name:<25} \u2192 {cron_expr}")
            active += 1
        else:
            console.print(f"  [dim]\u2298 {name:<25} \u2192 disabled[/dim]")

    # Install sync cron
    sync_expr = install_sync_cron(interval)
    success(f"Sync cron installed: every {interval}min ({sync_expr})")
    console.print(f"\n  {active} schedule entries active. Config: {config_path}")
    console.print("  Verify with 'pvctl schedule show' or 'crontab -l'.")


@app.command()
def sync(
    quiet: Annotated[bool, typer.Option("--quiet", "-q", hidden=True)] = False,
):
    """Fetch hub schedules and update cron entries.

    This is called automatically by the sync cron. Can also be run manually.
    """
    config = load_config()
    ip = get_hub_ip(config)

    try:
        with HubClient(ip) as client:
            events = client.get_scheduled_events()
            collections = client.get_scene_collections()
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None

    collection_map = {c.id: c.name for c in collections}
    entries = hub_events_to_entries(events, collection_map)
    results = sync_schedule(entries)

    if not quiet:
        active = sum(1 for _, _, enabled in results if enabled)
        disabled = sum(1 for _, _, enabled in results if not enabled)
        success(f"Synced {active} active, {disabled} disabled schedule entries")


@app.command()
def show(
    output_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Show currently installed pvctl cron entries."""
    cron_lines = get_pvctl_cron_entries()

    if not cron_lines:
        console.print("  No pvctl cron entries installed. Run 'pvctl schedule install'.")
        return

    if output_json:
        print_json(cron_lines)
        return

    from rich.table import Table

    table = Table(title="Installed pvctl Cron Entries", show_lines=True)
    table.add_column("", width=1)
    table.add_column("Cron Entry")

    for line in cron_lines:
        if line.startswith("# DISABLED:"):
            table.add_row("[dim]\u25cb[/dim]", f"[dim]{line}[/dim]")
        elif "pvctl-sync" in line:
            table.add_row("[blue]\u21bb[/blue]", line)
        else:
            table.add_row("[green]\u25cf[/green]", line)

    console.print(table)

    sync_config = load_sync_config()
    console.print(
        "  [green]●[/green] active schedule   "
        "[dim]○[/dim] disabled   "
        "[blue]↻[/blue] sync cron"
    )
    console.print(f"  Sync interval: every {sync_config['interval']}min")


@app.command()
def uninstall():
    """Remove all pvctl entries (schedules + sync) from crontab."""
    removed = uninstall_all()
    if removed > 0:
        success(f"Removed {removed} entries")
    else:
        console.print("  No pvctl entries found in crontab.")
