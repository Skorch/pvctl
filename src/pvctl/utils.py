"""Utility functions: name matching, position math."""

from __future__ import annotations

import difflib
import sys
from typing import TypeVar

T = TypeVar("T")

# Position encoding constants
POS_MAX = 65535
POS_MIN = 0


def pct_to_pos(pct: int) -> int:
    """Convert 0-100 percentage to 0-65535 position value."""
    return round(pct / 100 * POS_MAX)


def pos_to_pct(pos: int) -> int:
    """Convert 0-65535 position value to 0-100 percentage."""
    return round(pos / POS_MAX * 100)


def resolve_name(
    query: str,
    items: list[T],
    name_fn: callable,
    item_label: str = "item",
) -> T:
    """Resolve a user-provided name to a single item.

    Resolution order:
    1. Exact match (case-insensitive)
    2. Substring match
    3. Fuzzy match via difflib (threshold >= 0.6)
    4. If ambiguous: print candidates, exit 1
    5. If no match: print suggestions, exit 1

    Args:
        query: User-provided name string.
        items: List of items to search.
        name_fn: Callable that extracts the name string from an item.
        item_label: Label for error messages (e.g. "shade", "scene").

    Returns:
        The matched item.
    """
    query_lower = query.lower()
    names = [(name_fn(item), item) for item in items]

    # 1. Exact match (case-insensitive)
    exact = [(n, item) for n, item in names if n.lower() == query_lower]
    if len(exact) == 1:
        return exact[0][1]

    # 2. Substring match
    substr = [(n, item) for n, item in names if query_lower in n.lower()]
    if len(substr) == 1:
        return substr[0][1]
    if len(substr) > 1:
        _ambiguous_exit(query, [n for n, _ in substr], item_label)

    # 3. Fuzzy match
    all_names = [n for n, _ in names]
    close = difflib.get_close_matches(query, all_names, n=3, cutoff=0.6)
    if len(close) == 1:
        for n, item in names:
            if n == close[0]:
                return item
    if len(close) > 1:
        _ambiguous_exit(query, close, item_label)

    # 4. No match
    if close:
        suggestions = ", ".join(f'"{c}"' for c in close)
        print(f'No {item_label} matching "{query}". Did you mean: {suggestions}?', file=sys.stderr)
    else:
        print(f'No {item_label} matching "{query}".', file=sys.stderr)
        if all_names:
            print(f"Available: {', '.join(all_names)}", file=sys.stderr)
    raise SystemExit(1)


def _suggest_name(query: str, names: list[str]) -> str | None:
    """Return the best fuzzy match for a name, or None."""
    close = difflib.get_close_matches(query, names, n=1, cutoff=0.6)
    return close[0] if close else None


def _ambiguous_exit(query: str, candidates: list[str], item_label: str) -> None:
    """Print ambiguous match message and exit."""
    print(f'"{query}" matches multiple {item_label}s:', file=sys.stderr)
    for c in candidates:
        print(f"  - {c}", file=sys.stderr)
    print("Be more specific.", file=sys.stderr)
    raise SystemExit(1)
