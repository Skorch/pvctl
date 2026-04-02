"""pvctl hub — hub info and management."""

from __future__ import annotations

from typing import Annotated

import typer

from pvctl.api.client import HubClient, HubError
from pvctl.config import get_hub_ip, load_config
from pvctl.display import console, error, hub_panel, print_json

app = typer.Typer(no_args_is_help=True)


@app.command()
def info(
    hub: Annotated[str | None, typer.Option("--hub", help="Override hub IP")] = None,
    output_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Show hub info: firmware, serial, device counts."""
    config = load_config()
    ip = get_hub_ip(config, override=hub)

    try:
        with HubClient(ip) as client:
            userdata = client.get_userdata()
            firmware = client.get_firmware()
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None

    if output_json:
        print_json({
            "name": userdata.hubName,
            "ip": userdata.ip,
            "serial": userdata.serialNumber,
            "mac": userdata.macAddress,
            "firmware": firmware.version_str,
            "shades": userdata.shadeCount,
            "rooms": userdata.roomCount,
            "scenes": userdata.sceneCount,
            "collections": userdata.multiSceneCount,
            "schedules": userdata.scheduledEventCount,
        })
    else:
        console.print(hub_panel(userdata, firmware))
