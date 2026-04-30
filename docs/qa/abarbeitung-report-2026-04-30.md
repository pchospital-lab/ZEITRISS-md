# Abarbeitung Report (30.04.2026) — Save/Merge/Dispatcher

## Ziel

Dieses Dokument übersetzt den Nachcheck in eine anschlussfähige Arbeitsliste.
Fokus: **Masterprompt + Wissensdateien** als einziges Laufzeitsystem in der
Chatoberfläche (inkl. Split/Merge über mehrere parallele Chats).

## In diesem Schritt erledigt

- **SL-Referenz bereinigt:** Beispielblock und Erklärung auf
  `runtime_phase` umgestellt, damit kein persistenter `phase`-Anker für HQ-Saves
  impliziert wird.
- **HQ-Anker klargestellt:** In der gleichen Stelle explizit
  `continuity.last_seen.mode="hq"` und `continuity.last_seen.location="HQ"`
  als persistente Save-Route ergänzt.

## Offen (nächste Steps)

### P0 — Muss vor breitem Playtest

1. **Persistenzvertrag final harmonisieren**  
   Alle WS-Module auf dieselbe Trennung bringen:
   - persistent: Save-relevante Felder
   - runtime-only: Missions-/Queue-/Transfer-Zustände

2. **Chargen-Save-Gate regressionssicher**  
   Klassisch immer:
   Chargenabschluss → HQ-Heimkehrbeat → Save-Angebot → erst danach Briefing.

3. **`campaign.mode` strikt begrenzen**  
   Nur `mixed|preserve|trigger` als Persistenzstrategie;
   Missionsarten nicht als Kampagnenmodus persistieren.

### P1 — Unmittelbar danach

4. **5er-Split/Merge-Matrix als QA-Standard**  
   Fälle 4/1, 3/2, Resplit, Konfliktfälle, deterministische Thread-IDs.

5. **Seed-Cap/Overflow beweisen**  
   Merge >12 Seeds mit erwartetem Overflow-Logging (Trace + Flags).

6. **Arena-/Rift-Transferhygiene**  
   Kein persistenter Auto-Rejoin-Drift; HQ-only Savepfad und Wallet-Trennung
   in Negativtests sichern.

### P2 — Nach Stabilisierung

7. **Chronopolis-Qualitätspass**  
   Spawn-Prioritäten, shared/roster echoes, Beat-Loop-Varianz dokumentiert
   testen.

## Übergabeformat für den nächsten Step

Der nächste Bearbeitungsschritt sollte immer:

1. diese Datei aktualisieren (Was erledigt / Was offen),
2. die betroffenen Wissensmodule synchron ändern,
3. `bash scripts/smoke.sh` laufen lassen,
4. bei QA-relevanten Änderungen die betroffenen Fixture-Dateien benennen.
