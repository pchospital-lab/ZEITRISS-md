#!/usr/bin/env python3
"""Check critical doc anchors exist and are referenced correctly."""
from __future__ import annotations

from pathlib import Path
import json
import sys


# Beim direkten Aufruf über ``python3 scripts/lint_doc_links.py`` liegt das Paket
# ``scripts`` nicht automatisch im ``sys.path``. Wir ergänzen deshalb das
# Repository-Wurzelverzeichnis, damit die Modulimporte sowohl im Modul- als auch
# im Skriptmodus funktionieren.
if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.lib_repo import repo_root, read_text, get_logger
from scripts.lib_md import extract_md_anchors, slugify

log = get_logger("lint_doc_links")


def main() -> int:
    root = repo_root(Path(__file__))
    cfgp = root / ".lint" / "doc_anchors.json"
    if not cfgp.exists():
        log.info("No .lint/doc_anchors.json found")
        return 0
    cfg = json.loads(read_text(cfgp))
    items = cfg.get("critical", [])
    ok = True
    for item in items:
        rel = item["file"]
        aid_raw = item["anchor"]
        aid = slugify(aid_raw)
        p = root / rel
        if not p.exists():
            log.error("Target missing: %s", rel)
            ok = False
            continue
        anchors = extract_md_anchors(read_text(p))
        if aid in anchors:
            log.info("Anchor OK: %s#%s", rel, aid_raw)
        else:
            log.error("Missing anchor: %s#%s", rel, aid_raw)
            ok = False
    log.log(25, "Summary: %s", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
