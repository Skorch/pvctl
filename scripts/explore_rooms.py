#!/usr/bin/env python3
"""Explore room endpoint: /api/rooms.

Usage: uv run python scripts/explore_rooms.py <hub-ip>
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
        print("Usage: uv run python scripts/explore_rooms.py <hub-ip>")
        sys.exit(1)

    hub_ip = sys.argv[1]
    base = f"http://{hub_ip}/api"
    client = httpx.Client(timeout=10)

    # --- GET /api/rooms ---
    print(f"\n{'='*60}")
    print(f"GET {base}/rooms")
    print(f"{'='*60}")
    r = client.get(f"{base}/rooms")
    data = r.json()
    print(json.dumps(data, indent=2))
    save("rooms_list", data)

    rooms = data.get("roomData", [])
    print(f"\n  Found {len(rooms)} rooms:")
    for room in rooms:
        name = decode_name(room.get("name", ""))
        rid = room.get("id", "?")
        print(f"    [{rid}] {name}")
        # Print all fields for discovery
        for k, v in room.items():
            if k not in ("name", "id"):
                print(f"      {k}: {v}")

    print("\nDone. Check scripts/responses/ for saved JSON.")


if __name__ == "__main__":
    main()
