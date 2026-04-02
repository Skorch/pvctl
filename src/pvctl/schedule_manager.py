"""Schedule management: hub-synced cron with local config.

The hub's scheduled events are the source of truth. pvctl syncs them to cron
entries that call pvctl to execute the actions (since the hub's built-in
scheduler is unreliable).

Config lives at ~/.config/pvctl/schedule.yaml and controls sync behavior:
    sync:
      interval: 5  # minutes between sync polls

Crontab entries are tagged with '# pvctl:' for safe install/uninstall.
The sync cron entry is tagged with '# pvctl-sync' separately.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from pvctl.api.models import ScheduledEvent
from pvctl.config import get_schedule_path

CRON_TAG = "# pvctl:"
SYNC_CRON_TAG = "# pvctl-sync"
DEFAULT_SYNC_INTERVAL = 5  # minutes


@dataclass
class ScheduleEntry:
    """A hub schedule translated to a cron-ready entry."""

    name: str
    time: str  # "HH:MM"
    days: list[int]  # cron day-of-week numbers (0=Sun, 1=Mon, ...)
    collection_name: str
    collection_id: int
    enabled: bool = True

    @property
    def hour(self) -> int:
        return int(self.time.split(":")[0])

    @property
    def minute(self) -> int:
        return int(self.time.split(":")[1])

    @property
    def cron_days(self) -> str:
        return ",".join(str(d) for d in sorted(self.days))

    @property
    def cron_expression(self) -> str:
        return f"{self.minute} {self.hour} * * {self.cron_days}"

    @property
    def days_display(self) -> str:
        if sorted(self.days) == [0, 1, 2, 3, 4, 5, 6]:
            return "Daily"
        if sorted(self.days) == [1, 2, 3, 4, 5]:
            return "Mon\u2013Fri"
        if sorted(self.days) == [0, 6]:
            return "Sat\u2013Sun"
        day_names = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}
        return " ".join(day_names[d] for d in sorted(self.days))


def hub_events_to_entries(
    events: list[ScheduledEvent],
    collection_map: dict[int, str],
) -> list[ScheduleEntry]:
    """Convert hub scheduled events to ScheduleEntry objects."""
    entries = []
    for event in events:
        days = []
        for attr, dow in [
            ("daySunday", 0), ("dayMonday", 1), ("dayTuesday", 2),
            ("dayWednesday", 3), ("dayThursday", 4), ("dayFriday", 5),
            ("daySaturday", 6),
        ]:
            if getattr(event, attr):
                days.append(dow)

        coll_name = collection_map.get(
            event.sceneCollectionId, f"collection-{event.sceneCollectionId}"
        )

        entries.append(ScheduleEntry(
            name=coll_name,
            time=f"{event.hour:02d}:{event.minute:02d}",
            days=days,
            collection_name=coll_name,
            collection_id=event.sceneCollectionId,
            enabled=event.enabled,
        ))

    return entries


def load_sync_config(schedule_path: Path | None = None) -> dict:
    """Load sync config from schedule YAML. Returns defaults if missing."""
    path = get_schedule_path(schedule_path)
    if not path.exists():
        return {"interval": DEFAULT_SYNC_INTERVAL}

    data = yaml.safe_load(path.read_text()) or {}
    sync = data.get("sync", {})
    return {
        "interval": sync.get("interval", DEFAULT_SYNC_INTERVAL),
    }


def save_default_schedule_config(schedule_path: Path | None = None) -> Path:
    """Write default schedule config YAML if it doesn't exist."""
    path = get_schedule_path(schedule_path)
    if path.exists():
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# pvctl schedule sync config\n"
        "# Hub schedules are the source of truth.\n"
        "# pvctl syncs them to cron at this interval.\n"
        "sync:\n"
        f"  interval: {DEFAULT_SYNC_INTERVAL}  # minutes\n"
    )
    return path


def get_pvctl_path() -> str:
    """Resolve absolute path to pvctl binary."""
    path = shutil.which("pvctl")
    if path:
        return path
    return f"{sys.executable} -m pvctl"


def read_crontab() -> list[str]:
    """Read current user crontab lines."""
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            return []
        return result.stdout.splitlines()
    except FileNotFoundError:
        return []


def write_crontab(lines: list[str]) -> None:
    """Write lines to user crontab."""
    content = "\n".join(lines) + "\n"
    subprocess.run(
        ["crontab", "-"],
        input=content, text=True, check=True,
    )


def get_pvctl_cron_entries() -> list[str]:
    """Return all pvctl-managed cron lines (both schedule and sync)."""
    return [
        line for line in read_crontab()
        if CRON_TAG in line or SYNC_CRON_TAG in line
    ]


def install_sync_cron(interval: int) -> str:
    """Install the sync cron entry. Returns the cron expression."""
    pvctl_path = get_pvctl_path()
    existing = read_crontab()

    # Remove existing sync entry
    cleaned = [line for line in existing if SYNC_CRON_TAG not in line]

    cron_expr = f"*/{interval} * * * *"
    sync_line = (
        f"{cron_expr} {pvctl_path} schedule sync --quiet "
        f"2>&1 | logger -t pvctl {SYNC_CRON_TAG}"
    )
    cleaned.append(sync_line)
    write_crontab(cleaned)
    return cron_expr


def _build_schedule_lines(
    entries: list[ScheduleEntry], pvctl_path: str
) -> list[str]:
    """Build cron lines for schedule entries."""
    lines = []
    for entry in entries:
        cmd = (
            f'{pvctl_path} scene activate "{entry.collection_name}" --quiet'
        )
        cron_line = (
            f"{entry.cron_expression} {cmd} "
            f"2>&1 | logger -t pvctl {CRON_TAG} {entry.name}"
        )
        if entry.enabled:
            lines.append(cron_line)
        else:
            lines.append(f"# DISABLED: {cron_line}")
    return lines


def sync_schedule(entries: list[ScheduleEntry]) -> list[tuple[str, str | None, bool]]:
    """Sync hub schedule entries to crontab.

    Only writes crontab if entries have actually changed (avoids triggering
    macOS admin permission prompt on every sync).

    Returns list of (entry_name, cron_expression, enabled).
    """
    pvctl_path = get_pvctl_path()
    existing = read_crontab()

    # Build what the new schedule lines should be
    new_schedule_lines = _build_schedule_lines(entries, pvctl_path)

    # Extract current schedule lines (not sync, not non-pvctl)
    current_schedule_lines = [line for line in existing if CRON_TAG in line]

    # Only write if changed
    if new_schedule_lines != current_schedule_lines:
        cleaned = [line for line in existing if CRON_TAG not in line]
        cleaned.extend(new_schedule_lines)
        write_crontab(cleaned)

    results: list[tuple[str, str | None, bool]] = []
    for entry in entries:
        results.append((entry.name, entry.cron_expression, entry.enabled))
    return results


def uninstall_all() -> int:
    """Remove all pvctl entries (schedule + sync) from crontab."""
    existing = read_crontab()
    cleaned = [
        line for line in existing
        if CRON_TAG not in line and SYNC_CRON_TAG not in line
    ]
    removed = len(existing) - len(cleaned)

    if removed > 0:
        write_crontab(cleaned)

    return removed
