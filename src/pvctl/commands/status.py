"""pvctl status — show all shade positions and battery levels."""

from __future__ import annotations

from typing import Annotated

import typer

from pvctl.api.client import HubClient, HubError
from pvctl.config import get_hub_ip, load_config
from pvctl.display import console, error, print_json, shade_table, shade_table_footer


def status(
    hub: Annotated[str | None, typer.Option("--hub", help="Override hub IP")] = None,
    refresh: Annotated[bool, typer.Option("--refresh", help="Force RF poll (slower)")] = False,
    output_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Show all shade positions and battery levels."""
    config = load_config()
    ip = get_hub_ip(config, override=hub)

    try:
        with HubClient(ip) as client:
            shades = client.get_shades()
            rooms = client.get_rooms()

            if refresh:
                refreshed = []
                for s in shades:
                    try:
                        refreshed.append(client.get_shade(s.id, refresh=True))
                    except HubError:
                        refreshed.append(s)  # Keep stale data if RF poll fails
                shades = refreshed
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None

    room_map = {r.id: r.name for r in rooms}

    if output_json:
        print_json([
            {
                "id": s.id,
                "name": s.name,
                "room": room_map.get(s.roomId, None),
                "type": s.type,
                "position": s.positions.primary_pct if s.has_position else None,
                "battery": s.battery_pct if s.batteryStrength > 0 else None,
                "timedOut": s.timedOut,
            }
            for s in shades
        ])
    else:
        table = shade_table(shades, room_map)
        console.print(table)
        shade_table_footer(shades)
