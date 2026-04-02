# pvctl

CLI manager for Hunter Douglas PowerView blinds. Controls shades, scenes, and schedules via the hub's local REST API.

## What it does

- **See all shades at a glance** — positions, battery levels, rooms
- **Control shades** — open, close, set position, jog, stop (with fuzzy name matching)
- **Activate scenes** — both per-room scenes and multi-room scene collections
- **Replace the broken scheduler** — syncs hub schedule definitions to system cron for reliable execution
- **Machine-readable output** — `--json` flag on every command

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A Hunter Douglas PowerView Gen 1 hub on your local network

## Install

```bash
# Clone and install
git clone https://github.com/Skorch/pvctl.git
cd pvctl
uv sync

# Or install as a global tool
uv tool install .
```

## Quick start

```bash
# Point pvctl at your hub
pvctl init 192.168.7.38

# See your shades
pvctl status

# Control a shade (fuzzy name matching)
pvctl shade open "Master"
pvctl shade set "Lila" 50
pvctl shade close "Twins"

# List and activate scenes
pvctl scene list
pvctl scene activate "Morning Up All"

# Set up reliable scheduling (syncs hub schedules to cron every 5min)
pvctl schedule install
```

## Commands

```
pvctl init <hub-ip>           Connect to hub, discover devices, write config
pvctl status                  Show all shade positions and battery levels
pvctl hub info                Hub firmware, serial, device counts
pvctl shade open <name>       Fully open a shade
pvctl shade close <name>      Fully close a shade
pvctl shade set <name> <0-100> Set shade to specific position
pvctl shade jog <name>        Brief wiggle to identify a shade
pvctl shade stop <name>       Stop shade motion
pvctl scene list              List scenes and scene collections
pvctl scene activate <name>   Activate a scene or collection
pvctl room list               List rooms with shade counts
pvctl schedule install        Sync hub schedules to cron + set up auto-sync
pvctl schedule show           Show installed cron entries
pvctl schedule sync           Manually re-sync from hub
pvctl schedule uninstall      Remove all pvctl cron entries
```

## Global flags

| Flag | Effect |
|------|--------|
| `--json` | Machine-readable JSON output |
| `--quiet` / `-q` | Minimal output (for cron/scripts) |
| `--hub <ip>` | Override configured hub IP |
| `--refresh` | Force RF poll on shade queries (slower, more accurate) |

## How scheduling works

The PowerView hub has schedule definitions but its built-in executor is unreliable. pvctl reads those definitions and installs them as system cron entries that call `pvctl scene activate` at the right times.

```bash
pvctl schedule install    # Fetches hub schedules, writes cron entries,
                          # adds a sync cron that re-fetches every 5min
```

The sync interval is configurable in `~/.config/pvctl/schedule.yaml`:

```yaml
sync:
  interval: 5  # minutes
```

## Config files

| File | Purpose |
|------|---------|
| `~/.config/pvctl/config.yaml` | Hub IP and cached device data |
| `~/.config/pvctl/schedule.yaml` | Schedule sync configuration |

## Development

```bash
uv sync                          # Install dependencies
uv run pvctl --help               # Run CLI
uv run pytest                     # Run tests
uv run ruff check .               # Lint
./pvctl.sh status                 # Convenience wrapper
```

## Hub API

pvctl talks to the PowerView hub's unauthenticated REST API on port 80. No cloud, no accounts, no RF — just HTTP on your local network. See `specs/spec.md` for full API documentation.

## License

MIT
