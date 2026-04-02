"""Test utility functions."""

import pytest

from pvctl.utils import pct_to_pos, pos_to_pct, resolve_name


class TestPositionMath:
    def test_pct_to_pos_0(self):
        assert pct_to_pos(0) == 0

    def test_pct_to_pos_100(self):
        assert pct_to_pos(100) == 65535

    def test_pct_to_pos_50(self):
        assert pct_to_pos(50) == 32768

    def test_pos_to_pct_0(self):
        assert pos_to_pct(0) == 0

    def test_pos_to_pct_65535(self):
        assert pos_to_pct(65535) == 100

    def test_roundtrip(self):
        for pct in [0, 25, 50, 65, 75, 100]:
            assert pos_to_pct(pct_to_pos(pct)) == pct


class _Item:
    def __init__(self, name: str):
        self.name = name


class TestResolveName:
    items = [_Item("Master 1"), _Item("Master Big"), _Item("Lila 1"), _Item("Anna Small")]

    def test_exact_match(self):
        result = resolve_name("Lila 1", self.items, lambda x: x.name, "shade")
        assert result.name == "Lila 1"

    def test_exact_case_insensitive(self):
        result = resolve_name("lila 1", self.items, lambda x: x.name, "shade")
        assert result.name == "Lila 1"

    def test_substring_unique(self):
        result = resolve_name("Anna", self.items, lambda x: x.name, "shade")
        assert result.name == "Anna Small"

    def test_substring_ambiguous_exits(self):
        with pytest.raises(SystemExit):
            resolve_name("Master", self.items, lambda x: x.name, "shade")

    def test_no_match_exits(self):
        with pytest.raises(SystemExit):
            resolve_name("Kitchen", self.items, lambda x: x.name, "shade")

    def test_fuzzy_match(self):
        result = resolve_name("Anna Smal", self.items, lambda x: x.name, "shade")
        assert result.name == "Anna Small"
