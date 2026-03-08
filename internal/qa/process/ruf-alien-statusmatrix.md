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


## Follow-up-Hinweis

- **Durchlauf 58 (2026-03-08):** Restdrift im `core/spieler-handbuch.md`
  geschlossen (Debrief-Label auf **ITI-Ruf**, Tier V im Cheatsheet auf
  **5.000 CU** + Klartext zu kaufbaren Regulärpfaden ab Ruf +5).
- **Durchlauf 59 (2026-03-08):** Watchpoint-Lauf auf Referenzstellen
  abgeschlossen: Rufbegriffe in `gameplay/kampagnenuebersicht.md` und
  `core/sl-referenz.md` auf SSOT (`ITI-Ruf`/Fraktionssignal) gehärtet sowie
  Mystery-Tonlage in `core/zeitriss-core.md` ohne harten Alien-Fakt nachgezogen.

## Verknüpfung

- Fahrplan (Initiallauf): `internal/qa/plans/issue-pack-durchlauf-57-ruf-alien.md`
- Log (Initiallauf): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-57-ruf-alien.md`
- Fahrplan (Follow-up): `internal/qa/plans/issue-pack-durchlauf-58-ruf-alien-followup.md`
- Log (Follow-up): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-58-ruf-alien-followup.md`
- Fahrplan (Watchpoints): `internal/qa/plans/issue-pack-durchlauf-59-ruf-alien-watchpoints.md`
- Log (Watchpoints): `internal/qa/logs/2026-03-08-issue-pack-durchlauf-59-ruf-alien-watchpoints.md`
- Prozessanker: `internal/qa/process/known-issues.md` (ZR-018)
