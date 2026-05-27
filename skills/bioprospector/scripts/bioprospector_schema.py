#!/usr/bin/env python3
"""Shared schema loader for BioProspector scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "schemas" / "bioprospector-ledgers.json"


def load_schema(path: Path | None = None) -> dict[str, Any]:
    schema_path = path or DEFAULT_SCHEMA_PATH
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ledger_headers(schema: dict[str, Any] | None = None) -> dict[str, list[str]]:
    loaded = schema or load_schema()
    return {key: list(value) for key, value in loaded.get("ledger_headers", {}).items()}


def enum_values(name: str, schema: dict[str, Any] | None = None) -> set[str]:
    loaded = schema or load_schema()
    return set(loaded.get("enums", {}).get(name, []))


def required_ledger_keys(schema: dict[str, Any] | None = None) -> set[str]:
    loaded = schema or load_schema()
    return set(loaded.get("required_ledger_keys", []))


def optional_ledger_keys(schema: dict[str, Any] | None = None) -> set[str]:
    loaded = schema or load_schema()
    return set(loaded.get("optional_ledger_keys", []))
