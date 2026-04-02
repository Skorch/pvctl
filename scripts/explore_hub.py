#!/usr/bin/env python3
"""Explore hub info endpoints: /api/userdata and /api/fwversion.

Usage: uv run python scripts/explore_hub.py <hub-ip>
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


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/explore_hub.py <hub-ip>")
        sys.exit(1)

    hub_ip = sys.argv[1]
    base = f"http://{hub_ip}/api"
    client = httpx.Client(timeout=10)

    # --- /api/userdata ---
    print(f"\n{'='*60}")
    print(f"GET {base}/userdata")
    print(f"{'='*60}")
    r = client.get(f"{base}/userdata")
    data = r.json()
    print(json.dumps(data, indent=2))

    # Decode hub name if present
    ud = data.get("userData", {})
    if "hubName" in ud:
        try:
            name = base64.b64decode(ud["hubName"]).decode("utf-8")
            print(f"\n  Decoded hubName: {name}")
        except Exception as e:
            print(f"\n  Failed to decode hubName: {e}")

    save("userdata", data)

    # --- /api/fwversion ---
    print(f"\n{'='*60}")
    print(f"GET {base}/fwversion")
    print(f"{'='*60}")
    r = client.get(f"{base}/fwversion")
    data = r.json()
    print(json.dumps(data, indent=2))
    save("fwversion", data)

    print("\nDone. Check scripts/responses/ for saved JSON.")


if __name__ == "__main__":
    main()
