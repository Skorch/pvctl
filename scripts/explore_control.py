#!/usr/bin/env python3
"""Explore shade control: PUT /api/shades/{id} for position and motion.

This script MOVES SHADES. It will prompt before each action.

Usage: uv run python scripts/explore_control.py <hub-ip>
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
        print("Usage: uv run python scripts/explore_control.py <hub-ip>")
        sys.exit(1)

    hub_ip = sys.argv[1]
    base = f"http://{hub_ip}/api"
    client = httpx.Client(timeout=30)

    # First, list shades so user can pick one
    r = client.get(f"{base}/shades")
    data = r.json()
    shades = data.get("shadeData", [])

    print("\nAvailable shades:")
    for i, s in enumerate(shades):
        name = decode_name(s.get("name", ""))
        sid = s.get("id")
        pos = s.get("positions", {})
        print(f"  {i}: {name} (id={sid}, positions={pos})")

    choice = input("\nEnter shade number to control (or 'quit'): ").strip()
    if choice == "quit" or not choice.isdigit():
        print("Exiting.")
        return

    idx = int(choice)
    if idx < 0 or idx >= len(shades):
        print("Invalid index.")
        return

    shade = shades[idx]
    shade_id = shade["id"]
    shade_name = decode_name(shade.get("name", ""))
    print(f"\nSelected: {shade_name} (id={shade_id})")

    # --- Test 1: Jog (identify) ---
    if input("\nTest JOG (brief wiggle to identify)? [y/N]: ").strip().lower() == "y":
        print(f"  PUT {base}/shades/{shade_id}")
        body = {"shade": {"motion": "jog"}}
        print(f"  Body: {json.dumps(body)}")
        r = client.put(f"{base}/shades/{shade_id}", json=body)
        print(f"  Status: {r.status_code}")
        try:
            resp = r.json()
            print(json.dumps(resp, indent=2))
            save(f"control_jog_{shade_id}", resp)
        except Exception:
            print(f"  Body: {r.text}")

    # --- Test 2: Set position to 50% ---
    if input("\nTest SET to 50%? [y/N]: ").strip().lower() == "y":
        pos_value = round(50 / 100 * 65535)
        body = {"shade": {"positions": {"posKind1": 1, "position1": pos_value}}}
        print(f"  PUT {base}/shades/{shade_id}")
        print(f"  Body: {json.dumps(body)}")
        print(f"  (position1={pos_value} = 50%)")
        r = client.put(f"{base}/shades/{shade_id}", json=body)
        print(f"  Status: {r.status_code}")
        try:
            resp = r.json()
            print(json.dumps(resp, indent=2))
            save(f"control_set50_{shade_id}", resp)
        except Exception:
            print(f"  Body: {r.text}")

    # --- Test 3: Fully open ---
    if input("\nTest OPEN (100%)? [y/N]: ").strip().lower() == "y":
        body = {"shade": {"positions": {"posKind1": 1, "position1": 65535}}}
        print(f"  PUT {base}/shades/{shade_id}")
        print(f"  Body: {json.dumps(body)}")
        r = client.put(f"{base}/shades/{shade_id}", json=body)
        print(f"  Status: {r.status_code}")
        try:
            resp = r.json()
            print(json.dumps(resp, indent=2))
            save(f"control_open_{shade_id}", resp)
        except Exception:
            print(f"  Body: {r.text}")

    # --- Test 4: Fully close ---
    if input("\nTest CLOSE (0%)? [y/N]: ").strip().lower() == "y":
        body = {"shade": {"positions": {"posKind1": 1, "position1": 0}}}
        print(f"  PUT {base}/shades/{shade_id}")
        print(f"  Body: {json.dumps(body)}")
        r = client.put(f"{base}/shades/{shade_id}", json=body)
        print(f"  Status: {r.status_code}")
        try:
            resp = r.json()
            print(json.dumps(resp, indent=2))
            save(f"control_close_{shade_id}", resp)
        except Exception:
            print(f"  Body: {r.text}")

    # --- Test 5: Stop command ---
    if input("\nTest STOP (halt motion)? [y/N]: ").strip().lower() == "y":
        body = {"shade": {"motion": "stop"}}
        print(f"  PUT {base}/shades/{shade_id}")
        print(f"  Body: {json.dumps(body)}")
        r = client.put(f"{base}/shades/{shade_id}", json=body)
        print(f"  Status: {r.status_code}")
        try:
            resp = r.json()
            print(json.dumps(resp, indent=2))
            save(f"control_stop_{shade_id}", resp)
        except Exception:
            print(f"  Body: {r.text}")

    print("\nDone. Check scripts/responses/ for saved JSON.")


if __name__ == "__main__":
    main()
