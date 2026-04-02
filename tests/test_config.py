"""Test config file management."""

from pathlib import Path

from pvctl.config import get_hub_ip, load_config, save_config


class TestConfig:
    def test_save_and_load(self, tmp_path: Path):
        config = {"hub": {"ip": "192.168.7.38", "name": "Test Hub"}}
        config_dir = tmp_path / "pvctl"
        config_dir.mkdir()
        path = save_config(config, config_dir)
        assert path.exists()

        loaded = load_config(config_dir)
        assert loaded["hub"]["ip"] == "192.168.7.38"

    def test_load_missing_returns_empty(self, tmp_path: Path):
        config_dir = tmp_path / "nonexistent"
        config_dir.mkdir()
        assert load_config(config_dir) == {}

    def test_get_hub_ip_from_config(self):
        config = {"hub": {"ip": "10.0.0.1"}}
        assert get_hub_ip(config) == "10.0.0.1"

    def test_get_hub_ip_override(self):
        config = {"hub": {"ip": "10.0.0.1"}}
        assert get_hub_ip(config, override="192.168.1.1") == "192.168.1.1"

    def test_get_hub_ip_missing_exits(self):
        import pytest

        with pytest.raises(SystemExit):
            get_hub_ip({})
