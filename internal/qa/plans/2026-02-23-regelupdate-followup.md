# Follow-up Fahrplan – Regelupdate Terminologie/Chronopolis/Save (2026-02-23)

## Kontext
Dieses Follow-up protokolliert offene QA-Befunde aus dem Regelupdate-Lauf
(EP→XP-Terminologie, Chronopolis-Tod, Save-Taktung, Gruppen-Todesentscheid).

## Offene Punkte aus Pflichtprüfungen
- ✅ Erledigt: Legacy-Dokument archiviert unter
  `meta/archive/speicher-fortsetzung.legacy.md` (nicht mehr im Runtime-Pfad).
- ✅ Erledigt: `migrate_save` ist wieder explizit im Save-Modul dokumentiert,
  `tools/lint_runtime.py` und `GM_STYLE=verbose tools/lint_runtime.py` laufen
  grün.
- ✅ Erledigt: `make lint`, `bash scripts/smoke.sh`,
  `python3 scripts/lint_doc_links.py` und `python3 scripts/lint_umlauts.py`
  laufen vollständig durch.
- ✅ Erledigt: `tools/test_economy_merge.js` nutzt im Merge-Test jetzt ein
  schema-konformes `incomingSave.ui.action_mode="uncut"`; `make test` läuft
  wieder grün.

## Abschlussstand
Der Follow-up-Block ist abgeschlossen; es bestehen aktuell keine offenen
Pflichtprüfungs-Punkte mehr aus dem Regelupdate-Lauf vom 2026-02-23.

## Nachtrag Upload-Abgleich (Deep-Research-Report(4))

Die im Upload `uploads/deep-research-report(4).md` priorisierten Starttickets
wurden gegen den aktuellen Repo-Stand gegengeprüft und als abgeschlossen
markiert. Der Upload ist damit als Eingangsdokument archiviert; operative
Steuerung erfolgt ausschließlich über `internal/qa/plans/` und
`internal/qa/logs/`.

- ✅ ZR-001: Exploding-/Burst-Cap-SSOT vereinheitlicht.
- ✅ ZR-002: Px-Default ohne automatischen Strafabzug vereinheitlicht.
- ✅ ZR-003: Px-Scope für solo/npc-team vs. gruppe präzisiert.
- ✅ ZR-004: HQ-Rückkehr als Loop-Invariante durchgezogen.
- ✅ ZR-005: Chronopolis-Todesregel ohne Free-Respawn vereinheitlicht.

- ✅ ZR-010: Korrigiert auf "Mirror ohne Auslagerung" (Runtime-Makros bleiben vollständig im Toolkit; `internal/runtime/toolkit-runtime-makros.md` bleibt reiner QA-/Review-Spiegel).

## Nachzug Entscheidung GRP/TEMP (2026-02-23)

Deep-Research-Punkt „Team-TEMP im Gruppenspiel unklar“ ist jetzt als
SSOT-Entscheidung festgezogen und in Runtime + Wissensmodule gespiegelt:

- **GRP = Gruppe**.
- **Team-TEMP** im Modus `gruppe` wird als **aufgerundeter Durchschnitt**
  geführt: `TEMP_gruppe = ceil(sum(temp aller aktiven Charaktere) / anzahl)`.
- Der Teamwert steuert **Px-ETA** und TEMP-basierte Frequenzen (z. B.
  Fahrzeug-Verfügbarkeit).
- „Forward-only mode“ wird **nicht** als Default oder Pflichtmodus
  nachgezogen; der Hinweis im Upload bleibt reine Audit-Frage ohne Umsetzung.
