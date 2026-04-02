"""Config file management for pvctl.

Config lives at ~/.config/pvctl/config.yaml.
"""

from __future__ import annotations

from pathlib import Path

import yaml

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "pvctl"
CONFIG_FILE = "config.yaml"
SCHEDULE_FILE = "schedule.yaml"


def get_config_dir(override: Path | None = None) -> Path:
    return override or DEFAULT_CONFIG_DIR


def get_config_path(override: Path | None = None) -> Path:
    return get_config_dir(override) / CONFIG_FILE


def get_schedule_path(override: Path | None = None) -> Path:
    return get_config_dir(override) / SCHEDULE_FILE


def load_config(config_path: Path | None = None) -> dict:
    """Load config from YAML file. Returns empty dict if file doesn't exist."""
    path = get_config_path(config_path)
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def save_config(config: dict, config_path: Path | None = None) -> Path:
    """Write config to YAML file. Creates parent directories as needed."""
    path = get_config_path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))
    return path


def get_hub_ip(config: dict | None = None, override: str | None = None) -> str:
    """Resolve hub IP from override flag or config file.

    Returns the IP string or exits with an error.
    """
    if override:
        return override
    if config is None:
        config = load_config()
    ip = config.get("hub", {}).get("ip")
    if not ip:
        import sys
        print("No hub configured. Run 'pvctl init <hub-ip>' first.", file=sys.stderr)
        raise SystemExit(2)
    return ip
