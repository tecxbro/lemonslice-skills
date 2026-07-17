#!/usr/bin/env python3
"""Apply the reviewed LemonSlice hardening bundle to this checkout."""
from __future__ import annotations

import base64
import io
import tarfile
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    resolved_root = root.resolve()
    parts = sorted((root / "scripts").glob(".hardening_bundle.part*"))
    if not parts:
        raise RuntimeError("Hardening bundle parts are missing")
    encoded = "".join(path.read_text(encoding="utf-8") for path in parts)
    payload = base64.b64decode(encoded)
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            target = (root / member.name).resolve()
            if target != resolved_root and resolved_root not in target.parents:
                raise RuntimeError(f"Unsafe archive member: {member.name}")
        archive.extractall(root)
    print(f"Applied {len(members)} hardening files from {len(parts)} bundle parts.")


if __name__ == "__main__":
    main()
