---
title: "ZR-018 Statusmatrix – Ruf/Tier + Alien/Mystery"
version: 0.1.0
tags: [qa, process]
---

# ZR-018 Statusmatrix – Ruf/Tier + Alien/Mystery

Ziel: Die Punkte aus `uploads/ZEITRISS_ruf_alien_review.md` pro Issue
anschlussfähig dokumentieren.

## Legende

- **abgeschlossen:** im Repo umgesetzt und im Pflicht-Smoke mitgeprüft.
- **teilweise:** Kern umgesetzt, Feinschliff für Folge-Durchlauf offen.

## Status je Review-Issue

| Review-Issue | Kurzname | Status | Kernentscheidung | Evidenz |
| --- | --- | --- | --- | --- |
| 1 | ITI-Ruf vs. Fraktionsruf trennen | abgeschlossen | `reputation.iti` als operativer Lizenz-/Rangpfad, Fraktionsruf nur narrativ/politisch; kein Hard-Link mehr. | Durchlauf 57 |
| 2 | Boss-basierter ITI-Rufpfad | abgeschlossen | Start 0; +1 nach erster Core-Mission; +1 bei Core-Boss in M5/M10/M15/M20; Cap 5. | Durchlauf 57 |
| 3 | Tier-V-Logik | abgeschlossen | Tier V ist kaufbare Lizenz (Ruf +5, 5.000 CU), keine globale Quest-only-Sperre. | Durchlauf 57 |
| 4 | Rangnamen kanonisieren | abgeschlossen | Feste Mapping-Tabelle Ruf 0–5 → Rekrut/Operator I/Feldagent/Senior-Feldagent/Elitechrononaut/Apex-Agent. | Durchlauf 57 |
| 5 | Level-10 vs. Lizenz-Tier trennen | abgeschlossen | Level 10 = Chronopolis/Vertrauen; Shop-/Lizenzzugriff über ITI-Ruf + Tier. | Durchlauf 57 |
| 6 | Onboarding ohne harten Alien-Fakt | abgeschlossen | Einleitung auf Gerücht-/Aktenlogik umgestellt; keine bestätigte „galaktische Föderation“ im Frühtext. | Durchlauf 57 |
| 7 | Mystery-Contract explizit | abgeschlossen | Mystery-Contract-Kasten in Spieler-/Kampagnenkontext ergänzt. | Durchlauf 57 |
| 8 | Graue/Greys vereinheitlichen | abgeschlossen | Graue/Greys als Incident-/Deckname statt gesicherter Spezies geführt. | Durchlauf 57 |

## Watchpoints für Folge-Durchläufe

1. **Debrief-Disziplin:** Score-Screens immer als `ITI-Ruf` labeln, nie nur „Ruf“.
2. **Rangnamen-Konsistenz:** Keine alternativen Titel für dieselbe ITI-Rufstufe einführen.
3. **Tier-V-Rückfall verhindern:** Sonderfreigaben immer objektbezogen formulieren,
   nicht als globales Tier-V-Verbot.
4. **Onboarding-Ton halten:** Frühe Spielertexte bei UFO/Greys stets als Spur,
   Dossier oder Feldjargon formulieren.
5. **Debrief/HQ-SSOT halten:** In Ablauftexten und Tabellen immer `ITI-Ruf-Update`
   sowie den formalen `reputation.iti`-Pfad für Freigaben verwenden.
6. **Smoke-Guard aktiv halten:** `tools/test_ruf_alien_watchguard.js` bleibt im
   Pflicht-Smoke und wird bei neuen Textmodulen bei Bedarf um präzise
   Negativ-/Positivmuster ergänzt.

## Monitoring-Rhythmus (ZR-018)

- **Trigger:** Bei Änderungen an Onboarding-, Kampagnen-, Charakter- oder
  Generatortexten mit Ruf/Tier/Mystery-Bezug.
- **Pflicht:** Watchguard-Muster auf neue/angepasste Formulierungen prüfen und
  bei Bedarf erweitern.
- **Nachweis:** Jeder Anschlusslauf erhält Plan + Log + Eintrag in dieser
  Statusmatrix inkl. Verlinkung im Prozessanker `known-issues.md`.


## Follow-up-Hinweis

- **Durchlauf 58 (2026-03-08):** Restdrift im `core/spieler-handbuch.md`
  geschlossen (Debrief-Label auf **ITI-Ruf**, Tier V im Cheatsheet auf
  **5.000 CU** + Klartext zu kaufbaren Regulärpfaden ab Ruf +5).
- **Durchlauf 59 (2026-03-08):** Watchpoint-Lauf auf Referenzstellen
  abgeschlossen: Rufbegriffe in `gameplay/kampagnenuebersicht.md` und
  `core/sl-referenz.md` auf SSOT (`ITI-Ruf`/Fraktionssignal) gehärtet sowie
  Mystery-Tonlage in `core/zeitriss-core.md` ohne harten Alien-Fakt nachgezogen.
- **Durchlauf 60 (2026-03-08):** Restdrift im Beispielpfad
  `gameplay/kampagnenstruktur.md` geschlossen: hartes Alien-Wording auf
  Feldread-Formulierung (`scheinbar "Alien"-Raptoren` als zeitversetzte
  Fauna) umgestellt, damit die Onboarding-Tonlage auch in Missionsbeispielen
  konsistent bleibt.
- **Durchlauf 61 (2026-03-08):** Watchpoint-Wording in Randmodulen
  nachgezogen: Ausrüstungs-Hinweistext in
  `characters/ausruestung-cyberware.md` auf formalen
  `ITI-Ruf`/`Lizenz-Tier`-Pfad gehärtet und `Greys` im
  Urban-Myth-Generator (`gameplay/kreative-generatoren-begegnungen.md`)
  explizit als `ITI-Deckname` markiert, um Falschspur-Lesart stabil zu
  halten.
- **Durchlauf 62 (2026-03-08):** Reviewer-Feedback auf Grey-Logik
  eingearbeitet: Urban-Myth-Eintrag in
  `gameplay/kreative-generatoren-begegnungen.md` von Nano-Anzug-/ITI-Only
  auf posthumane Fernzukunfts-Herkunft (jenseits T-/N-Stufe) mit möglichen
  externen Zeitmanipulator-Fraktionen korrigiert; flankierend in
  `gameplay/kampagnenuebersicht.md` die Gegnerklarheit (`ITI` vs. externe
  Zeitmanipulatoren) explizit gehalten.
- **Durchlauf 63 (2026-03-08):** Restdrift in
  `gameplay/kampagnenstruktur.md` geschlossen: Debrief-Autoscreen auf
  `ITI-Ruf-Update` vereinheitlicht und HQ-/Lizenzfreigaben klar als formalen
  `reputation.iti`-Pfad getrennt von Fraktionsruf (politisches Signal)
  dokumentiert.
- **Durchlauf 64 (2026-03-08):** Chronopolis-Wegführung als
  Schlauchlevel explizit verankert (`Eingangsschleuse -> Ringlauf ->
  gegenüberliegende Ausgangsschleuse`) in `core/sl-referenz.md` und
  `gameplay/kampagnenstruktur.md`; zusätzlich `core/zeitriss-core.md` bei
  Level-10-Meilenstein auf Verantwortung + Chronopolis-Schlüssel gehärtet
  und Shop-/Lizenzfreigaben weiter auf `ITI-Ruf + Lizenz-Tier` fixiert.
- **Durchlauf 65 (2026-03-08):** Watchpoints als leichter Smoke-Guard
  verstetigt (`tools/test_ruf_alien_watchguard.js` in `scripts/smoke.sh`):
  Debrief-Disziplin (`ITI-Ruf-Update`), Tier-V-Rückfallblocker und
  Onboarding-Ton-Guard gegen harte Alien-Faktbehauptungen.
- **Durchlauf 66 (2026-03-08):** Restdrift im Gating-Wording in
  `characters/charaktererschaffung-grundlagen.md` und
  `characters/ausruestung-cyberware.md` geschlossen: Mischbegriff
  `Dienstgrad/Ruf` entfernt, Shop-Tier-Restabschnitt auf formalen
  `ITI-Ruf + Lizenz-Tier`-Pfad (Level nur Build-Fortschritt) gehärtet;
  Watchguard in `tools/test_ruf_alien_watchguard.js` um entsprechende
  Rückfallmuster erweitert.

- **Durchlauf 67 (2026-03-08):** Restdrift im Chronopolis-Gating in
  `gameplay/kampagnenuebersicht.md` geschlossen: Mischbegriff
  `ITI-Rang/ITI-Ruf` entfernt, formales Gating auf `reputation.iti`
  präzisiert und Kernbereichs-Zugang auf höheren ITI-Ruf gehärtet;
  Watchguard in `tools/test_ruf_alien_watchguard.js` um das
  Rückfallmuster `ITI-Rang/ITI-Ruf` erweitert.

- **Durchlauf 68 (2026-03-08):** Rangnamen-Konsistenz im
  `core/spieler-handbuch.md` nachgezogen: kanonisches ITI-Rang-Mapping
  (Ruf 0–5) und Debrief-Format (`Rang … · ITI-Ruf … · Lizenz Tier …`)
  explizit ergänzt; Watchguard in `tools/test_ruf_alien_watchguard.js`
  um Positiv-Check für das Handbuch-Debrief-Format erweitert.

- **Durchlauf 69 (2026-03-08):** Monitoring-Standard explizit ergänzt und
  Guard-Abdeckung verbreitert: `tools/test_ruf_alien_watchguard.js` prüft nun
  zusätzlich den Reveal-Pfad im Kernmodul (`es gibt keine Aliens, nur ...`)
  sowie den kanonischen `Greys - posthumane Fernzukunfts-Menschen`-Eintrag in
  `gameplay/kreative-generatoren-begegnungen.md`.

- **Durchlauf 70 (2026-03-08):** Abschlusscheck auf v7-SSOT +
  Wissensspeicher-Linkhygiene durchgeführt: Pflicht-Smoke erneut grün,
  lokale Außenverweise aus WS-Texten entfernt (`core/sl-referenz.md`,
  `core/spieler-handbuch.md`, `systems/gameflow/speicher-fortsetzung.md`)
  und ein fehlerhafter relativer Modul-Link in
  `gameplay/kampagnenstruktur.md` korrigiert.

- **Durchlauf 71 (2026-03-08):** Follow-up auf den Abschlusscheck: die
  V6→V7-Migrationsreferenz wurde direkt im Wissensspeicher verankert
  (`systems/gameflow/speicher-fortsetzung.md`, neuer Anker
  `#v6-v7-migrationsbeispiel-im-wissensspeicher`) und die
  `core/sl-referenz.md` auf diesen internen WS-Pfad umgestellt.

- **Durchlauf 72 (2026-03-08):** Allgemeiner Abschlusscheck auf v7/Format/
  Links durchgeführt: Pflicht-Smoke grün, Linklint grün, zusätzlicher
  WS-Linkscope-Guard ohne Außenverweise (`ws-internal-link-guard-ok`);
  Zeilenlängen-Scan als nicht-blockierender QA-Befund dokumentiert.

- **Durchlauf 73 (2026-03-08):** Round-4-SSOT-Harmonisierung umgesetzt:
  Voice-Default repoweit auf `gm_second_person` ausgerichtet
  (Masterprompt/Toolkit/Save-Doku), Save-v7-Persistenzkonflikt
  (`SYS_runtime`/`SYS_used`/`cooldowns`) bereinigt, Px-Optionalität
  (Merge-Schalter/Jitter/Halbzählung) in `gameplay/kampagnenstruktur.md`
  entfernt, Toolkit-Tierpfad auf `reputation.iti` korrigiert,
  Absolut-Framing in frühen Spielertexten als ITI-Arbeitsbegriff ergänzt sowie
  Signaturtell + Forensik-Dreieck als regelnahe Payoff-Module ergänzt.


## Verknüpfung

- Fahrplan (Initiallauf): `internal/qa/plans/issue-pack-durchlauf-57-ruf-alien.md`
- Log (Initiallauf): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-57-ruf-alien.md`
- Fahrplan (Follow-up): `internal/qa/plans/issue-pack-durchlauf-58-ruf-alien-followup.md`
- Log (Follow-up): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-58-ruf-alien-followup.md`
- Fahrplan (Watchpoints): `internal/qa/plans/issue-pack-durchlauf-59-ruf-alien-watchpoints.md`
- Log (Watchpoints): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-59-ruf-alien-watchpoints.md`
- Fahrplan (Restdrift): `internal/qa/plans/issue-pack-durchlauf-60-ruf-alien-restdrift.md`
- Log (Restdrift): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-60-ruf-alien-restdrift.md`
- Fahrplan (Watchpoints II): `internal/qa/plans/issue-pack-durchlauf-61-ruf-alien-watchpoints-ii.md`
- Log (Watchpoints II): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-61-ruf-alien-watchpoints-ii.md`
- Fahrplan (Greys/Feindbild): `internal/qa/plans/issue-pack-durchlauf-62-ruf-alien-greys-feindbild.md`
- Log (Greys/Feindbild): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-62-ruf-alien-greys-feindbild.md`
- Fahrplan (Debrief/HQ-SSOT): `internal/qa/plans/issue-pack-durchlauf-63-ruf-alien-debrief-hq-ssot.md`
- Log (Debrief/HQ-SSOT): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-63-ruf-alien-debrief-hq-ssot.md`
- Fahrplan (Chronopolis-Schlauchlevel): `internal/qa/plans/issue-pack-durchlauf-64-ruf-alien-chronopolis-schlauchlevel.md`
- Log (Chronopolis-Schlauchlevel): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-64-ruf-alien-chronopolis-schlauchlevel.md`
- Fahrplan (Watchguard): `internal/qa/plans/issue-pack-durchlauf-65-ruf-alien-watchguard.md`
- Log (Watchguard): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-65-ruf-alien-watchguard.md`
- Prozessanker: `internal/qa/process/known-issues.md` (ZR-018)

- Fahrplan (Gating-Restdrift): `internal/qa/plans/issue-pack-durchlauf-66-ruf-alien-gating-restdrift.md`
- Log (Gating-Restdrift): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-66-ruf-alien-gating-restdrift.md`

- Fahrplan (Chronopolis-Rufklarheit): `internal/qa/plans/issue-pack-durchlauf-67-ruf-alien-chronopolis-rufklarheit.md`
- Log (Chronopolis-Rufklarheit): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-67-ruf-alien-chronopolis-rufklarheit.md`

- Fahrplan (Rang-Mapping Handbuch): `internal/qa/plans/issue-pack-durchlauf-68-ruf-alien-rangmapping-handbuch.md`
- Log (Rang-Mapping Handbuch): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-68-ruf-alien-rangmapping-handbuch.md`

- Fahrplan (Monitoring + Guard-Härtung): `internal/qa/plans/issue-pack-durchlauf-69-ruf-alien-monitoring-guard.md`
- Log (Monitoring + Guard-Härtung): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-69-ruf-alien-monitoring-guard.md`

- Fahrplan (Abschlusscheck v7 + Linkhygiene): `internal/qa/plans/issue-pack-durchlauf-70-abschlusscheck-v7-links.md`
- Log (Abschlusscheck v7 + Linkhygiene): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-70-abschlusscheck-v7-links.md`

- Fahrplan (V6-Migrationsreferenz im Wissensspeicher): `internal/qa/plans/issue-pack-durchlauf-71-v6-migrationsreferenz-ws.md`
- Log (V6-Migrationsreferenz im Wissensspeicher): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-71-v6-migrationsreferenz-ws.md`

- Fahrplan (Abschlusscheck v7/Format/Links): `internal/qa/plans/issue-pack-durchlauf-72-abschlusscheck-v7-format-links.md`
- Log (Abschlusscheck v7/Format/Links): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-72-abschlusscheck-v7-format-links.md`


- Fahrplan (Round4 SSOT-Harmonisierung): `internal/qa/plans/issue-pack-durchlauf-73-round4-ssot-harmonisierung.md`
- Log (Round4 SSOT-Harmonisierung): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-73-round4-ssot-harmonisierung.md`

- **Durchlauf 74 (2026-03-08):** Abschluss-Restdrift aus Round-4 nachgezogen: `core/zeitriss-core.md` v7-UI-Default auf `gm_second_person` harmonisiert und `systems/toolkit-gpt-spielleiter.md` beim Dispatcher-Semver-Hinweis auf kanonisches `zr` mit Legacy-Normalisierung (`zr_version`) geschärft; Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Round4 Abschluss-Restdrift): `internal/qa/plans/issue-pack-durchlauf-74-round4-abschluss-restdrift.md`
- Log (Round4 Abschluss-Restdrift): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-74-round4-abschluss-restdrift.md`

- **Durchlauf 75 (2026-03-08):** Round-4-Restklarheit nachgezogen: `core/sl-referenz.md` Persistenz-Bullet auf kanonische `characters[]`-Felder geschärft (Legacy-`character{}` nur als Import-Normalisierung), `systems/gameflow/speicher-fortsetzung.md` Legacy-HQ-Block explizit als nicht-kanonischen Neu-Export markiert und `gameplay/kampagnenstruktur.md` beim Chronopolis-Entry auf einmaligen In-World-Warnhinweis statt Warn-Cutscene harmonisiert; Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Round4 Restklarheit Save/Chronopolis): `internal/qa/plans/issue-pack-durchlauf-75-round4-restklarheit-save-chronopolis.md`
- Log (Round4 Restklarheit Save/Chronopolis): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-75-round4-restklarheit-save-chronopolis.md`

- **Durchlauf 76 (2026-03-08):** HQ-Save/Reset-Klarstellung über die drei SSOT-Orte gezogen: `meta/masterprompt_v6.md`, `core/sl-referenz.md` und `systems/gameflow/speicher-fortsetzung.md` benennen jetzt explizit die Invariante „Speichern nur im HQ; Debrief-Reset von `stress`/`psi_heat`/`SYS` vor Save“, inklusive Begründung, warum `stress`/`psi_heat` trotz Reset im v7-Schema verbleiben (expliziter HQ-Status + stabile Legacy-/Import-Normalisierung). Pflicht-Smoke erneut grün.

- Fahrplan (HQ-Save/Reset Klarheit): `internal/qa/plans/issue-pack-durchlauf-76-hq-save-reset-clarity.md`
- Log (HQ-Save/Reset Klarheit): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-76-hq-save-reset-clarity.md`

- **Durchlauf 77 (2026-03-08):** Round-4-Anschlusslauf in `systems/gameflow/speicher-fortsetzung.md` durchgeführt: Chronopolis-Makrotext auf einmaligen In-World-Warnhinweis (statt Warn-Popup) harmonisiert und SaveGuard-Hinweis um die klare Einordnung als Runtime-/Legacy-Bridge vor v7-Normalisierung ergänzt (kein kanonischer Neu-Export). Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Round4 Anschluss Chronopolis/Bridge): `internal/qa/plans/issue-pack-durchlauf-77-round4-anschluss-chronopolis-bridge.md`
- Log (Round4 Anschluss Chronopolis/Bridge): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-77-round4-anschluss-chronopolis-bridge.md`

- **Durchlauf 78 (2026-03-08):** Round-4-Anschlusslauf für den Mystery-Contract abgeschlossen: In `gameplay/kampagnenuebersicht.md` wurde der Signatursatz ergänzt ("Was im ersten Zugriff wie Fremdheit wirkt ... menschliche Zukunft"), um den gewünschten Aha-Pfad (Fremdheit → menschliche Fernzukunft) als Leitplanke explizit zu verankern; Pflicht-Smoke + Linklint erneut grün.

- Fahrplan (Round4 Mystery-Signatursatz): `internal/qa/plans/issue-pack-durchlauf-78-round4-signatursatz-mystery-bridge.md`
- Log (Round4 Mystery-Signatursatz): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-78-round4-signatursatz-mystery-bridge.md`

