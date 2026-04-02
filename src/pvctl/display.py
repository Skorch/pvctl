"""Rich rendering helpers for pvctl output."""

from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pvctl.api.models import (
    FirmwareVersion,
    Room,
    Scene,
    SceneCollection,
    ScheduledEvent,
    Shade,
    UserData,
)

console = Console()
err_console = Console(stderr=True)

# Quiet mode flag — set by CLI --quiet flag. Suppresses Rich output for cron/scripts.
_quiet = False


def set_quiet(quiet: bool) -> None:
    global _quiet
    _quiet = quiet

BATTERY_WARN = 20
BATTERY_CRITICAL = 10
POSITION_BAR_WIDTH = 20


def success(msg: str) -> None:
    if not _quiet:
        console.print(f"  [green]✓[/green] {msg}")


def error(msg: str) -> None:
    # Errors always print, even in quiet mode
    err_console.print(f"  [red]✗[/red] {msg}")


def warn(msg: str) -> None:
    if not _quiet:
        console.print(f"  [yellow]⚠[/yellow] {msg}")


def info(msg: str) -> None:
    if not _quiet:
        console.print(f"  [blue]▶[/blue] {msg}")


def render_position_bar(pct: int, width: int = POSITION_BAR_WIDTH) -> str:
    """Block character position bar: █ filled, ░ empty."""
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def render_battery(pct: int) -> Text:
    """Color-coded battery percentage."""
    if pct == 0:
        return Text("—", style="dim")
    if pct < BATTERY_CRITICAL:
        style = "bold red"
    elif pct < BATTERY_WARN:
        style = "yellow"
    else:
        style = "green"
    return Text(f"{pct}%", style=style)


def shade_table(shades: list[Shade], room_map: dict[int, str] | None = None) -> Table:
    """Rich table of shade status."""
    table = Table(title="PowerView Shade Status", show_lines=True)
    table.add_column("Shade", style="bold")
    table.add_column("Room")
    table.add_column("Position")
    table.add_column("Battery", justify="right")

    low_battery: list[str] = []

    for s in shades:
        room = room_map.get(s.roomId, "") if room_map and s.roomId else ""

        if s.has_position:
            pct = s.positions.primary_pct
            pos_text = Text(f"{render_position_bar(pct)} {pct:>3}%")
        else:
            pos_text = Text("—", style="dim")

        batt = render_battery(s.battery_pct)
        if 0 < s.battery_pct < BATTERY_WARN:
            low_battery.append(s.name)

        table.add_row(s.name, room, pos_text, batt)

    return table


def shade_table_footer(shades: list[Shade]) -> None:
    """Print footer summary and legend below shade table."""
    online = len([s for s in shades if s.roomId is not None])
    low = [s.name for s in shades if 0 < s.battery_pct < BATTERY_WARN]

    console.print(f"  [bold]{online}[/bold] shades online")
    if low:
        console.print(
            f"  [yellow]⚠ {len(low)} low battery ({', '.join(low)})[/yellow]"
        )
    console.print(
        "  [dim]Battery: [green]■[/green] ≥20%  "
        "[yellow]■[/yellow] 10–19%  "
        "[bold red]■[/bold red] <10%  "
        "— unknown[/dim]"
    )
    console.print(
        "  [dim]Position: █ open  ░ closed  — no data (use --refresh to poll)[/dim]"
    )


def hub_panel(userdata: UserData, firmware: FirmwareVersion) -> Panel:
    """Rich panel with hub metadata."""
    lines = [
        f"  [bold]Name:[/bold]       {userdata.hubName}",
        f"  [bold]IP:[/bold]         {userdata.ip}",
        f"  [bold]Serial:[/bold]     {userdata.serialNumber}",
        f"  [bold]MAC:[/bold]        {userdata.macAddress}",
        f"  [bold]Firmware:[/bold]   {firmware.version_str}",
        "",
        f"  [bold]Shades:[/bold]     {userdata.shadeCount}",
        f"  [bold]Rooms:[/bold]      {userdata.roomCount}",
        f"  [bold]Scenes:[/bold]     {userdata.sceneCount}",
        f"  [bold]Collections:[/bold] {userdata.multiSceneCount}",
        f"  [bold]Schedules:[/bold]  {userdata.scheduledEventCount} (hub-side)",
    ]
    return Panel("\n".join(lines), title="PowerView Hub", border_style="blue")


def scene_table(scenes: list[Scene], room_map: dict[int, str] | None = None) -> Table:
    """Rich table of scenes."""
    table = Table(title="PowerView Scenes", show_lines=True)
    table.add_column("ID", justify="right")
    table.add_column("Name", style="bold")
    table.add_column("Room")

    for s in scenes:
        room = room_map.get(s.roomId, "") if room_map else ""
        table.add_row(str(s.id), s.name, room)

    return table


def collection_table(collections: list[SceneCollection]) -> Table:
    """Rich table of scene collections."""
    table = Table(title="PowerView Scene Collections", show_lines=True)
    table.add_column("ID", justify="right")
    table.add_column("Name", style="bold")

    for c in collections:
        table.add_row(str(c.id), c.name)

    return table


def room_table(
    rooms: list[Room], shade_counts: dict[int, int] | None = None
) -> Table:
    """Rich table of rooms."""
    table = Table(title="PowerView Rooms", show_lines=True)
    table.add_column("ID", justify="right")
    table.add_column("Room", style="bold")
    table.add_column("Shades", justify="right")

    for r in rooms:
        count = str(shade_counts.get(r.id, 0)) if shade_counts else ""
        table.add_row(str(r.id), r.name, count)

    return table


def schedule_table(
    events: list[ScheduledEvent],
    collection_map: dict[int, str] | None = None,
) -> Table:
    """Rich table of hub-side scheduled events."""
    table = Table(title="Hub Scheduled Events", show_lines=True)
    table.add_column("", width=1)
    table.add_column("Time", justify="right")
    table.add_column("Days")
    table.add_column("Action")

    for e in events:
        dot = "[green]●[/green]" if e.enabled else "[dim]○[/dim]"
        cid = str(e.sceneCollectionId)
        action = collection_map.get(e.sceneCollectionId, cid) if collection_map else cid
        table.add_row(dot, e.time_str, " ".join(e.days_list), action)

    return table


def print_json(data: object) -> None:
    """Print JSON to stdout."""
    print(json.dumps(data, indent=2, default=str))


def shade_confirm(name: str, pct: int) -> None:
    """Print shade move confirmation with mini bar."""
    console.print(f"  {name} → {pct}%  {render_position_bar(pct)}")
