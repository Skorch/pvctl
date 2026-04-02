"""pvctl room — list rooms."""

from __future__ import annotations

from collections import Counter
from typing import Annotated

import typer

from pvctl.api.client import HubClient, HubError
from pvctl.config import get_hub_ip, load_config
from pvctl.display import console, error, print_json, room_table

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def room_list(
    hub: Annotated[str | None, typer.Option("--hub", help="Override hub IP")] = None,
    output_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """List all rooms with shade counts."""
    config = load_config()
    ip = get_hub_ip(config, override=hub)

    try:
        with HubClient(ip) as client:
            rooms = client.get_rooms()
            shades = client.get_shades()
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None

    shade_counts = Counter(s.roomId for s in shades if s.roomId is not None)

    if output_json:
        print_json([
            {
                "id": r.id,
                "name": r.name,
                "shadeCount": shade_counts.get(r.id, 0),
            }
            for r in rooms
        ])
    else:
        console.print(room_table(rooms, shade_counts))
