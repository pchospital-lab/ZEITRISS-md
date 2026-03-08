---
title: "QA-Log 2026-03-08 – Durchlauf 76 (HQ-Save/Reset Klarheit)"
status: "abgeschlossen"
run_id: "zr-018-d76"
---

# Kontext

Anschlusslauf auf Basis der Rückfrage, ob `stress`/`psi_heat` nicht ohnehin im
HQ resetten und Speichern ausschließlich dort möglich ist. Ziel: keine
Regeländerung, sondern SSOT-Klarstellung über Masterprompt, SL-Referenz und
Speicherdoku.

# Umgesetzte Änderungen

1. **Masterprompt präzisiert**
   - `meta/masterprompt_v6.md`: Schema-Regelblock um eine explizite
     HQ-Save-Invariante ergänzt (Save nur im HQ; Debrief-Reset auf HQ-Basis für
     `stress`/`psi_heat`/`SYS`; Felder bleiben im Schema für expliziten
     HQ-Status und Legacy-/Import-Stabilität).

2. **SL-Referenz harmonisiert**
   - `core/sl-referenz.md`: Persistenz-Bullet auf dieselbe Invariante gehärtet;
     `psi_heat` als Feld bei Psi-Charakteren formuliert.

3. **Speicherdoku harmonisiert**
   - `systems/gameflow/speicher-fortsetzung.md`: direkt vor dem kanonischen
     v7-Exportformat denselben HQ-only-/Debrief-Reset-Hinweis ergänzt.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

# Bewertung

- Die gesuchte Aussage ist jetzt explizit in allen maßgeblichen SSOT-Texten
  verankert.
- Kein Drift zwischen Masterprompt, SL-Referenz und Speicherdokumentation.
- Keine Ausweitung des Schemas; nur Klarstellung des bestehenden Verhaltens.
