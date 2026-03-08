---
title: "Issue-Pack Durchlauf 77 – Round4 Anschluss: Chronopolis-Wording + Bridge-Klarheit"
status: "abgeschlossen"
owner: "codex"
created: "2026-03-08"
links:
  issue: "internal/qa/process/known-issues.md#zr-018-ruf-tier-progress-und-alienmystery-onboarding-als-ssot-nachziehen"
  statusmatrix: "internal/qa/process/ruf-alien-statusmatrix.md"
---

# Ziel

Round-4-Anschlusslauf mit Fokus auf verbliebene Formulierungs-/SSOT-Kanten in
`systems/gameflow/speicher-fortsetzung.md`:

1. Chronopolis-Hinweis konsistent als In-World-Hinweis statt UI-Popup halten.
2. SaveGuard-Pseudocode explizit als Runtime-/Legacy-Bridge vor v7-Normalisierung
   kennzeichnen (kein kanonischer Neu-Export).
3. Pflicht-Smoke und Linklint erneut ausführen.

# Checkliste

- [x] Chronopolis-Makrotext auf In-World-Warnhinweis harmonisiert.
- [x] SaveGuard-Pseudocode mit klarer Bridge-/Legacy-Einordnung ergänzt.
- [x] Pflicht-Smoke ausgeführt.
- [x] Linklint ausgeführt.
- [x] Prozessanker auf Durchlauf 77 erweitert.

# Abschluss

Die letzte Round-4-Stilkante in der Speicherdoku ist geschlossen; gleichzeitig
ist die Leserführung klarer, dass Legacy-/Runtime-Felder im Guard-Block nur
Import-/Normalisierungszwecken dienen und nicht das kanonische v7-Exportmodell
ersetzen.
