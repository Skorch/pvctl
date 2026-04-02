# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`pvctl` is a Python CLI tool for managing a Hunter Douglas PowerView **Gen 1 hub** (controlling Gen 2 motorized blinds) over its local REST API. The hub exposes an unauthenticated HTTP API on port 80 at `http://<hub-ip>/api/`. Full spec at `specs/spec.md`.

## Build & Development Commands

- **Install (dev):** `uv sync`
- **Run CLI:** `uv run pvctl`
- **Run tests:** `uv run pytest`
- **Run single test:** `uv run pytest tests/test_foo.py::TestClass::test_name -v`
- **Lint:** `uv run ruff check .`
- **Format:** `uv run ruff format .`
- **Lint + test:** `uv run ruff check . && uv run pytest`
- **Install as tool:** `uv tool install .`

## Stack

- **Python 3.10+**, **Typer** (CLI), **Rich** (terminal output), **httpx** (HTTP client)
- **Pydantic 2** (API response models, config/schedule validation), **PyYAML** (config/schedule files)
- **uv + hatchling** (packaging), **ruff** (lint/format), **pytest + pytest-httpx** (testing)
- **difflib** (stdlib) for fuzzy name matching — no thefuzz dependency
- **Direct crontab manipulation** — no python-crontab dependency; write/remove lines with `# pvctl:` markers

## Architecture

```
src/pvctl/
├── cli.py              # Typer app, command groups, --quiet/-q flag via callback
├── commands/
│   ├── init.py         # pvctl init <ip> — discover hub, write config
│   ├── hub.py          # pvctl hub info — Rich panel with hub metadata
│   ├── status.py       # pvctl status — shade table with position bars + battery
│   ├── shade.py        # pvctl shade open|close|set|stop|jog <name>
│   ├── scene.py        # pvctl scene list|activate — scenes AND scene collections
│   ├── room.py         # pvctl room list — rooms with shade counts
│   └── schedule.py     # pvctl schedule show|validate|install|uninstall|run
├── api/
│   ├── client.py       # HubClient: sync httpx wrapper, all endpoint methods
│   └── models.py       # Pydantic models: Shade, Scene, SceneCollection, Room, etc.
├── config.py           # YAML config at ~/.config/pvctl/config.yaml
├── schedule_manager.py # Schedule YAML parsing, crontab read/write with # pvctl: tags
├── display.py          # Rich rendering helpers, quiet mode support
└── utils.py            # Name fuzzy matching (difflib), position math (0-65535 ↔ 0-100%)
```

API endpoint methods live in `api/client.py` (not split into separate endpoint files — the API is small enough for one class).

## Key Design Decisions

- **Hub is the radio, pvctl is the brain:** Hub handles RF to shades. pvctl handles scheduling, monitoring, UI.
- **Scene activation is a GET:** `GET /api/scenes?sceneid={id}` (confirmed, unusual but real). Scene collections: `GET /api/scenecollections?sceneCollectionId={id}`.
- **Two kinds of "scenes":** Hub has scenes (per-room) and scene collections (multi-room). Hub schedules use collections. `pvctl scene activate` searches both, matching by name.
- **Hub schedules are source of truth:** `pvctl schedule sync` fetches hub's `scheduledEventData`, translates to cron entries. `pvctl schedule install` sets up a sync cron (default every 5min). Cron entries tagged `# pvctl:`, sync entry tagged `# pvctl-sync`. Disabled hub schedules → commented `# DISABLED:` cron lines. `~/.config/pvctl/schedule.yaml` only configures sync interval.
- **Name matching order:** exact (case-insensitive) → substring → difflib fuzzy (cutoff 0.6) → disambiguation/exit 1.
- **Exit codes:** 0=success, 1=user error, 2=hub unreachable.
- **API is case-sensitive:** Endpoints must be lowercase (e.g. `scenecollections` not `sceneCollections`). Wrong case crashes the hub.
- **Positions may be missing:** Bulk shade list often returns empty `positions: {}`. Must RF-poll individual shades with `?refresh=true` for current data (slow, ~6s per shade, may timeout).

## Hub API Quick Reference

All endpoints at `http://<hub-ip>/api/`. Names are Base64-encoded UTF-8. Position range: 0–65535 (0=closed, 65535=open). `batteryStrength` 0–200, pct = `min(val, 200) // 2`. See spec for full details and example responses.

| Endpoint | Method | Notes |
|----------|--------|-------|
| `userdata` | GET | Hub info (serial, MAC, counts) |
| `fwversion` | GET | Firmware version |
| `shades` | GET | List all (positions often empty) |
| `shades/{id}` | GET | Single shade, also returns all others in `shadeData` |
| `shades/{id}?refresh=true` | GET | RF poll, slow, may return `timedOut: true` |
| `shades/{id}` | PUT | Set position or motion (jog/stop) |
| `scenes` | GET | List scenes |
| `scenes?sceneid={id}` | GET | Activate scene, returns `{scene: {shadeIds: [...]}}` |
| `scenecollections` | GET | List scene collections (multi-scenes) |
| `scenecollections?sceneCollectionId={id}` | GET | Activate collection, returns `{}` |
| `rooms` | GET | List rooms |
| `scheduledevents` | GET | Hub-side schedules (reference only) |
| `scheduledevents/{id}` | PUT | Enable/disable hub schedule |

## Config

- Config: `~/.config/pvctl/config.yaml` — hub IP + cached device data
- Schedule: `~/.config/pvctl/schedule.yaml` — local schedule definitions
