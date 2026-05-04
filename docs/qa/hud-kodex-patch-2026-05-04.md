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
- [x] `runtime.js`
  - Chat-UI-Normalisierung ergänzt: Falls eine Runtime-Ausgabe doch als
    Markdown-Code-Fence (` ``` `) hereinkommt, wird sie vor Ausgabe automatisch in
    Inline-Backticks je Zeile umgewandelt.
  - Ziel: keine schwarzen Codeblöcke im Chatfenster, ohne die HUD/Kodex-Textinhalte zu verlieren.
- [x] `meta/masterprompt_v6.md`
  - Harte Ausgaberegel verankert: HUD/Kodex nie als Code-Fence, nur Inline-Backticks.
  - Intro-Reihenfolge explizit fixiert: erst Nullzeit-HUD, dann Kodex-Handshake.
- [x] `core/sl-referenz.md` + `systems/toolkit-gpt-spielleiter.md`
  - Gleiche UI-Regel im spielrelevanten Wissensspeicher verankert, damit die KI-SL
    dieselbe Formatvorgabe in Runtime-Ausgaben konsistent befolgt.

- [x] `meta/masterprompt_v6.md` + `systems/toolkit-gpt-spielleiter.md`
  - Leak-Guard präzisiert: nur Roh-Makro/Debug unterdrücken, **nicht** gerenderte Makro-Ergebnisse.
  - Sprung-/Entry-Sequenzen und sichtbare Kommandos (`menü`, `!save`, `!load`) bleiben ausdrücklich erlaubt.
- [x] `systems/gameflow/cinematic-start.md`
  - Terminologie auf `Kodex-sync` vereinheitlicht.

## Offen / Nächster möglicher Schritt

- [ ] Optional: HUD-Icon-Review gemäß Bericht (nur falls konsistent mit Runtime-SSOT).
- [ ] Optional: Zusatz-Linterregel, die generische Fence-Blöcke mit HUD-typischen
      Statuszeilen (`LP`, `Stress`, `EP/MS/SC`) im WS-Text hart blockt.
- [x] QA-Notiz ergänzt: ENTRY-/Sprungsequenzen bleiben trotz Leak-Guard zulässig (Prompt+Toolkit präzisiert).

## Verifikation (Patchnote-Stil)

- `pytest scripts/tests/test_lint_hud_kodex.py` → OK (5 passed)
- `bash scripts/smoke.sh` → OK (All smoke checks passed)
- `bash scripts/smoke.sh` (nach Runtime-Normalisierung erneut) → OK (All smoke checks passed)
