"""pvctl shade — control individual shades."""

from __future__ import annotations

from typing import Annotated

import typer

from pvctl.api.client import HubClient, HubError
from pvctl.config import get_hub_ip, load_config
from pvctl.display import console, error, print_json, shade_confirm
from pvctl.utils import pct_to_pos, resolve_name

app = typer.Typer(no_args_is_help=True)


def _get_client_and_shades(hub_override: str | None = None):
    """Shared setup for shade commands."""
    config = load_config()
    ip = get_hub_ip(config, override=hub_override)
    client = HubClient(ip)
    try:
        shades = client.get_shades()
    except HubError as e:
        client.close()
        error(str(e))
        raise typer.Exit(2) from None
    return client, shades


@app.command("open")
def shade_open(
    name: Annotated[str, typer.Argument(help="Shade name (fuzzy matched)")],
    hub: Annotated[str | None, typer.Option("--hub", help="Override hub IP")] = None,
    output_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Fully open a shade (100%)."""
    client, shades = _get_client_and_shades(hub)
    shade = resolve_name(name, shades, lambda s: s.name, "shade")

    try:
        client.set_shade_position(shade.id, pct_to_pos(100))
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None
    finally:
        client.close()

    if output_json:
        print_json({"id": shade.id, "name": shade.name, "position": 100})
    else:
        shade_confirm(shade.name, 100)


@app.command("close")
def shade_close(
    name: Annotated[str, typer.Argument(help="Shade name (fuzzy matched)")],
    hub: Annotated[str | None, typer.Option("--hub", help="Override hub IP")] = None,
    output_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Fully close a shade (0%)."""
    client, shades = _get_client_and_shades(hub)
    shade = resolve_name(name, shades, lambda s: s.name, "shade")

    try:
        client.set_shade_position(shade.id, pct_to_pos(0))
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None
    finally:
        client.close()

    if output_json:
        print_json({"id": shade.id, "name": shade.name, "position": 0})
    else:
        shade_confirm(shade.name, 0)


@app.command("set")
def shade_set(
    name: Annotated[str, typer.Argument(help="Shade name (fuzzy matched)")],
    position: Annotated[int, typer.Argument(help="Position 0-100", min=0, max=100)],
    hub: Annotated[str | None, typer.Option("--hub", help="Override hub IP")] = None,
    output_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Set a shade to a specific position (0-100%)."""
    client, shades = _get_client_and_shades(hub)
    shade = resolve_name(name, shades, lambda s: s.name, "shade")

    try:
        client.set_shade_position(shade.id, pct_to_pos(position))
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None
    finally:
        client.close()

    if output_json:
        print_json({"id": shade.id, "name": shade.name, "position": position})
    else:
        shade_confirm(shade.name, position)


@app.command()
def jog(
    name: Annotated[str, typer.Argument(help="Shade name (fuzzy matched)")],
    hub: Annotated[str | None, typer.Option("--hub", help="Override hub IP")] = None,
):
    """Jog a shade (brief wiggle to identify it)."""
    client, shades = _get_client_and_shades(hub)
    shade = resolve_name(name, shades, lambda s: s.name, "shade")

    try:
        client.jog_shade(shade.id)
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None
    finally:
        client.close()

    console.print(f"  ⟳ Jogging {shade.name}")


@app.command()
def stop(
    name: Annotated[str, typer.Argument(help="Shade name (fuzzy matched)")],
    hub: Annotated[str | None, typer.Option("--hub", help="Override hub IP")] = None,
):
    """Stop a shade's current motion."""
    client, shades = _get_client_and_shades(hub)
    shade = resolve_name(name, shades, lambda s: s.name, "shade")

    try:
        client.stop_shade(shade.id)
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None
    finally:
        client.close()

    console.print(f"  ⏹ Stopped {shade.name}")
