#!/bin/bash
# Convenience wrapper — runs pvctl via uv from the project root
DIR="$(cd "$(dirname "$0")" && pwd)"
exec uv run --project "$DIR" pvctl "$@"
