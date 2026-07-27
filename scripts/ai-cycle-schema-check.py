#!/usr/bin/env python3
"""Lightweight JSON Schema subset validator for current-cycle.json (stdlib only).

Supports: type, enum, required, properties, additionalProperties (ignored),
$ref to local #/$defs, minLength, minimum, arrays/items, null unions.
Does not require the jsonschema package.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def fail(msg: str) -> None:
    print(f"FAIL: schema: {msg}", file=sys.stderr)


def resolve_ref(schema: dict[str, Any], root: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not ref:
        return schema
    if not isinstance(ref, str) or not ref.startswith("#/"):
        raise ValueError(f"unsupported $ref: {ref}")
    node: Any = root
    for part in ref[2:].split("/"):
        if not isinstance(node, dict) or part not in node:
            raise ValueError(f"unresolved $ref: {ref}")
        node = node[part]
    if not isinstance(node, dict):
        raise ValueError(f"$ref does not point to object: {ref}")
    return node


def type_matches(value: Any, expected: str | list[str]) -> bool:
    types = expected if isinstance(expected, list) else [expected]
    for t in types:
        if t == "null" and value is None:
            return True
        if t == "string" and isinstance(value, str):
            return True
        if t == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if t == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if t == "boolean" and isinstance(value, bool):
            return True
        if t == "array" and isinstance(value, list):
            return True
        if t == "object" and isinstance(value, dict):
            return True
    return False


def validate(
    value: Any,
    schema: dict[str, Any],
    root: dict[str, Any],
    path: str,
    errors: list[str],
) -> None:
    try:
        schema = resolve_ref(schema, root)
    except ValueError as exc:
        label = path if path else "(root)"
        errors.append(f"{label}: {exc}")
        return

    if "type" in schema and not type_matches(value, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']}, got {type(value).__name__}")
        return

    if value is None:
        return

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} not in enum {schema['enum']}")

    if "minLength" in schema and isinstance(value, str) and len(value) < schema["minLength"]:
        errors.append(f"{path}: string shorter than minLength {schema['minLength']}")

    if "minimum" in schema and isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema["minimum"]:
            errors.append(f"{path}: value {value} below minimum {schema['minimum']}")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required field '{key}'")
        props = schema.get("properties", {})
        for key, child in value.items():
            if key in props:
                child_path = f"{path}.{key}" if path else key
                validate(child, props[key], root, child_path, errors)

    if isinstance(value, list) and "items" in schema:
        item_schema = schema["items"]
        for i, item in enumerate(value):
            validate(item, item_schema, root, f"{path}[{i}]", errors)


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "usage: ai-cycle-schema-check.py <state.json> <schema.json>",
            file=sys.stderr,
        )
        return 2

    state_path = Path(sys.argv[1])
    schema_path = Path(sys.argv[2])

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load inputs: {exc}")
        return 1

    errors: list[str] = []
    try:
        validate(state, schema, schema, "", errors)
    except ValueError as exc:
        fail(str(exc))
        return 1

    if errors:
        for err in errors:
            fail(err)
        print(f"schema validation failed with {len(errors)} issue(s).", file=sys.stderr)
        return 1

    print("OK: JSON matches schema subset")
    return 0


if __name__ == "__main__":
    sys.exit(main())
