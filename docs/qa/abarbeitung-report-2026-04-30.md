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

## Offen (nächste Steps)

### P0 — Muss vor breitem Playtest

1. **Chargen-Save-Gate regressionssicher**  
   Klassisch immer:
   Chargenabschluss → HQ-Heimkehrbeat → Save-Angebot → erst danach Briefing.

2. **Persistenzvertrag repo-weit spiegeln (Rest-Scan)**  
   Kernmodule sind harmonisiert (`core/sl-referenz.md`,
   `gameplay/kampagnenstruktur.md`,
   `systems/toolkit-gpt-spielleiter.md`,
   `systems/gameflow/speicher-fortsetzung.md`). Offen ist nur noch ein
   finaler Rest-Scan auf Altbegriffe in ergänzenden QA-/Arbeitsdokumenten.

### P1 — Unmittelbar danach

3. **5er-Split/Merge-Matrix als QA-Standard**  
   Fälle 4/1, 3/2, Resplit, Konfliktfälle, deterministische Thread-IDs.

4. **Seed-Cap/Overflow beweisen**  
   Merge >12 Seeds mit erwartetem Overflow-Logging (Trace + Flags).

5. **Arena-/Rift-Transferhygiene**  
   Kein persistenter Auto-Rejoin-Drift; HQ-only Savepfad und Wallet-Trennung
   in Negativtests sichern.

### P2 — Nach Stabilisierung

6. **Chronopolis-Qualitätspass**  
   Spawn-Prioritäten, shared/roster echoes, Beat-Loop-Varianz dokumentiert
   testen.

## Übergabeformat für den nächsten Step

Der nächste Bearbeitungsschritt sollte immer:

1. diese Datei aktualisieren (Was erledigt / Was offen),
2. die betroffenen Wissensmodule synchron ändern,
3. `bash scripts/smoke.sh` laufen lassen,
4. bei QA-relevanten Änderungen die betroffenen Fixture-Dateien benennen.
