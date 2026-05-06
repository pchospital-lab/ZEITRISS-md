# Datensatztrennung — Testfallblöcke (Start, 2026-05-06)

Ziel: Offene Punkte aus dem Issue-Paket in reproduzierbare QA-Blöcke überführen,
nicht als Fließtext-Hypothesen. Dieses Dokument ist die Arbeitsgrundlage für
die nächste WS-nahe Patchrunde.

## P1-1-T01 — Trennlinie bei Regelbefund (WS-pflichtig)

## Datensatz-vs-Dev-Check

- Datensatz-Relevanz: ja — Regelwirkung in Laufzeitantworten.
- Nur Dev/QA: nein.
- WS-Spiegelpflicht: ja — Zielmodule nach Evidenz festlegen (voraussichtlich `core/sl-referenz.md` plus betroffene Runtime-Module).
- Invarianten betroffen: nein (wird pro Einzelpatch erneut gegengeprüft).

- Setup: Einen vorhandenen Regelbefund aus `docs/qa/playtest-befund-*.md` wählen,
  der eine Laufzeitwirkung beschreibt.
- Erwartung: Befund enthält klaren Zielhinweis für WS-Spiegelung (Modul + Feld/Abschnitt).
- Ist: In älteren Befunden teils nur allgemeine Formulierung ohne Zielmodul.
- Status: FAIL.
- Nächste Aktion: Bei jedem betroffenen Altbefund Nachtrag mit Zielmodul ergänzen;
  neue Befunde nur mit vollständigem Trennlinienblock aufnehmen.

## P1-1-T02 — Dev-only Hinweis korrekt entkoppelt

## Datensatz-vs-Dev-Check

- Datensatz-Relevanz: nein — betrifft nur Test-Harness/Prozess.
- Nur Dev/QA: ja — `docs/testing.md` und externe Harness-Scripts.
- WS-Spiegelpflicht: nein.
- Invarianten betroffen: nein.

- Setup: Einen bekannten Harness-Hinweis (Port-Migration/Env-Thema) prüfen.
- Erwartung: Befund wird als Dev-only geführt, ohne Runtime-Buglabel.
- Ist: Im Guide bereits als offener Fix markiert; keine WS-Forderung.
- Status: PASS.
- Nächste Aktion: Bei neuen Harness-Problemen strikt Dev-only kennzeichnen.

## P1-2-T01 — Drift-Bündelung mit WS-Auswirkung im Report

## Datensatz-vs-Dev-Check

- Datensatz-Relevanz: ja — nur Driftpunkte mit möglicher Laufzeitwirkung.
- Nur Dev/QA: teilweise — Dev-Hinweise bleiben getrennt.
- WS-Spiegelpflicht: ja, falls Drift bestätigt und invariantensicher patchbar.
- Invarianten betroffen: aktuell nein (nur Dokumentations-/Strukturarbeit).

- Setup: Aktuellen Abarbeitungs-Report um einen dedizierten Drift-Abschnitt erweitern.
- Erwartung: Driftpunkte sind gebündelt, priorisiert und mit nächster Aktion versehen.
- Ist: Vorher nur verteilt in Abschnitten „Offen“/Einzelupdates.
- Status: PASS (mit heutigem Report-Update).
- Nächste Aktion: Abschnitt pro Folge-Update fortschreiben, Einträge bei Erledigung abhaken.

## P1-1-T03 — Upload-Vorschläge nur nach Evidenz übernehmen

## Datensatz-vs-Dev-Check

- Datensatz-Relevanz: ja, wenn Vorschlag Regeländerung fordert.
- Nur Dev/QA: nein.
- WS-Spiegelpflicht: ja, aber erst nach bestandenem Testblock.
- Invarianten betroffen: potenziell ja; daher Vorab-Check Pflicht.

- Setup: Einen Vorschlag aus `uploads/` gegen bestehende QA-Evidenz spiegeln.
- Erwartung: Ohne reproduzierbaren Nachweis keine WS-Änderung.
- Ist: Regel bereits im Issue-Paket formuliert, aber noch nicht als Testfall dokumentiert gewesen.
- Status: PASS (Regel jetzt testfallbasiert festgehalten).
- Nächste Aktion: Für den ersten WS-Patch explizit Evidenzreferenz in Commit/Report angeben.
