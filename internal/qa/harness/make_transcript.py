#!/usr/bin/env python3
"""make_transcript.py <run_dir> — baut EINE lesbare Voll-Transkript-Datei.

Merged aus channel.md (Tisch-Absprache + Leader-Post je Runde) + sl_full.jsonl
(vollständige SL-Narration je Runde) → <run_dir>/TRANSCRIPT.md. So liest man die
ganze 5er-Session als durchgehendes Dokument statt drei Dateien parallel.

Aufruf: python3 make_transcript.py <run_dir>
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path


def main(run_dir: str) -> int:
    run = Path(run_dir)
    slf = run / "sl_full.jsonl"
    chan = run / "channel.md"
    if not slf.exists() or not chan.exists():
        print(f"FEHLER: sl_full.jsonl oder channel.md fehlt in {run}", flush=True)
        return 2

    # Volle SL-Antworten je Turn
    sl: dict[str, dict] = {}
    for line in slf.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        o = json.loads(line)
        sl[str(o.get("turn"))] = o

    # channel.md in Turn-Blöcke zerlegen (Absprache + Leader-Post)
    blocks: dict[str, dict[str, list]] = {}
    cur = mode = None
    for ln in chan.read_text(encoding="utf-8").splitlines():
        m = re.match(r"##\s*Turn\s*(\d+)\s*—\s*(Absprache|Leader-Post)", ln)
        if m:
            cur, mode = m.group(1), m.group(2)
            blocks.setdefault(cur, {"Absprache": [], "Leader-Post": []})
            continue
        if cur and mode:
            blocks[cur][mode].append(ln)

    # Kopf aus run.md (Setup/Anker)
    header = ""
    rm = run / "run.md"
    if rm.exists():
        header = "\n".join(rm.read_text(encoding="utf-8").splitlines()[:6])

    out = [f"# Transkript — {run.name}\n", header, "\n---\n"]
    turns = sorted(set(list(blocks.keys()) + [t for t in sl if t.isdigit()]), key=int)
    for t in turns:
        out.append(f"\n## ── Runde {t} " + f"(Szene {sl.get(t, {}).get('scene', '?')}/12, "
                   f"Phase {sl.get(t, {}).get('phase') or '—'}) ──\n")
        b = blocks.get(t, {"Absprache": [], "Leader-Post": []})
        absr = "\n".join(x for x in b["Absprache"] if x.strip())
        lead = "\n".join(x for x in b["Leader-Post"] if x.strip())
        if absr:
            out.append("**Absprache am Tisch (Messenger):**\n\n" + absr + "\n")
        if lead:
            out.append("**Leader tippt an die Spielleitung:**\n\n" + lead + "\n")
        if t in sl:
            out.append("**SPIELLEITUNG:**\n\n" + sl[t]["content"] + "\n")

    dest = run / "TRANSCRIPT.md"
    dest.write_text("\n".join(out), encoding="utf-8")
    print(f"TRANSCRIPT.md geschrieben: {dest} ({len(turns)} Runden, {dest.stat().st_size} Bytes)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Aufruf: python3 make_transcript.py <run_dir>", flush=True)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
