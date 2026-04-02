#!/usr/bin/env python3
"""Explore shade endpoints: /api/shades and /api/shades/{id}.

Captures all shade data, decodes names, shows battery and position values.
Also times a ?refresh=true request to see how much slower RF polling is.

Usage: uv run python scripts/explore_shades.py <hub-ip>
"""

import base64
import json
import sys
import time
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
        print("Usage: uv run python scripts/explore_shades.py <hub-ip>")
        sys.exit(1)

    hub_ip = sys.argv[1]
    base = f"http://{hub_ip}/api"
    client = httpx.Client(timeout=30)

    # --- GET /api/shades (list all) ---
    print(f"\n{'='*60}")
    print(f"GET {base}/shades")
    print(f"{'='*60}")
    r = client.get(f"{base}/shades")
    data = r.json()
    print(json.dumps(data, indent=2))
    save("shades_list", data)

    shades = data.get("shadeData", [])
    shade_ids = data.get("shadeIds", [])

    print(f"\n  Found {len(shades)} shades (IDs: {shade_ids})")

    # Summary table
    print(f"\n  {'Name':<25} {'ID':<8} {'Type':<6} {'Battery':<10} {'Positions'}")
    print(f"  {'-'*25} {'-'*8} {'-'*6} {'-'*10} {'-'*30}")
    for s in shades:
        name = decode_name(s.get("name", ""))
        sid = s.get("id", "?")
        stype = s.get("type", "?")
        batt = s.get("batteryStrength", "?")
        batt_status = s.get("batteryStatus", "?")
        positions = s.get("positions", {})
        print(f"  {name:<25} {sid:<8} {stype:<6} {batt} (st={batt_status})  {positions}")

    # --- GET /api/shades/{id} for first shade (cached vs refresh) ---
    if shade_ids:
        first_id = shade_ids[0]

        # Cached request
        print(f"\n{'='*60}")
        print(f"GET {base}/shades/{first_id}  (cached)")
        print(f"{'='*60}")
        t0 = time.monotonic()
        r = client.get(f"{base}/shades/{first_id}")
        t1 = time.monotonic()
        data = r.json()
        print(json.dumps(data, indent=2))
        print(f"  Time: {t1 - t0:.2f}s")
        save(f"shade_{first_id}_cached", data)

        # Refresh request
        print(f"\n{'='*60}")
        print(f"GET {base}/shades/{first_id}?refresh=true  (RF poll)")
        print(f"{'='*60}")
        t0 = time.monotonic()
        r = client.get(f"{base}/shades/{first_id}", params={"refresh": "true"})
        t1 = time.monotonic()
        data = r.json()
        print(json.dumps(data, indent=2))
        print(f"  Time: {t1 - t0:.2f}s")
        save(f"shade_{first_id}_refresh", data)

    print("\nDone. Check scripts/responses/ for saved JSON.")


if __name__ == "__main__":
    main()
