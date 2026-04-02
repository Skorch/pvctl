"""Typer CLI app definition with command groups and global flags."""

from __future__ import annotations

from typing import Annotated

import typer

from pvctl import __version__
from pvctl.commands import hub, init, room, scene, schedule, shade, status

app = typer.Typer(
    name="pvctl",
    help="CLI manager for Hunter Douglas PowerView blinds.",
    no_args_is_help=True,
)

# Register command groups
app.add_typer(hub.app, name="hub", help="Hub info and management.")
app.add_typer(shade.app, name="shade", help="Control individual shades.")
app.add_typer(scene.app, name="scene", help="List and activate scenes.")
app.add_typer(room.app, name="room", help="List rooms.")
app.add_typer(schedule.app, name="schedule", help="Manage local schedules.")

# Register top-level commands
app.command()(init.init)
app.command()(status.status)


@app.callback()
def main(
    quiet: Annotated[
        bool, typer.Option("--quiet", "-q", help="Minimal output (for cron/scripts)")
    ] = False,
):
    """CLI manager for Hunter Douglas PowerView blinds."""
    if quiet:
        from pvctl.display import set_quiet

        set_quiet(True)


@app.command()
def version():
    """Show pvctl version."""
    typer.echo(f"pvctl {__version__}")
