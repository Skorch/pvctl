"""pvctl init — connect to hub, discover devices, write config."""

from __future__ import annotations

from typing import Annotated

import typer

from pvctl.api.client import HubClient, HubError
from pvctl.config import save_config
from pvctl.display import error, success


def init(
    hub_ip: Annotated[str, typer.Argument(help="Hub IP address (e.g. 192.168.7.38)")],
):
    """Connect to hub, discover devices, and write config."""
    try:
        with HubClient(hub_ip) as hub:
            userdata = hub.get_userdata()
            firmware = hub.get_firmware()
            shades = hub.get_shades()
            scenes = hub.get_scenes()
            collections = hub.get_scene_collections()
            rooms = hub.get_rooms()
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None

    config = {
        "hub": {
            "ip": hub_ip,
            "name": userdata.hubName,
            "serial": userdata.serialNumber,
            "firmware": firmware.version_str,
        },
        "cache": {
            "shades": {
                s.id: {"name": s.name, "roomId": s.roomId, "type": s.type}
                for s in shades
            },
            "scenes": {
                s.id: {"name": s.name, "roomId": s.roomId}
                for s in scenes
            },
            "collections": {
                c.id: {"name": c.name}
                for c in collections
            },
            "rooms": {
                r.id: {"name": r.name}
                for r in rooms
            },
        },
    }

    path = save_config(config)
    success(f"Connected to hub at {hub_ip}")
    success(
        f"Found {len(shades)} shades, {len(rooms)} rooms, "
        f"{len(scenes)} scenes, {len(collections)} collections"
    )
    success(f"Config written to {path}")
    typer.echo("\n  Run 'pvctl status' to see your shades.")
