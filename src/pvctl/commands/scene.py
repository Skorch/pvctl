"""pvctl scene — list and activate scenes and scene collections."""

from __future__ import annotations

from typing import Annotated

import typer

from pvctl.api.client import HubClient, HubError
from pvctl.config import get_hub_ip, load_config
from pvctl.display import (
    collection_table,
    console,
    error,
    info,
    print_json,
    scene_table,
    success,
)
from pvctl.utils import resolve_name

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def scene_list(
    hub: Annotated[str | None, typer.Option("--hub", help="Override hub IP")] = None,
    output_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """List all scenes and scene collections."""
    config = load_config()
    ip = get_hub_ip(config, override=hub)

    try:
        with HubClient(ip) as client:
            scenes = client.get_scenes()
            collections = client.get_scene_collections()
            rooms = client.get_rooms()
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None

    room_map = {r.id: r.name for r in rooms}

    if output_json:
        print_json({
            "scenes": [
                {"id": s.id, "name": s.name, "room": room_map.get(s.roomId, None)}
                for s in scenes
            ],
            "collections": [
                {"id": c.id, "name": c.name}
                for c in collections
            ],
        })
    else:
        console.print(scene_table(scenes, room_map))
        console.print()
        console.print(collection_table(collections))


@app.command()
def activate(
    name: Annotated[str, typer.Argument(help="Scene or collection name (fuzzy matched)")],
    hub: Annotated[str | None, typer.Option("--hub", help="Override hub IP")] = None,
    output_json: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
):
    """Activate a scene or scene collection by name."""
    config = load_config()
    ip = get_hub_ip(config, override=hub)

    try:
        with HubClient(ip) as client:
            scenes = client.get_scenes()
            collections = client.get_scene_collections()

            # Try scenes first, then collections
            all_items = [(s, "scene") for s in scenes] + [(c, "collection") for c in collections]
            matched_item, item_type = resolve_name(
                name,
                all_items,
                lambda x: x[0].name,
                "scene/collection",
            )

            if item_type == "scene":
                result = client.activate_scene(matched_item.id)
                shade_ids = result.get("scene", {}).get("shadeIds", [])
                label = f"scene: {matched_item.name}"
                shade_count = len(shade_ids)
            else:
                client.activate_scene_collection(matched_item.id)
                label = f"collection: {matched_item.name}"
                shade_count = None
    except HubError as e:
        error(str(e))
        raise typer.Exit(2) from None

    if output_json:
        data = {"name": matched_item.name, "type": item_type, "id": matched_item.id}
        if shade_count is not None:
            data["shadeCount"] = shade_count
        print_json(data)
    else:
        info(f"Activating {label}")
        if shade_count is not None:
            success(f"Done ({shade_count} shades)")
        else:
            success("Done")
