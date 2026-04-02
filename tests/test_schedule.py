"""Test schedule management: hub event conversion, sync config, cron generation."""

from pathlib import Path

import yaml

from pvctl.api.models import ScheduledEvent
from pvctl.schedule_manager import (
    ScheduleEntry,
    hub_events_to_entries,
    load_sync_config,
    save_default_schedule_config,
)


def _make_event(**kwargs) -> ScheduledEvent:
    defaults = {
        "id": 1,
        "enabled": True,
        "sceneCollectionId": 100,
        "daySunday": False,
        "dayMonday": False,
        "dayTuesday": False,
        "dayWednesday": False,
        "dayThursday": False,
        "dayFriday": False,
        "daySaturday": False,
        "eventType": 0,
        "hour": 7,
        "minute": 30,
    }
    defaults.update(kwargs)
    return ScheduledEvent.model_validate(defaults)


class TestHubEventsToEntries:
    def test_basic_conversion(self):
        event = _make_event(
            dayMonday=True, dayTuesday=True, dayWednesday=True,
            dayThursday=True, dayFriday=True,
            hour=7, minute=30, sceneCollectionId=100,
        )
        entries = hub_events_to_entries([event], {100: "Morning Up"})
        assert len(entries) == 1
        assert entries[0].name == "Morning Up"
        assert entries[0].time == "07:30"
        assert entries[0].days == [1, 2, 3, 4, 5]
        assert entries[0].cron_expression == "30 7 * * 1,2,3,4,5"

    def test_disabled_event(self):
        event = _make_event(enabled=False, dayMonday=True)
        entries = hub_events_to_entries([event], {100: "Test"})
        assert entries[0].enabled is False

    def test_daily_event(self):
        event = _make_event(
            daySunday=True, dayMonday=True, dayTuesday=True,
            dayWednesday=True, dayThursday=True, dayFriday=True,
            daySaturday=True,
        )
        entries = hub_events_to_entries([event], {100: "Daily"})
        assert entries[0].days_display == "Daily"

    def test_unknown_collection(self):
        event = _make_event(sceneCollectionId=999, dayMonday=True)
        entries = hub_events_to_entries([event], {})
        assert entries[0].name == "collection-999"


class TestScheduleEntry:
    def test_cron_expression(self):
        entry = ScheduleEntry(
            name="Test", time="07:30", days=[1, 2, 3, 4, 5],
            collection_name="Morning", collection_id=100,
        )
        assert entry.cron_expression == "30 7 * * 1,2,3,4,5"

    def test_days_display_weekdays(self):
        entry = ScheduleEntry(
            name="Test", time="07:00", days=[1, 2, 3, 4, 5],
            collection_name="X", collection_id=1,
        )
        assert entry.days_display == "Mon\u2013Fri"

    def test_days_display_weekends(self):
        entry = ScheduleEntry(
            name="Test", time="07:00", days=[0, 6],
            collection_name="X", collection_id=1,
        )
        assert entry.days_display == "Sat\u2013Sun"


class TestSyncConfig:
    def test_default_config(self, tmp_path: Path):
        config_dir = tmp_path / "pvctl"
        config_dir.mkdir()
        config = load_sync_config(config_dir)
        assert config["interval"] == 5

    def test_custom_interval(self, tmp_path: Path):
        config_dir = tmp_path / "pvctl"
        config_dir.mkdir()
        schedule_file = config_dir / "schedule.yaml"
        schedule_file.write_text(yaml.dump({"sync": {"interval": 10}}))
        config = load_sync_config(config_dir)
        assert config["interval"] == 10

    def test_save_default(self, tmp_path: Path):
        config_dir = tmp_path / "pvctl"
        config_dir.mkdir()
        path = save_default_schedule_config(config_dir)
        assert path.exists()
        data = yaml.safe_load(path.read_text())
        assert data["sync"]["interval"] == 5

    def test_save_default_doesnt_overwrite(self, tmp_path: Path):
        config_dir = tmp_path / "pvctl"
        config_dir.mkdir()
        schedule_file = config_dir / "schedule.yaml"
        schedule_file.write_text(yaml.dump({"sync": {"interval": 15}}))
        save_default_schedule_config(config_dir)
        data = yaml.safe_load(schedule_file.read_text())
        assert data["sync"]["interval"] == 15
