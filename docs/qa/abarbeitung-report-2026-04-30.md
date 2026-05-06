# Abarbeitung Report (30.04.2026) — Save/Merge/Dispatcher

## Ziel

Dieses Dokument übersetzt den Nachcheck in eine anschlussfähige Arbeitsliste.
Fokus: **Masterprompt + Wissensdateien** als einziges Laufzeitsystem in der
Chatoberfläche (inkl. Split/Merge über mehrere parallele Chats).


## In diesem Schritt erledigt

- **Persistenzvertrag geschärft (P0-1):** `core/sl-referenz.md` präzisiert,
  dass `campaign.mode` ausschließlich Persistenzstrategie (`mixed|preserve|trigger`)
  ist und Arena-Status über Runtime (`runtime_phase`) läuft.
- **`campaign.mode`-Härtung dokumentiert (P0-3):** PvP-/Arena-Passagen
  stellen jetzt explizit klar, dass kein `campaign.mode='pvp'` persistiert
  wird; Fallback bleibt `mixed` bei fehlendem `arena.previous_mode`.
- **Arena-Resume entschärft:** `arena.resume_token` ist als runtime-only markiert;
  HQ-Load erfolgt über den regulären Arena-Router statt Auto-Rejoin via Save.
- **Persistenzvertrag weiter gespiegelt (P0-2, Teil 1):** `gameplay/kampagnenstruktur.md` nennt `campaign.mode` jetzt explizit als persistente Pool-Strategie; aktive Missionszustände laufen über `runtime_phase`, HQ-Anker über `continuity.last_seen` (`mode="hq"`, `location="HQ"`).
- **Persistenzvertrag in weiteren WS-Modulen gespiegelt (P0-2, Teil 2):**
  `systems/toolkit-gpt-spielleiter.md` und
  `systems/gameflow/speicher-fortsetzung.md` stellen Arena/Core/Rift-Zustände
  jetzt konsistent als Runtime (`runtime_phase` + `arena.*`) dar; `campaign.mode`
  bleibt als persistente Strategie (`mixed|preserve|trigger`) dokumentiert.
- **P0-2 Abschluss in Toolkit nachgezogen:** verbleibende Altformulierungen
  (`campaign.previous_mode`, `state.phase/campaign.phase`) in
  `systems/toolkit-gpt-spielleiter.md` sind auf
  `arena.previous_mode` bzw. `runtime_phase` harmonisiert.
- **Rest-Scan abgeschlossen (P0-2, final):** Ergänzende Wissens-/QA-Texte
  sind auf den aktuellen Vertrag gezogen (Legacy-`phase: core`-Snippet auf
  `runtime_phase: core`; SaveGuard-Trace-Text in
  `systems/gameflow/speicher-fortsetzung.md` auf `runtime_phase` + Legacy-
  Fallback `state.phase` präzisiert).



- **Chargen-Save-Gate regressionssicher abgeschlossen (P0):** Der klassische
  Startpfad bleibt verbindlich `Chargenabschluss -> HQ-Heimkehrbeat -> einmaliges
  Save-Angebot -> HQ-Menü`; Briefing startet erst nach expliziter
  Spielerentscheidung. Der Status ist zusätzlich in der v7-Checkliste als
  erledigt dokumentiert (`#11 Chargen-Save-Gate`).

## Offen (nächste Steps)

### P1 — Unmittelbar danach

1. **5er-Split/Merge-Matrix als QA-Standard**  
   Fälle 4/1, 3/2, Resplit, Konfliktfälle, deterministische Thread-IDs.

2. **Seed-Cap/Overflow beweisen**  
   Merge >12 Seeds mit erwartetem Overflow-Logging (Trace + Flags).

3. **Arena-/Rift-Transferhygiene**  
   Kein persistenter Auto-Rejoin-Drift; HQ-only Savepfad und Wallet-Trennung
   in Negativtests sichern.

### P2 — Nach Stabilisierung

4. **Chronopolis-Qualitätspass**  
   Spawn-Prioritäten, shared/roster echoes, Beat-Loop-Varianz dokumentiert
   testen.

## Übergabeformat für den nächsten Step

Der nächste Bearbeitungsschritt sollte immer:

1. diese Datei aktualisieren (Was erledigt / Was offen),
2. die betroffenen Wissensmodule synchron ändern,
3. `bash scripts/smoke.sh` laufen lassen,
4. bei QA-relevanten Änderungen die betroffenen Fixture-Dateien benennen.


## Update 2026-05-06 — Startpaket Datensatztrennung

### Neu erledigt

- **Issue-Paket in QA überführt:** Vorschläge aus der externen Unterredung/Uploads
  wurden als priorisierte Startliste in `docs/qa/issue-pack-datensatz-trennung-2026-05-06.md`
  verankert (P0/P1/P2 mit Fundstellen).
- **Arbeitsprinzip fixiert:** "Nicht blind übernehmen" ist jetzt als explizite
  Review-Regel dokumentiert (reproduzierbar, invariantensicher, WS-verankerbar).

### Offen (konkret als nächste Abarbeitung)

1. **P0-1 ausführen:** Datensatz-vs-Dev-Check als festen Prüfpunkt in jedem
   neuen QA-Befund mitführen.
2. **P1-1 ausführen:** Offene Vorschläge schrittweise in testbare
   Fallblöcke überführen (Setup/Erwartung/Ist/Status).
3. **WS-Patches gezielt nachziehen:** Nur Punkte in die 19 Wissensmodule
   übernehmen, die den Testblock bestanden haben.


## Update 2026-05-06 (Teil 2) — Trennlinie als QA-Pflichtgate

### Neu erledigt

- **P0-1 konkret umgesetzt:** `docs/testing.md` enthält jetzt ein
  verpflichtendes „Datensatz-vs-Dev“-Gate inkl. Copy/Paste-Template für neue
  Befunde.
- **Übernahmeregel operationalisiert:** QA-Befunde müssen jetzt explizit
  markieren, ob ein Punkt nur Dev/Tooling betrifft oder in WS gespiegelt werden
  muss.

### Offen (nächste Abarbeitung)

1. **P1-1 starten:** Für die Top-Driftpunkte aus dem Issue-Paket je einen
   Testfallblock mit `Setup/Erwartung/Ist/Status` anlegen.
2. **Drift-Bündelung nachziehen (P1-2):** Im nächsten Report-Update einen
   eigenen Sammelabschnitt „Drift mit WS-Auswirkung“ führen.
3. **WS-Patches nur nach Evidenz:** Erst Testfallblock, dann gezielter Patch in
   den 19 Wissensdateien + erneuter Smoke.

## Update 2026-05-06 (Teil 3) — Testfallblöcke & Drift-Bündelung gestartet

### Neu erledigt

- **P1-1 gestartet:** Offene Punkte aus dem Datensatztrennungs-Issue-Paket sind
  jetzt als reproduzierbare Testfallblöcke dokumentiert (`Setup/Erwartung/Ist/Status`
  inkl. Trennlinien-Check) in
  `docs/qa/datensatz-trennung-testfallbloecke-2026-05-06.md`.
- **P1-2 operationalisiert:** Ein eigener Sammelblick „Drift mit WS-Auswirkung“
  ist unten ergänzt, damit Laufzeitrelevanz nicht mehr zwischen Dev-Hinweisen
  untergeht.

### Drift mit WS-Auswirkung (Sammelstand)

1. **Unvollständige WS-Zielmarkierung in älteren Befunden**
   - Risiko: Regelhinweise bleiben im QA-Text hängen und werden nicht in den 19
     Wissensmodulen verankert.
   - Stand: Als FAIL-Testfall P1-1-T01 erfasst.
   - Nächste Aktion: Altbefunde mit betroffenen Zielmodulen nachannotieren.

2. **Upload-Vorschläge ohne Evidenzdruck**
   - Risiko: Übernahme von gut klingenden, aber unbestätigten Regeländerungen.
   - Stand: Als PASS-Regeltest P1-1-T03 formalisiert (Übernahme erst nach
     reproduzierbarem Nachweis).
   - Nächste Aktion: Beim nächsten WS-Patch Evidenzreferenz verpflichtend führen.

### Offen (nächste Abarbeitung)

1. **Altbefunde nachannotieren (P1-1-T01):** Für laufzeitrelevante QA-Dateien
   pro Befund Ziel-WS-Modul ergänzen.
2. **Erster evidenzbasierter WS-Patch:** Einen bestätigten Driftpunkt aus den
   Testfallblöcken in ein konkretes Wissensmodul überführen + Smoke.
3. **Drift-Sammelstand fortschreiben:** Abschnitt „Drift mit WS-Auswirkung“ in
   jedem weiteren Update aktualisieren (neu/erledigt/offen).

## Update 2026-05-06 (Teil 4) — Altbefunde nachannotiert

### Neu erledigt

- **P1-1-T01 (Teilfortschritt):** Laufzeitrelevante Altbefunde wurden mit dem
  Pflichtblock `Datensatz-vs-Dev-Check` nachannotiert:
  - `docs/qa/playtest-befund-chargen-save-gate.md`
  - `docs/qa/playtest-befund-w10-schwelle-halluzination.md`
- **Zielmodul-Disziplin erhöht:** Beide Befunde benennen jetzt explizit, in
  welche Wissensmodule ein möglicher Regelpatch gehört statt nur
  Fließtext-Hinweise zu liefern.

### Drift mit WS-Auswirkung (Sammelstand, aktualisiert)

1. **Unvollständige WS-Zielmarkierung in älteren Befunden**
   - Risiko: Regelhinweise bleiben im QA-Text hängen und werden nicht in den 19
     Wissensmodulen verankert.
   - Stand: **IN PROGRESS** (2 Altbefunde nachannotiert, Restscan offen).
   - Nächste Aktion: Weitere laufzeitnahe Befunde mit Pflichtblock ergänzen.

2. **Upload-Vorschläge ohne Evidenzdruck**
   - Risiko: Übernahme von gut klingenden, aber unbestätigten Regeländerungen.
   - Stand: **PASS-Regel aktiv** (kein Drift beobachtet).
   - Nächste Aktion: Beim ersten inhaltlichen WS-Patch die Evidenzreferenz
     weiterhin verpflichtend im Report führen.

### Offen (nächste Abarbeitung)

1. **Restscan P1-1-T01:** Weitere ältere QA-Befunde auf fehlenden
   Datensatz-vs-Dev-Block prüfen und nachannotieren.
2. **Erster evidenzbasierter WS-Patch:** Einen bestätigten Driftpunkt in
   ein WS-Modul überführen (inkl. Vorher/Nachher-Check + Smoke).


## Update 2026-05-06 (Teil 5) — Restscan fortgesetzt & weiterer Altbefund nachannotiert

### Neu erledigt

- **P1-1-T01 (weiterer Fortschritt):** Ein zusätzlicher laufzeitrelevanter
  Altbefund wurde mit dem Pflichtblock `Datensatz-vs-Dev-Check` ergänzt:
  - `docs/qa/playtest-befund-pvp-only-cashout.md`
- **WS-Zielpfad präzisiert:** Der Befund nennt jetzt explizit die
  Zielmodule für mögliche Runtime-Korrekturen (`speicher-fortsetzung`,
  `toolkit-gpt-spielleiter`, `kampagnenstruktur`, `masterprompt_v6`).

### Drift mit WS-Auswirkung (Sammelstand, aktualisiert)

1. **Unvollständige WS-Zielmarkierung in älteren Befunden**
   - Risiko: Regelhinweise bleiben im QA-Text hängen und werden nicht in den 19
     Wissensmodulen verankert.
   - Stand: **IN PROGRESS** (3 Altbefunde nachannotiert, Restscan weiter offen).
   - Nächste Aktion: Restliche laufzeitnahen QA-Befunde stichprobenbasiert
     prüfen und nur bei WS-Relevanz nachannotieren.

2. **Upload-Vorschläge ohne Evidenzdruck**
   - Risiko: Übernahme von gut klingenden, aber unbestätigten Regeländerungen.
   - Stand: **PASS-Regel aktiv** (kein Drift beobachtet).
   - Nächste Aktion: Beim ersten inhaltlichen WS-Patch Evidenzreferenz +
     Vorher/Nachher-Nachweis verbindlich dokumentieren.

### Offen (nächste Abarbeitung)

1. **Restscan P1-1-T01 abschließen:** Verbleibende ältere QA-Befunde mit
   Laufzeitbezug auf fehlenden Datensatz-vs-Dev-Block prüfen.
2. **Erster evidenzbasierter WS-Patch:** Einen bestätigten Driftpunkt mit
   minimalinvasivem Patch in ein konkretes WS-Modul überführen (inkl. Smoke).

## Update 2026-05-06 (Teil 6) — Restscan erweitert um Runtime-Verifikation

### Neu erledigt

- **P1-1-T01 (zusätzlicher Altbefund):** Ein weiterer laufzeitnaher QA-Befund
  wurde im Restscan nachgezogen und um den Pflichtblock
  `Datensatz-vs-Dev-Check` ergänzt:
  - `docs/qa/w10-schwelle-runtime-verifikation.md`
- **WS-Zielpfad konkretisiert:** Der Befund verweist nun explizit auf
  `meta/masterprompt_v6.md` sowie auf die betroffenen Runtime-Module
  `01_system/03_mechanik_proben.md` und `01_system/04_mechanik_kampf.md`.

### Drift mit WS-Auswirkung (Sammelstand, aktualisiert)

1. **Unvollständige WS-Zielmarkierung in älteren Befunden**
   - Risiko: Regelhinweise bleiben im QA-Text hängen und werden nicht in den 19
     Wissensmodulen verankert.
   - Stand: **IN PROGRESS** (4 Altbefunde nachannotiert, Restscan weiter offen).
   - Nächste Aktion: Stichprobe auf weitere laufzeitnahe Nicht-`playtest-befund`
     Dateien fortsetzen; nur bei echter WS-Relevanz Pflichtblock ergänzen.

2. **Upload-Vorschläge ohne Evidenzdruck**
   - Risiko: Übernahme von gut klingenden, aber unbestätigten Regeländerungen.
   - Stand: **PASS-Regel aktiv** (kein Drift beobachtet).
   - Nächste Aktion: Beim ersten inhaltlichen WS-Patch Evidenzreferenz +
     Vorher/Nachher-Nachweis verbindlich dokumentieren.

### Offen (nächste Abarbeitung)

1. **Restscan P1-1-T01 finalisieren:** Laufzeitnahe QA-Artefakte außerhalb der
   bisherigen Befundserie auf fehlenden Datensatz-vs-Dev-Block prüfen.
2. **Erster evidenzbasierter WS-Patch:** Bestätigten Driftpunkt aus den
   W10/Buff-Befunden minimalinvasiv ins Ziel-WS-Modul überführen (inkl. Smoke).

## Update 2026-05-06 (Teil 7) — Restscan auf statistische Buff-Verifikation erweitert

### Neu erledigt

- **P1-1-T01 (zusätzlicher Altbefund):** Ein weiteres laufzeitnahes
  QA-Artefakt wurde im Restscan nachgezogen und um den Pflichtblock
  `Datensatz-vs-Dev-Check` ergänzt:
  - `docs/qa/buff-schwelle-v2-verifikation.md`
- **WS-Zielpfad konsistent gemacht:** Der Befund verweist jetzt analog zu den
  übrigen W10/Buff-Befunden auf `meta/masterprompt_v6.md` sowie auf die
  Runtime-Module `01_system/03_mechanik_proben.md` und
  `01_system/04_mechanik_kampf.md`.

### Drift mit WS-Auswirkung (Sammelstand, aktualisiert)

1. **Unvollständige WS-Zielmarkierung in älteren Befunden**
   - Risiko: Regelhinweise bleiben im QA-Text hängen und werden nicht in den 19
     Wissensmodulen verankert.
   - Stand: **IN PROGRESS** (5 Altbefunde nachannotiert, Final-Check offen).
   - Nächste Aktion: Restliche laufzeitnahen QA-Dateien ohne unmittelbaren
     Regelbezug gegenprüfen und P1-1-T01 danach formell schließen.

2. **Upload-Vorschläge ohne Evidenzdruck**
   - Risiko: Übernahme von gut klingenden, aber unbestätigten Regeländerungen.
   - Stand: **PASS-Regel aktiv** (kein Drift beobachtet).
   - Nächste Aktion: Beim ersten inhaltlichen WS-Patch Evidenzreferenz +
     Vorher/Nachher-Nachweis verbindlich dokumentieren.

### Offen (nächste Abarbeitung)

1. **Restscan P1-1-T01 abschließen:** Nachannotierte Befundserie final gegen
   `docs/testing.md`-Gate prüfen und offenen Rest dokumentieren (falls vorhanden).
2. **Erster evidenzbasierter WS-Patch:** Bestätigten Driftpunkt aus
   `buff-schwelle-v2-verifikation`/`w10-schwelle-runtime-verifikation`
   minimalinvasiv ins Ziel-WS-Modul überführen (inkl. Smoke).


## Update 2026-05-06 (Teil 8) — Restscan um Critic-Selbstreview ergänzt

### Neu erledigt

- **P1-1-T01 (zusätzlicher Altbefund):** Der laufzeitnahe Review-Befund
  wurde im Restscan nachgezogen und um den Pflichtblock
  `Datensatz-vs-Dev-Check` ergänzt:
  - `docs/qa/buff-schwelle-critic-selbstreview.md`
- **WS-Zielpfad harmonisiert:** Der nachgezogene Befund verwendet nun
  denselben WS-Überführungspfad wie die übrigen W10/Buff-Artefakte
  (`meta/masterprompt_v6.md`, `01_system/03_mechanik_proben.md`,
  `01_system/04_mechanik_kampf.md`, optional `master-index.json`).

### Drift mit WS-Auswirkung (Sammelstand, aktualisiert)

1. **Unvollständige WS-Zielmarkierung in älteren Befunden**
   - Risiko: Regelhinweise bleiben im QA-Text hängen und werden nicht in den 19
     Wissensmodulen verankert.
   - Stand: **IN PROGRESS** (6 Altbefunde nachannotiert, Abschlussprüfung offen).
   - Nächste Aktion: Abschließende Gegenprobe gegen `docs/testing.md`-Gate;
     verbleibende Restdateien als "nicht laufzeitrelevant" oder "nachannotiert"
     explizit markieren und P1-1-T01 danach schließen.

2. **Upload-Vorschläge ohne Evidenzdruck**
   - Risiko: Übernahme von gut klingenden, aber unbestätigten Regeländerungen.
   - Stand: **PASS-Regel aktiv** (kein Drift beobachtet).
   - Nächste Aktion: Beim ersten inhaltlichen WS-Patch Evidenzreferenz +
     Vorher/Nachher-Nachweis verbindlich dokumentieren.

### Offen (nächste Abarbeitung)

1. **Restscan P1-1-T01 formell schließen:** Abschlussliste der geprüften
   Laufzeitbefunde inkl. "kein WS-Impact"-Markierungen dokumentieren.
2. **Erster evidenzbasierter WS-Patch:** Bestätigten Driftpunkt aus
   `buff-schwelle-v2-verifikation`/`w10-schwelle-runtime-verifikation`
   minimalinvasiv ins Ziel-WS-Modul überführen (inkl. `bash scripts/smoke.sh`).

## Update 2026-05-06 (Teil 9) — Restscan P1-1-T01 formell geschlossen

### Neu erledigt

- **P1-1-T01 Abschlussprüfung durchgeführt:** Der Restscan wurde gegen das
  verpflichtende `Datensatz-vs-Dev`-Gate aus `docs/testing.md` final
  gegengeprüft; alle laufzeitnahen Befunde der Serie sind nachannotiert.
- **Abschlussliste dokumentiert (laufzeitrelevant = nachannotiert):**
  - `docs/qa/playtest-befund-chargen-save-gate.md`
  - `docs/qa/playtest-befund-w10-schwelle-halluzination.md`
  - `docs/qa/playtest-befund-pvp-only-cashout.md`
  - `docs/qa/w10-schwelle-runtime-verifikation.md`
  - `docs/qa/buff-schwelle-v2-verifikation.md`
  - `docs/qa/buff-schwelle-critic-selbstreview.md`
- **Restdateien explizit als nicht-laufzeitrelevant markiert:**
  `docs/qa/accessibility-docs-nachcheck-2026-05-05.md`,
  `docs/qa/chronopolis-dynamik-arbeitsplan.md`,
  `docs/qa/chronopolis-regressionsmatrix.md`,
  `docs/qa/hud-kodex-patch-2026-05-04.md`,
  `docs/qa/pvp-bio-nachcheck-status.md`,
  `docs/qa/v7-bug-widerspruchs-checkliste-2026-04-30.md`,
  `docs/qa/tester-playtest-briefing.md` (Prozess/Plan/Briefing, kein
  unmittelbarer Regel- oder Runtime-Patchpfad).

### Drift mit WS-Auswirkung (Sammelstand, aktualisiert)

1. **Unvollständige WS-Zielmarkierung in älteren Befunden**
   - Risiko: Regelhinweise bleiben im QA-Text hängen und werden nicht in den 19
     Wissensmodulen verankert.
   - Stand: **CLOSED** (P1-1-T01 abgeschlossen; laufzeitnahe Altbefunde
     vollständig nachannotiert).
   - Nächste Aktion: Gate als Dauerstandard beibehalten; bei jedem neuen
     Laufzeitbefund Pflichtblock direkt im Erstentwurf setzen.

2. **Upload-Vorschläge ohne Evidenzdruck**
   - Risiko: Übernahme von gut klingenden, aber unbestätigten Regeländerungen.
   - Stand: **PASS-Regel aktiv** (kein Drift beobachtet).
   - Nächste Aktion: Beim ersten inhaltlichen WS-Patch Evidenzreferenz +
     Vorher/Nachher-Nachweis verbindlich dokumentieren.

### Offen (nächste Abarbeitung)

1. **P1-1-T02 vorbereiten:** Aus `buff-schwelle-v2-verifikation` und
   `w10-schwelle-runtime-verifikation` einen priorisierten
   Minimalpatch-Kandidaten wählen (ein Regelpunkt, ein Zielmodul).
2. **Erster evidenzbasierter WS-Patch:** Gewählten Driftpunkt minimalinvasiv in
   das Ziel-WS-Modul überführen (inkl. `bash scripts/smoke.sh`).
