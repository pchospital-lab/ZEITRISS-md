# Issue-Paket (Start) — Datensatztrennung & QA-Fokus

**Datum:** 2026-05-06  
**Auslöser:** Nachcheck auf Vermischung von Laufzeit-Datensatz (Masterprompt + 19 Wissensdateien) mit Dev-/Testartefakten.  
**Ziel:** Saubere, priorisierte Abarbeitung mit klarer Fundstelle pro Thema.

## Leitplanken

- ZEITRISS-Laufzeit = **nur** Masterprompt + 19 Wissensdateien.
- `docs/`, `internal/`, `meta/archive/`, `runtime.js`, `tools/` sind Dev-/QA-Kontext.
- Regeländerungen gelten erst als "echt", wenn sie in den Wissensdateien verankert sind.

## Priorisierte Issues

## P0 — Muss zuerst

### P0-1: Datensatz/Dev-Trennlinie als Checkliste im QA-Flow verankern

**Problem:** In Reviews werden Befunde teils korrekt erkannt, aber nicht immer als "WS-pflichtig" nachgezogen.  
**Fix-Ansatz:** In QA-Dokumenten explizit prüfen, ob ein Befund nur Dev-Dateien betrifft oder in WS gespiegelt werden muss.  
**Fundstellen:** `AGENTS.md`, `docs/testing.md`, `docs/qa/abarbeitung-report-2026-04-30.md`.

### P0-2: "Issue-Paket" aus Uploads in repo-nahe, wartbare QA-Struktur überführen

**Problem:** Große Vorschlagspakete liegen in `uploads/` und sind dadurch für die laufende Abarbeitung schwer versionierbar.  
**Fix-Ansatz:** Relevante Punkte als priorisierte Tickets (P0/P1/P2) in `docs/qa/` pflegen; Upload bleibt nur Referenzquelle.  
**Fundstellen:** `uploads/ZEITRISS_agentenpaket_nachcheck.md`, `uploads/Spielstand speichern und laden.pdf`.

## P1 — Direkt danach

### P1-1: Offene fachliche Punkte in Testfallblöcke statt Fließtext zerlegen

**Problem:** Gute Vorschläge enthalten teils Mischungen aus Problem, Lösung und Hypothese.  
**Fix-Ansatz:** Jeden offenen Punkt als testbaren Block führen: Setup, Erwartung, Ist, Status, nächste Aktion.

### P1-2: Drift-Warnungen bündeln (nur mit WS-Relevanz)

**Problem:** Einzelhinweise sind verteilt über mehrere QA-Dateien.  
**Fix-Ansatz:** Sammelabschnitt "Drift mit WS-Auswirkung" pro Report-Update.

## P2 — Nach Stabilisierung

### P2-1: Archiv-/Upload-Hygiene

**Problem:** Historische Pakete sind wertvoll, aber ohne Querverweis schwer auffindbar.  
**Fix-Ansatz:** Kurze Indexliste in QA, welche Upload-Datei welchen Schwerpunkt abdeckt.

## Nicht blind übernehmen (Review-Prinzip)

- Upload-Vorschläge sind **Input, nicht SSOT**.
- Übernahme nur, wenn:
  1. der Punkt reproduzierbar/testbar ist,
  2. keine Invarianten bricht,
  3. in den Wissensdateien sauber verankerbar ist.

## Nächste konkrete Schritte

1. Dieses Issue-Paket als Startliste in den QA-Report eintragen.
2. Pro P0/P1-Punkt einen Testfallblock nach `docs/testing.md`-Artefaktpflicht führen.
3. Erst danach gezielte WS-Patches vornehmen (nicht pauschal aus Upload kopieren).
