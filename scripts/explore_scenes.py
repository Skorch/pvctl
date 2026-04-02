#!/usr/bin/env python3
"""Explore scene endpoints: /api/scenes and scene activation.

Lists all scenes. Optionally activates one (with confirmation prompt).

Usage: uv run python scripts/explore_scenes.py <hub-ip>
"""

import base64
import json
import sys
from pathlib import Path

import httpx

RESPONSES_DIR = Path(__file__).parent / "responses"


def save(name: str, data: dict) -> None:
    RESPONSES_DIR.mkdir(exist_ok=True)
    path = RESPONSES_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2))
    print(f"  Saved to {path}")


def decode_name(b64: str) -> str:
    try:
        return base64.b64decode(b64).decode("utf-8")
    except Exception:
        return f"<decode error: {b64}>"


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/explore_scenes.py <hub-ip>")
        sys.exit(1)

    hub_ip = sys.argv[1]
    base = f"http://{hub_ip}/api"
    client = httpx.Client(timeout=10)

    # --- GET /api/scenes ---
    print(f"\n{'='*60}")
    print(f"GET {base}/scenes")
    print(f"{'='*60}")
    r = client.get(f"{base}/scenes")
    data = r.json()
    print(json.dumps(data, indent=2))
    save("scenes_list", data)

    scenes = data.get("sceneData", [])
    print(f"\n  Found {len(scenes)} scenes:")
    for s in scenes:
        name = decode_name(s.get("name", ""))
        sid = s.get("id", "?")
        room_id = s.get("roomId", "?")
        print(f"    [{sid}] {name}  (roomId={room_id})")

    # --- Scene activation ---
    if scenes:
        print(f"\n{'='*60}")
        print("Scene activation test")
        print(f"{'='*60}")
        print("Available scenes:")
        for i, s in enumerate(scenes):
            name = decode_name(s.get("name", ""))
            print(f"  {i}: {name} (id={s['id']})")

        choice = input("\nEnter scene number to activate (or 'skip'): ").strip()
        if choice != "skip" and choice.isdigit():
            idx = int(choice)
            if 0 <= idx < len(scenes):
                scene = scenes[idx]
                scene_id = scene["id"]
                scene_name = decode_name(scene.get("name", ""))
                print(f"\n  Activating scene: {scene_name} (id={scene_id})")
                print(f"  GET {base}/scenes?sceneid={scene_id}")
                r = client.get(f"{base}/scenes", params={"sceneid": scene_id})
                print(f"  Status: {r.status_code}")
                try:
                    resp = r.json()
                    print(json.dumps(resp, indent=2))
                    save(f"scene_activate_{scene_id}", resp)
                except Exception:
                    print(f"  Body: {r.text}")
                    save(f"scene_activate_{scene_id}", {"status": r.status_code, "body": r.text})
            else:
                print("  Invalid index")
        else:
            print("  Skipped activation")

    print("\nDone. Check scripts/responses/ for saved JSON.")


if __name__ == "__main__":
    main()
