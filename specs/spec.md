# PRD: pvctl — Hunter Douglas PowerView Hub CLI Manager

**Date:** 2026-04-01
**Status:** Draft
**File Location:** `/specs/pvctl/prd.md`

---

## Executive Summary

`pvctl` is a Python CLI tool for managing a Hunter Douglas PowerView Gen 1/Gen 2 hub over its local REST API. It provides shade control, status monitoring, scene management, and local schedule execution — replacing the hub's unreliable built-in scheduler with cron-driven API calls. Built with Typer + Rich for polished terminal output, packaged via uv for zero-friction installation.

---

## Problem Statement

### Current State

The user has a PowerView Gen 1 hub controlling Gen 2 motorized blinds. The hub exposes an unauthenticated REST API on port 80 at `http://<hub-ip>/api/`. The hub's built-in schedule execution is unreliable — schedules are configured but not firing. The PowerView mobile app provides control but no visibility into what's happening or why schedules fail. Gen 2 hubs are discontinued and irreplaceable, making the hub a critical single point of failure that needs to be augmented, not replaced.

### User Pain Points

#### Unreliable Schedule Execution
- **Who:** Homeowner with automated blinds
- **Situation:** Hub has schedules configured but they don't execute
- **Pain:** Blinds don't open/close on schedule; manual intervention required daily
- **Impact:** Defeats the purpose of motorized blinds

#### No Visibility
- **Who:** Same
- **Situation:** No way to see shade positions, battery levels, or schedule status at a glance from a terminal
- **Pain:** Must use the mobile app or guess
- **Impact:** Can't debug issues, can't script automation

#### No Scriptable Interface
- **Who:** Same (technical user comfortable with CLI)
- **Situation:** Wants to integrate shade control into existing home automation scripts, cron jobs, SSH sessions
- **Pain:** Only interface is the mobile app or raw curl commands
- **Impact:** Can't compose shade control with other tools

---

## Solution Overview

### Core Concept

A Python CLI tool that wraps the PowerView hub's REST API with a clean command structure and Rich terminal output. The tool talks to the hub over HTTP on the local network — no RF, no cloud, no proprietary protocols. For scheduling, the tool owns the schedule definition (stored locally as YAML) and executes it via system cron, bypassing the hub's broken scheduler entirely.

### Key Principles

1. **Hub is the radio, pvctl is the brain:** The hub handles RF communication with shades. pvctl handles scheduling, monitoring, and user interface. Clean separation.
2. **Scriptable first, pretty second:** Every command outputs structured data suitable for piping. Rich formatting is the default for interactive use but `--json` flag gives machine-readable output on any command.
3. **Local only:** No cloud dependencies, no accounts, no auth tokens. The hub's API is unauthenticated on the LAN.
4. **Minimal config:** Hub IP is the only required configuration. Everything else is discoverable from the hub.

### What This Is / What This Isn't

**This IS:**
- A CLI wrapper around the PowerView hub's existing REST API
- A local schedule executor that replaces the hub's unreliable scheduler
- A status dashboard for shade positions and battery levels
- A scriptable tool for automation pipelines

**This ISN'T:**
- An RF-level hub replacement (we still need the physical hub)
- A mobile app replacement (though it covers the same functionality)
- A Home Assistant integration (HA already has one; this is for direct CLI use)
- A multi-hub manager (single hub target, though the architecture shouldn't prevent future multi-hub support)

---

## User Stories

### Story 1: See All My Shades At a Glance

**As a** homeowner
**I want to** run a single command and see every shade's name, position, and battery level
**So that** I know the state of my house and can spot low batteries before they die

#### Acceptance Criteria
- GIVEN the hub is reachable on the network
- WHEN I run `pvctl status`
- THEN I see a Rich table with columns: Name, Room, Position (as % with visual bar), Battery (with color-coded level), and Shade Type

### Story 2: Control a Shade

**As a** homeowner
**I want to** open, close, or set a specific shade position from my terminal
**So that** I can control blinds without the mobile app

#### Acceptance Criteria
- GIVEN I know the shade name or ID
- WHEN I run `pvctl shade open "Living Room"` or `pvctl shade set "Living Room" 50`
- THEN the shade moves to the specified position and the command confirms the action

### Story 3: Run Scenes

**As a** homeowner
**I want to** activate PowerView scenes I've already configured
**So that** I can trigger multi-shade presets from the terminal or scripts

#### Acceptance Criteria
- GIVEN scenes exist on the hub
- WHEN I run `pvctl scene list` to see available scenes, then `pvctl scene activate "Good Morning"`
- THEN the scene executes and all associated shades move

### Story 4: Replace the Broken Scheduler

**As a** homeowner
**I want to** define a local schedule and have pvctl execute it reliably
**So that** my blinds open and close on time every day without depending on the hub's buggy scheduler

#### Acceptance Criteria
- GIVEN I have a schedule file defining times and actions (shade positions or scene activations)
- WHEN I run `pvctl schedule install`
- THEN pvctl writes system crontab entries that call `pvctl` commands at the specified times
- AND I can verify the installed schedule with `pvctl schedule show`
- AND I can remove it with `pvctl schedule uninstall`

### Story 5: Quick Discovery

**As a** homeowner setting up pvctl for the first time
**I want to** point it at my hub and have it discover everything
**So that** I don't have to manually configure shade IDs, room names, or scene names

#### Acceptance Criteria
- GIVEN I know my hub's IP address
- WHEN I run `pvctl init 192.168.7.38`
- THEN pvctl connects, discovers all shades/rooms/scenes, and writes a config file
- AND subsequent commands work without specifying the IP

### Story 6: Hub Health Check

**As a** homeowner
**I want to** see hub firmware version, serial number, and connected device counts
**So that** I can verify the hub is healthy and know what I'm working with

#### Acceptance Criteria
- GIVEN pvctl is configured
- WHEN I run `pvctl hub info`
- THEN I see a Rich panel with hub metadata including firmware version, serial, MAC, IP, and counts of shades/rooms/scenes

---

## Scope

### In Scope (V1)

- [x] Hub discovery and config initialization (`pvctl init`)
- [x] Hub info display (`pvctl hub info`)
- [x] Shade listing with status (`pvctl status`)
- [x] Shade control: open, close, set position, stop, jog (`pvctl shade <action>`)
- [x] Scene listing and activation (`pvctl scene list`, `pvctl scene activate`)
- [x] Room listing (`pvctl room list`)
- [x] Schedule definition file format (YAML)
- [x] Schedule installation to system cron (`pvctl schedule install/uninstall/show`)
- [x] `--json` flag on all commands for machine-readable output
- [x] Battery level monitoring with color-coded warnings
- [x] Config file at `~/.config/pvctl/config.yaml`
- [x] Schedule file at `~/.config/pvctl/schedule.yaml`
- [x] Shade name fuzzy matching (don't require exact names)

### Out of Scope (V1)

- Shade pairing/enrollment — *Reason: requires RF-level access, not available via API*
- Schedule editing via TUI — *Reason: edit the YAML file directly; keep V1 simple*
- Multi-hub support — *Reason: user has one hub; architect for it but don't implement*
- Daemon/service mode — *Reason: cron is simpler and more reliable for V1*
- Webhook/push monitoring — *Reason: polling is fine for CLI; the hub's webhook interface is fragile*
- Textual TUI dashboard — *Reason: Rich Live `pvctl watch` would be a nice V2 feature*

### Future Considerations (V2+)

- `pvctl watch` — Rich Live auto-refreshing dashboard
- Trogon integration for interactive TUI form-based command builder
- Sunrise/sunset schedule support (integrate with astral library for solar time)
- Shade group management (create/edit groups via API)
- Battery trend tracking (log levels over time, predict replacement)
- MQTT bridge mode for Home Assistant integration
- Badger 2040 W display client that polls pvctl's status endpoint

---

## Milestones

### Milestone 1: Project Scaffolding & Hub Connection

**User Outcome:** User can install pvctl via uv and connect to their hub

**Delivers:**
- uv-compatible Python package with Typer CLI skeleton
- Hub connection, discovery, and config persistence
- `pvctl init <ip>` and `pvctl hub info`

**Dependencies:** None

**Approximate Scope:**
- Project structure, pyproject.toml, entry points
- HTTP client wrapper for hub API
- Config file management
- Hub info and discovery endpoints

### Milestone 2: Shade Status & Control

**User Outcome:** User can see all shade positions/battery and control individual shades

**Delivers:**
- `pvctl status` — Rich table with all shades
- `pvctl shade open|close|set|stop|jog` — Individual shade control
- `--json` output mode
- Shade name fuzzy matching

**Dependencies:** Milestone 1

**Approximate Scope:**
- Shade API client (list, get, update position, motion commands)
- Rich table rendering with position bars and battery indicators
- Name resolution (fuzzy match shade names to IDs)
- JSON output formatter

### Milestone 3: Scenes & Rooms

**User Outcome:** User can list rooms, list scenes, and activate scenes

**Delivers:**
- `pvctl scene list` and `pvctl scene activate <name>`
- `pvctl room list` with shade counts
- Scene name fuzzy matching

**Dependencies:** Milestone 1

**Approximate Scope:**
- Scene API client (list, activate)
- Room API client (list with shade associations)
- Rich table rendering for scenes and rooms

### Milestone 4: Local Schedule Management

**User Outcome:** User can define a schedule in YAML and install it to cron, replacing the hub's broken scheduler

**Delivers:**
- Schedule YAML file format with validation
- `pvctl schedule show` — Display current schedule as Rich table
- `pvctl schedule install` — Write crontab entries
- `pvctl schedule uninstall` — Remove crontab entries
- `pvctl schedule validate` — Check schedule file for errors
- `pvctl schedule run <entry>` — Manually trigger a schedule entry (for testing)

**Dependencies:** Milestones 2 and 3 (schedule entries reference shades and scenes)

**Approximate Scope:**
- Schedule file schema and parser
- Crontab read/write (python-crontab or direct manipulation)
- Schedule validation (shade names exist, times are valid, no conflicts)
- Schedule display with next-run calculation

---

## Technical Specification

### Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.10+ | User preference, ecosystem |
| CLI Framework | Typer 0.12+ | Type-hint routing, native Rich help |
| Terminal Output | Rich 13+ | Tables, panels, progress, color |
| HTTP Client | httpx | Modern, clean API, good error handling |
| Config Format | YAML (PyYAML) | Human-editable, comments supported |
| Packaging | uv + hatchling | Zero-friction install via uvx/uv tool |
| Schedule Backend | python-crontab | Clean crontab manipulation |
| Name Matching | thefuzz | Fuzzy string matching for shade/scene names |
| Data Validation | Pydantic 2+ | API response parsing, config/schedule validation |

### Project Structure

```
pvctl/
├── pyproject.toml
├── README.md
├── src/
│   └── pvctl/
│       ├── __init__.py
│       ├── cli.py                 # Typer app, command groups, global flags
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── init.py            # pvctl init <ip>
│       │   ├── hub.py             # pvctl hub info
│       │   ├── shade.py           # pvctl shade open|close|set|stop|jog
│       │   ├── scene.py           # pvctl scene list|activate
│       │   ├── room.py            # pvctl room list
│       │   ├── status.py          # pvctl status
│       │   └── schedule.py        # pvctl schedule show|install|uninstall|validate|run
│       ├── api/
│       │   ├── __init__.py
│       │   ├── client.py          # HTTP client wrapper (httpx, timeout, retry)
│       │   ├── shades.py          # GET/PUT /api/shades
│       │   ├── scenes.py          # GET /api/scenes
│       │   ├── rooms.py           # GET /api/rooms
│       │   └── models.py          # Pydantic models for API responses
│       ├── config.py              # Config file read/write (~/.config/pvctl/)
│       ├── schedule_manager.py    # Schedule YAML parsing, cron read/write
│       ├── display.py             # Rich rendering helpers (shared table styles, bars, panels)
│       └── utils.py               # Base64 decode, name fuzzy matching, position math
└── tests/
    ├── conftest.py                # Shared fixtures, mock hub responses
    ├── test_api_client.py
    ├── test_commands.py
    ├── test_config.py
    ├── test_schedule.py
    ├── test_display.py
    └── test_utils.py
```

### pyproject.toml

```toml
[project]
name = "pvctl"
version = "0.1.0"
description = "CLI manager for Hunter Douglas PowerView blinds"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
dependencies = [
    "typer>=0.12.0",
    "rich>=13.0.0",
    "httpx>=0.27.0",
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "python-crontab>=3.0",
    "thefuzz>=0.22.0",
]

[project.scripts]
pvctl = "pvctl.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/pvctl"]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-httpx>=0.30.0",
    "ruff>=0.4.0",
]
```

### Config File (~/.config/pvctl/config.yaml)

```yaml
hub:
  ip: "192.168.7.38"
  name: "Living Room Hub"      # from discovery
  serial: "..."                 # from discovery
  firmware: "..."               # from discovery

# Cached device data (updated on init and pvctl refresh)
cache:
  shades: {}    # id -> {name, room, type}
  scenes: {}    # id -> {name, room}
  rooms: {}     # id -> {name}

# Display preferences
display:
  position_bar_width: 20       # character width of position bars in tables
  battery_warn: 20             # yellow below this %
  battery_critical: 10         # red below this %
```

### Schedule File (~/.config/pvctl/schedule.yaml)

```yaml
# pvctl schedule file
# Install to cron with: pvctl schedule install
# Validate with: pvctl schedule validate

schedules:
  - name: "Morning Open"
    time: "07:00"
    days: "weekdays"       # or [mon, tue, wed, thu, fri] or "daily" or "weekends"
    action:
      scene: "Good Morning"

  - name: "Weekend Open"
    time: "08:30"
    days: "weekends"
    action:
      scene: "Good Morning"

  - name: "Office Partial"
    time: "08:00"
    days: "weekdays"
    action:
      shade: "Office"
      position: 65

  - name: "Evening Close"
    time: "21:00"
    days: "daily"
    action:
      scene: "Good Night"

  - name: "Bedroom Dim"
    time: "21:30"
    days: "daily"
    action:
      shade: "Bedroom"
      position: 20

  - name: "Midday Kitchen"
    time: "12:00"
    days: "daily"
    enabled: false
    action:
      shade: "Kitchen"
      position: 0
```

### PowerView Hub API Reference

All endpoints are `http://<hub-ip>/api/...` — unauthenticated HTTP on port 80.

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/api/userdata` | GET | Hub info (serial, MAC, counts) | |
| `/api/fwversion` | GET | Firmware version | |
| `/api/shades` | GET | List all shades | Names are Base64-encoded |
| `/api/shades/{id}` | GET | Get single shade | Add `?refresh=true` for fresh RF poll |
| `/api/shades/{id}` | PUT | Set shade position or motion | Body: `{"shade": {"positions": {...}}}` or `{"shade": {"motion": "jog"}}` |
| `/api/scenes` | GET | List all scenes | Names are Base64-encoded |
| `/api/scenes?sceneid={id}` | GET | Activate a scene | Activation is a GET with query param |
| `/api/rooms` | GET | List all rooms | Names are Base64-encoded |
| `/api/scheduledevents` | GET | List hub-side schedules | For reference only |

**Position encoding:**
- `position1` range: 0 (closed) to 65535 (fully open)
- `posKind1`: 1 = primary rail, 2 = secondary rail (top-down/bottom-up), 3 = vane/tilt
- Percentage conversion: `pct = round(pos / 65535 * 100)` and `pos = round(pct / 100 * 65535)`

**Name decoding:** All `name` fields are Base64-encoded UTF-8. Decode: `base64.b64decode(name).decode('utf-8')`

**Battery mapping:** `batteryStrength` is 0–200. Rough percentage: `min(batteryStrength, 200) / 2`

### Command Reference & Rich Output Design

#### `pvctl init <hub-ip>`

Connects to hub, discovers all devices, writes config file.

```
 ✓ Connected to hub at 192.168.7.38
 ✓ Found 4 shades, 3 rooms, 5 scenes
 ✓ Config written to ~/.config/pvctl/config.yaml

 Run 'pvctl status' to see your shades.
```

#### `pvctl status`

Primary dashboard view. Rich table with visual position bars and color-coded battery.

```
                         PowerView Shade Status
┌──────────────┬─────────────┬──────────────────────────┬─────────┐
│ Shade        │ Room        │ Position                 │ Battery │
├──────────────┼─────────────┼──────────────────────────┼─────────┤
│ Duette       │ Living Room │ ████████████████████ 100% │ ██░░ 87%│
│ Roller       │ Bedroom     │ ░░░░░░░░░░░░░░░░░░░░   0% │ █░░░ 42%│
│ Silhouette   │ Office      │ █████████████░░░░░░░  65% │ ██░░ 91%│
│ Roller       │ Kitchen     │ ████████████████████ 100% │ ▪░░░ 15%│
└──────────────┴─────────────┴──────────────────────────┴─────────┘
  ● 4 shades online   ⚠ 1 low battery (Kitchen)
  Last refresh: 10:34 AM
```

Design details:
- Position bars use block characters (█ for filled, ░ for empty)
- Battery colors: green ≥50%, yellow 20–49%, red <20%
- Footer summary calls out low battery shades by name
- `--refresh` flag forces RF poll (slower but current)
- `--json` outputs array of shade objects

#### `pvctl shade open|close|set|stop|jog <name>`

```
$ pvctl shade set "Living Room" 50
  Living Room → 50%  ██████████░░░░░░░░░░

$ pvctl shade jog Kitchen
  ⟳ Jogging Kitchen (identify)

$ pvctl shade open Bedroom
  Bedroom → 100%  ████████████████████
```

Design details:
- Name matching is fuzzy: "living" matches "Living Room Duette"
- If ambiguous, show disambiguation table and exit with non-zero code
- `open` = 100%, `close` = 0%, `set` takes 0–100
- Mini position bar on confirmation line

#### `pvctl scene list`

```
                      PowerView Scenes
┌────────┬────────────────┬─────────────────────────┐
│ ID     │ Name           │ Shades                  │
├────────┼────────────────┼─────────────────────────┤
│ 54321  │ Good Morning   │ 4 shades                │
│ 54322  │ Good Night     │ 4 shades                │
│ 54323  │ Movie Time     │ 2 shades                │
│ 54324  │ Work Mode      │ 1 shade                 │
│ 54325  │ All Open       │ 4 shades                │
└────────┴────────────────┴─────────────────────────┘
```

#### `pvctl scene activate <name>`

```
$ pvctl scene activate "Good Morning"
  ▶ Activating scene: Good Morning (4 shades)
  ✓ Done
```

#### `pvctl room list`

```
                        PowerView Rooms
┌────────┬─────────────┬────────┬─────────────────────┐
│ ID     │ Room        │ Shades │ Shade Names          │
├────────┼─────────────┼────────┼─────────────────────┤
│ 101    │ Living Room │ 1      │ Duette               │
│ 102    │ Bedroom     │ 1      │ Roller               │
│ 103    │ Office      │ 1      │ Silhouette           │
│ 104    │ Kitchen     │ 1      │ Roller               │
└────────┴─────────────┴────────┴─────────────────────┘
```

#### `pvctl hub info`

```
╭─────────────── PowerView Hub ───────────────╮
│                                              │
│  Name:       Living Room Hub                 │
│  IP:         192.168.7.38                    │
│  Serial:     XXXXXXXXXXXX                    │
│  MAC:        XX:XX:XX:XX:XX:XX               │
│  Firmware:   2.0.1.0                         │
│                                              │
│  Shades:     4                               │
│  Rooms:      3                               │
│  Scenes:     5                               │
│  Schedules:  6 (hub-side)                    │
│                                              │
╰──────────────────────────────────────────────╯
```

#### `pvctl schedule show`

```
                     pvctl Schedule
┌─────┬─────────────────┬───────┬────────────┬──────────────────┐
│     │ Name            │ Time  │ Days       │ Action           │
├─────┼─────────────────┼───────┼────────────┼──────────────────┤
│ ●   │ Morning Open    │ 07:00 │ Mon–Fri    │ Scene: Good Morn │
│ ●   │ Weekend Open    │ 08:30 │ Sat–Sun    │ Scene: Good Morn │
│ ●   │ Office Partial  │ 08:00 │ Mon–Fri    │ Office → 65%     │
│ ●   │ Evening Close   │ 21:00 │ Daily      │ Scene: Good Night│
│ ●   │ Bedroom Dim     │ 21:30 │ Daily      │ Bedroom → 20%    │
│ ○   │ Midday Kitchen  │ 12:00 │ Daily      │ Kitchen → 0%     │
└─────┴─────────────────┴───────┴────────────┴──────────────────┘
  ● = active   ○ = disabled
  Next: Morning Open at 07:00 tomorrow
  Cron: 5 entries installed ✓
```

#### `pvctl schedule install`

```
$ pvctl schedule install

  Installing 5 schedule entries to crontab...
  ✓ Morning Open     → 0 7 * * 1,2,3,4,5
  ✓ Weekend Open     → 30 8 * * 6,0
  ✓ Office Partial   → 0 8 * * 1,2,3,4,5
  ✓ Evening Close    → 0 21 * * *
  ✓ Bedroom Dim      → 30 21 * * *
  ⊘ Midday Kitchen   → skipped (disabled)

  5 cron entries installed. Verify with 'crontab -l'.
```

Each cron entry calls pvctl with absolute path and quiet mode:
```cron
# pvctl: Morning Open
0 7 * * 1,2,3,4,5 /absolute/path/to/pvctl scene activate "Good Morning" --quiet 2>&1 | logger -t pvctl
```

The `--quiet` flag suppresses Rich output for non-interactive use.
The `| logger -t pvctl` pipes output to syslog for debugging.

#### `pvctl schedule uninstall`

```
$ pvctl schedule uninstall

  Removing pvctl entries from crontab...
  ✓ Removed 5 entries
```

Only removes entries with `# pvctl:` comment tags. Leaves other cron entries alone.

#### `pvctl schedule validate`

```
$ pvctl schedule validate

  Validating ~/.config/pvctl/schedule.yaml...
  ✓ 6 entries parsed
  ✓ All shade names resolve
  ✓ All scene names resolve
  ✓ No time conflicts
  ✓ Schedule is valid
```

Or on error:
```
  ✗ Shade "Kitchn" not found. Did you mean "Kitchen"?
  ✗ Entry "Duplicate" conflicts with "Morning Open" (same time and days)
```

#### `pvctl schedule run <name>`

Manually triggers a specific schedule entry for testing:
```
$ pvctl schedule run "Morning Open"
  ▶ Running: Morning Open
  ▶ Activating scene: Good Morning
  ✓ Done
```

### Global Flags

| Flag | Effect |
|------|--------|
| `--json` | Output raw JSON instead of Rich tables/panels |
| `--quiet` / `-q` | Minimal output, no Rich formatting (for cron/scripts) |
| `--hub <ip>` | Override configured hub IP for this command |
| `--no-color` | Disable Rich color output (also respects `NO_COLOR` env var) |
| `--refresh` | Force RF poll on shade queries (slower, more accurate) |
| `--verbose` / `-v` | Show HTTP request/response details for debugging |
| `--config <path>` | Override config file path |

### API Client Design

Implemented in `api/client.py` as a synchronous httpx wrapper:

- **Base URL:** `http://{hub_ip}/api`
- **Default timeout:** 10 seconds; 30 seconds for `?refresh=true` endpoints
- **Retry:** 1 automatic retry on `httpx.ConnectError` or `httpx.TimeoutException`
- **Error handling:** Catch connection errors → user-friendly message: "Hub not reachable at {ip}. Check network and hub power."
- **Response parsing:** All responses parsed through Pydantic models; Base64 name fields decoded automatically in the model validators
- **Verbose mode:** When `--verbose`, log full request URL and response status to stderr via `rich.console.Console(stderr=True)`

### Name Fuzzy Matching (utils.py)

Resolution order for shade/scene names:
1. Exact match (case-insensitive)
2. Substring match ("living" → "Living Room")
3. Fuzzy match via thefuzz with score threshold ≥ 80
4. If multiple matches at same confidence: show Rich table of candidates, exit code 1
5. If no match: show "did you mean?" with top 3 closest, exit code 1

### Display Helpers (display.py)

Shared Rich rendering functions used across commands:
- `render_position_bar(pct: int, width: int = 20) -> str` — block character bar
- `render_battery(pct: int) -> str` — color-coded battery with icon
- `shade_table(shades: list[Shade]) -> Table` — standard shade status table
- `scene_table(scenes: list[Scene]) -> Table` — standard scene list table
- `schedule_table(entries: list[ScheduleEntry]) -> Table` — schedule display with next-run
- `hub_panel(info: HubInfo) -> Panel` — hub info detail panel
- `success(msg: str)`, `error(msg: str)`, `warn(msg: str)` — styled status messages with ✓/✗/⚠

---

## Risks & Mitigations

### Risk 1: Hub Unreachable

| Aspect | Value |
|--------|-------|
| Probability | Medium |
| Impact | High — all commands fail |
| Description | Hub loses connectivity, reboots, or gets new DHCP IP |
| Mitigation | Clear error messages with IP shown; `--hub` override; recommend static IP reservation |

### Risk 2: Stale Shade Positions

| Aspect | Value |
|--------|-------|
| Probability | High |
| Impact | Low — cosmetic only, displayed positions may be stale |
| Description | Hub caches positions; Pebble remote usage isn't reflected |
| Mitigation | `--refresh` flag for RF poll; document this as a known limitation of the Gen 2 protocol |

### Risk 3: Cron Environment PATH

| Aspect | Value |
|--------|-------|
| Probability | Medium |
| Impact | Medium — schedules silently fail |
| Description | Cron runs with minimal PATH; `pvctl` binary may not be found |
| Mitigation | `schedule install` resolves absolute path to pvctl binary via `shutil.which()` and writes full path in cron entries; syslog output for debugging failed runs |

### Risk 4: Hub API Undocumented Changes

| Aspect | Value |
|--------|-------|
| Probability | Low |
| Impact | Medium — commands return unexpected data |
| Description | Hub firmware updates could change API behavior |
| Mitigation | Pydantic models with `model_config = ConfigDict(extra="ignore")` to tolerate extra fields; version check on init |

---

## Success Criteria

### Functional Success

- [ ] `pvctl status` returns all shade data in under 3 seconds (without `--refresh`)
- [ ] `pvctl shade set <name> <pct>` moves the correct shade within 2 seconds
- [ ] `pvctl schedule install` creates valid crontab entries that survive reboot
- [ ] Cron-triggered commands execute silently and log to syslog
- [ ] Fuzzy name matching resolves unambiguous names on first try
- [ ] `--json` output on every command is valid, parseable JSON
- [ ] Tool installs cleanly via `uv tool install .` from project root
- [ ] `uv run pvctl status` works during development without manual install

### Measurable Outcomes

| Metric | Current | Target | How Measured |
|--------|---------|--------|--------------|
| Schedule reliability | ~50% (hub) | 99%+ (cron) | Blinds move on time |
| Time to check status | 30s (app) | 3s (CLI) | Wall clock |
| Time to control shade | 15s (app) | 5s (CLI) | Wall clock |

---

## Appendix

### Shade Type Reference

| Type ID | Description |
|---------|-------------|
| 1 | Roller |
| 4 | Roman |
| 5 | Bottom Up |
| 6 | Duette |
| 7 | Top Down Bottom Up |
| 8 | Duette Top Down Bottom Up |
| 9 | Duette DuoLite Top Down Bottom Up |
| 10 | Silhouette / Pirouette |
| 23 | Silhouette Duolite |
| 42 | M25T Roller Blind |
| 43 | Facette |
| 44 | Twist |
| 47 | Pleated Top Down Bottom Up |
| 49 | AC Roller |
| 51 | Venetian |
| 54 | Vertical Slats Left |
| 55 | Vertical Slats Right |
| 62 | Venetian |
| 65 | Vane Full Tilt 180° |
| 66 | Vane Partial Tilt 90° |
| 69 | Curtain Left |
| 70 | Curtain Right |
| 71 | Curtain Split |

### Shade Capability Matrix

| Capability | posKind1 | posKind2 | Tilt |
|------------|----------|----------|------|
| 0 | Primary | — | — |
| 1 | Primary | — | Tilt 90° |
| 2 | Primary | — | Tilt 180° |
| 3 | Primary | Secondary | — |
| 4 | Primary | Secondary | — |
| 5 | Primary | Secondary | — |
| 6 | Primary | — | Tilt on close 90° |
| 7 | Primary | — | Tilt on close 180° |
| 8 | Primary | Secondary | Tilt |
| 9 | Primary | Secondary | Tilt |
| 10 | Primary | Tilt-only | — |
| 11 | Primary | Tilt-only | — |

### Example API Responses

**GET /api/shades**
```json
{
  "shadeData": [
    {
      "id": 29889,
      "name": "TGl2aW5nIFJvb20=",
      "roomId": 46688,
      "groupId": 18480,
      "type": 6,
      "batteryStrength": 159,
      "batteryStatus": 3,
      "positions": {
        "posKind1": 1,
        "position1": 65535
      },
      "firmware": {
        "revision": 1,
        "subRevision": 8,
        "build": 1944
      }
    }
  ],
  "shadeIds": [29889, 56112, 11903, 43667]
}
```

**GET /api/scenes**
```json
{
  "sceneData": [
    {
      "id": 54321,
      "name": "R29vZCBNb3JuaW5n",
      "roomId": 46688,
      "order": 0,
      "colorId": 7,
      "iconId": 0
    }
  ],
  "sceneIds": [54321, 54322, 54323]
}
```

**GET /api/userdata**
```json
{
  "userData": {
    "serialNumber": "XXXXXXXXXXXX",
    "rfID": "0x1234",
    "macAddress": "XX:XX:XX:XX:XX:XX",
    "ip": "192.168.7.38",
    "localTimeDataSet": true,
    "enableScheduledEvents": true,
    "editingEnabled": true,
    "setupCompleted": true,
    "hubName": "TGl2aW5nIFJvb20gSHVi"
  }
}
```

**GET /api/fwversion**
```json
{
  "firmware": {
    "mainProcessor": {"name": "...", "revision": 2, "subRevision": 0, "build": 1},
    "radio": {"name": "...", "revision": 2, "subRevision": 0, "build": 0}
  }
}
```