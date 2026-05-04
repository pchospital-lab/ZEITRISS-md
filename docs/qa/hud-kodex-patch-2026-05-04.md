---
title: "QA-Status – HUD/Kodex-Patch (2026-05-04)"
status: "in-progress"
owner: "repo-agent"
---

# QA-Status – HUD/Kodex-Patch

## Ziel

Abarbeitung des Berichts `uploads/hud-und-kodex-patch.pdf` mit Fokus auf
Intro-HUD-Reihenfolge, Inline-Darstellung des Kodex-Hinweises und Linter-Absicherung.

## Umgesetzt in diesem Schritt

- [x] `systems/gameflow/cinematic-start.md`
  - HUD-Overlay (`Nullzeit-Puffer · Transfer ...`) vor Kodex-Handshake gezogen.
  - Kodex-Handshake und Tipp explizit als Inline-Hinweise geführt (kein Code-Fence).
- [x] `scripts/lint_hud_kodex.py`
  - Erkennung für fehlerhafte Code-Fences mit Legacy-HUD/Kodex-Tags ergänzt.
- [x] `scripts/tests/test_lint_hud_kodex.py`
  - Tests für neue Fence-Erkennung ergänzt.

## Offen / Nächster möglicher Schritt

- [ ] Optional: HUD-Icon-Review gemäß Bericht (nur falls konsistent mit Runtime-SSOT).
- [ ] Optional: explizite QA-Simulation für `ENTRY`-Tag-Budget-Bypass dokumentieren
      (Implementierung ist bereits vorhanden, derzeit kein Code-Eingriff nötig).

## Verifikation (Patchnote-Stil)

- `pytest scripts/tests/test_lint_hud_kodex.py` → OK (5 passed)
- `bash scripts/smoke.sh` → OK (All smoke checks passed)
