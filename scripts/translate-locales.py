#!/usr/bin/env python3
"""Fill a target locale JSON by translating missing strings from en.json.

Usage:
  ./scripts/translate-locales.py --to ru
  ./scripts/translate-locales.py --to de --force
  ./scripts/translate-locales.py --to fr --dry-run

Uses the public Google Translate endpoint (dev tooling only — not used at app runtime).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "frontend" / "src" / "locales"
EN_PATH = LOCALES_DIR / "en.json"


def flatten(node: Any, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            out.update(flatten(value, path))
    elif isinstance(node, str):
        out[prefix] = node
    return out


def unflatten(flat: dict[str, str]) -> dict[str, Any]:
    root: dict[str, Any] = {}
    for path, value in flat.items():
        parts = path.split(".")
        cursor: dict[str, Any] = root
        for part in parts[:-1]:
            nxt = cursor.get(part)
            if not isinstance(nxt, dict):
                nxt = {}
                cursor[part] = nxt
            cursor = nxt
        cursor[parts[-1]] = value
    return root


def translate_text(text: str, *, source: str, target: str) -> str:
    # Keep placeholders like {title} intact by shielding them.
    shields: list[str] = []

    def shield(match: str) -> str:
        shields.append(match)
        return f"⟦{len(shields) - 1}⟧"

    import re

    protected = re.sub(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}", lambda m: shield(m.group(0)), text)
    query = urllib.parse.urlencode(
        {
            "client": "gtx",
            "sl": source,
            "tl": target,
            "dt": "t",
            "q": protected,
        }
    )
    url = f"https://translate.googleapis.com/translate_a/single?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "ScribeLocaleTranslate/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    chunks = payload[0] if payload and payload[0] else []
    translated = "".join(part[0] for part in chunks if part and part[0])
    for i, original in enumerate(shields):
        translated = translated.replace(f"⟦{i}⟧", original)
        translated = translated.replace(f"[[{i}]]", original)
    return translated.strip() or text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--to", required=True, help="Target language code (e.g. ru, de, fr)")
    parser.add_argument("--from", dest="source", default="en", help="Source language (default: en)")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-translate keys that already exist in the target file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes without writing the file",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.15,
        help="Delay between API calls in seconds (default: 0.15)",
    )
    args = parser.parse_args()

    if not EN_PATH.is_file():
        print(f"Missing source locale: {EN_PATH}", file=sys.stderr)
        return 1

    source_tree = json.loads(EN_PATH.read_text(encoding="utf-8"))
    source_flat = flatten(source_tree)

    target_path = LOCALES_DIR / f"{args.to}.json"
    if target_path.is_file() and args.to != args.source:
        existing_flat = flatten(json.loads(target_path.read_text(encoding="utf-8")))
    else:
        existing_flat = {}

    out_flat: dict[str, str] = {}
    translated = 0
    kept = 0
    for key, english in source_flat.items():
        if key in existing_flat and not args.force:
            out_flat[key] = existing_flat[key]
            kept += 1
            continue
        if args.to == args.source:
            out_flat[key] = english
            kept += 1
            continue
        try:
            text = translate_text(english, source=args.source, target=args.to)
        except Exception as exc:  # noqa: BLE001 — surface network/parse issues
            print(f"Failed on {key}: {exc}", file=sys.stderr)
            return 1
        out_flat[key] = text
        translated += 1
        print(f"  {key}: {english!r} → {text!r}")
        time.sleep(max(0.0, args.sleep))

    tree = unflatten(out_flat)
    print(f"Translated {translated}, kept {kept}, total {len(out_flat)}")
    if args.dry_run:
        print(json.dumps(tree, ensure_ascii=False, indent=2))
        return 0

    target_path.write_text(
        json.dumps(tree, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {target_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
