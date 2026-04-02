#!/usr/bin/env python3
"""Explore hub-side schedules: /api/scheduledevents.

Usage: uv run python scripts/explore_schedules.py <hub-ip>
"""

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
        print("Usage: uv run python scripts/explore_schedules.py <hub-ip>")
        sys.exit(1)

    hub_ip = sys.argv[1]
    base = f"http://{hub_ip}/api"
    client = httpx.Client(timeout=10)

    # --- GET /api/scheduledevents ---
    print(f"\n{'='*60}")
    print(f"GET {base}/scheduledevents")
    print(f"{'='*60}")
    r = client.get(f"{base}/scheduledevents")
    data = r.json()
    print(json.dumps(data, indent=2))
    save("scheduledevents", data)

    # Try to summarize whatever structure we find
    events = data.get("scheduledEventData", data.get("scheduleData", []))
    if isinstance(events, list):
        print(f"\n  Found {len(events)} scheduled events")
        for e in events:
            print(f"    {json.dumps(e)}")
    else:
        print(f"\n  Response keys: {list(data.keys())}")

    print("\nDone. Check scripts/responses/ for saved JSON.")


if __name__ == "__main__":
    main()
