---
title: "Known Issues & Triage-Prozess"
version: 1.1.0
tags: [meta, qa]
---

# Known Issues & Triage-Prozess

Diese Seite bündelt den Prozess für offene QA-Funde, die nicht direkt im
Runtime-Content gelöst werden (z. B. Tooling-, Workflow- oder Plattformfragen).

## Ziel

- Einheitlicher Ort für Triagestatus (`neu`, `geprüft`, `geplant`,
  `in Umsetzung`, `abgeschlossen`, `verworfen`).
- Klare Verlinkung zwischen Eingangsquelle, Fahrplan, Log und Umsetzung.
- Saubere Trennung zwischen Runtime-Änderungen und Meta-Prozessarbeit.

## Prozess (leichtgewichtig)

1. **Erfassen**
   - Issue im QA-Log benennen und mit Quelle verlinken (Upload, Playtest,
     Audit, Maintainer-Report).
2. **Triagieren**
   - Priorität (`P0`–`P3`), Scope (Runtime/Meta/Tooling) und Besitzer:in
     festlegen.
3. **Planen**
   - Falls umsetzungsrelevant: Ticket in den Fahrplan (`internal/qa/plans/`)
     aufnehmen.
4. **Umsetzen**
   - Änderungen im Repo durchführen, Pflichtprüfungen laufen lassen,
     Commit/PR mit Referenz auf den QA-Eintrag versehen.
5. **Abschließen**
   - Status in dieser Liste, im QA-Log und im Fahrplan synchron auf
     `abgeschlossen` oder `verworfen` setzen.

## Aktuelle Known Issues

| ID | Titel | Quelle | Priorität | Scope | Status | Notiz |
| --- | --- | --- | --- | --- | --- | --- |
| ZR-015 | Interne QA-Known-Issues in GitHub-Issue-Triage spiegeln | `uploads/deep-research-report(4).md` | P3 | Meta/Prozess | abgeschlossen | Diese Prozessseite bleibt der kanonische Triage-Einstieg. |
| ZR-016 | Externer Codex-Issue-Pack in iterative Fahrplan-Cluster überführen | `uploads/ZEITRISS_codex_issue_pack.md` | P0 | Runtime/QA | abgeschlossen | Primärindex: `internal/qa/process/issue-pack-statusmatrix.md`; Durchläufe bis 38 abgeschlossen. |
| ZR-017 | Save/Load v7 und OpenWebUI-Standardpfad aus dem neuen Issue-Pack nachziehen | `uploads/ZEITRISS_v7_save_load_issue_pack.md` | P0 | Runtime/QA | abgeschlossen | Detail- und Anschlussstand in `internal/qa/process/v7-save-load-statusmatrix.md`. |
| ZR-018 | Ruf/Tier-Progress und Alien/Mystery-Onboarding als SSOT nachziehen | `uploads/ZEITRISS_ruf_alien_review.md` | P0 | Runtime/QA | abgeschlossen | Detailstand in `internal/qa/process/ruf-alien-statusmatrix.md`. |
| ZR-021 | Post-139 Onboarding-Hardening fortführen | `uploads/ZEITRISS_start_mmo_onboarding_review.md` | P1 | Runtime/QA + Meta/Prozess | abgeschlossen | Hard-Final-Review-Anschlussdurchläufe 140–179 erledigt; Detailhistorie 157–179 ist in `internal/qa/process/archive/hard-final-review-durchlaufhistorie-157-179.md` ausgelagert (Durchlauf 180), Durchlauf 181 härtet den Meta-Guard um den Pflichtanker `scopeLabel`; Durchlauf 182 bereinigt den Onboarding-Watchguard auf direkte Loader-Nutzung ohne lokale Wrapper; Durchlauf 183 härtet den Meta-Guard gegen Kommentar-Drift und erzwingt direkte Loader-API-Bindung aus `createDocTextLoader(...)`; Durchlauf 184 normiert `scopeLabel` zusätzlich (Suffix `Watchguard`, keine Slash-Zeichen) für einheitliche Diagnoseausgaben; Durchlauf 185 ergänzt die Dateiname-Label-Kohärenz (`scopeLabel` muss semantisch zum jeweiligen Guard-Dateinamen passen); Durchlauf 186 ergänzt ein Watchguard-Neuanlage-Playbook inkl. Template `tools/templates/watchguard.template.js` und Prozesscheckliste `internal/qa/process/watchguard-neuanlage-checkliste.md`; operativer Folgestand in `internal/qa/process/hard-final-review-next-steps.md`; Durchlauf 187 härtet den Meta-Guard zusätzlich auf Ergebnis-Token-Kohärenz (erwartetes `...-ok` je Guard-Dateiname) und schärft die Checkliste mit expliziter Dateiname→Token-Regel; operativer Folgestand in `internal/qa/process/hard-final-review-next-steps.md`. Durchlauf 188 ergänzt den Meta-Guard `tools/test_watchguard_smoke_coverage.js` zur Pflichtprüfung der Watchguard-Smoke-Abdeckung (fehlend/stale/doppelt) und verankert den Check in `scripts/smoke.sh`; operativer Folgestand in `internal/qa/process/hard-final-review-next-steps.md`. Durchlauf 189 härtet denselben Coverage-Guard auf Dateinamen-Varianten (`test_*watchguard_*.js`), damit auch Watchguards mit Suffix zuverlässig in der Smoke-Abdeckungsprüfung liegen; operativer Folgestand in `internal/qa/process/hard-final-review-next-steps.md`. Durchlauf 190 schließt den v7-SSOT-Feinschliff (Schema/Doku/Fixtures/Guards + kleine HQ-/Setup-Syncs); Durchlauf 191 zieht den verbliebenen Slot-Count-Unsync im Maintainer-Memo auf den 19er-Defaultpfad nach; Durchlauf 192 bereinigt verbleibende LP-Terminologie-Drift in spielnahen aktiven Texten (HP/Hitpoints → LP); Durchlauf 193 zieht eine missverständliche Sozialkonflikt-Formulierung in Modul 7 auf den Wurfkern (CHA/SG + Named-Opposition) zurück; Durchlauf 194 präzisiert die CHA-/Willenskraft-Terminologie (kein separates Willenskraft-Attribut) in Modul 7; Durchlauf 195 präzisiert den Pen-&-Paper-Flow bei Sozialkonflikten (erst Ausspielen, dann Wurf bei unklar/umkämpft); Durchlauf 196 schärft verbleibende Legacy-vs-v7-Lesedrift in `systems/gameflow/speicher-fortsetzung.md` (Legacy-Bridge-Beispiele eindeutig als `v: 6` + Migrationskontext markiert, kein konkurrierender v7-Neu-Exportpfad); operativer Folgestand jeweils in `internal/qa/process/hard-final-review-next-steps.md`; Durchlauf 197 schließt verbleibende LP-Restdrift im QA-Playtest-Skript `internal/qa/playtest-2026-02-22-deep.sh` (`HP`→`LP`) für vollständige Terminologie-Kohärenz auch in Evidenzpfaden; operativer Folgestand jeweils in `internal/qa/process/hard-final-review-next-steps.md`. Durchlauf 198 schließt die letzte LP-Restdrift im aktiven Gameplay-Pseudocode `gameplay/massenkonflikte.md` (`effektive_HP/HP_Pool` → `effektive_LP/LP_Pool`); operativer Folgestand jeweils in `internal/qa/process/hard-final-review-next-steps.md`. Durchlauf 199 schließt die verbleibende LP-Restdrift in `internal/qa/playtest-2026-02-22-round2.sh` (Gladiator-Startnachricht `HP 12/12` → `LP 12/12`); operativer Folgestand jeweils in `internal/qa/process/hard-final-review-next-steps.md`. Durchlauf 200 verankert einen dauerhaften LP-Regression-Guard (`tools/test_lp_terminology_watchguard.js`) im Pflicht-Smoke (`scripts/smoke.sh`) für aktive Runtime-/QA-Pfade; operativer Folgestand jeweils in `internal/qa/process/hard-final-review-next-steps.md`. Durchlauf 201 schließt eine verbleibende aktive Slot-Count-Restdrift im QA-Audit (`internal/qa/audits/ZEITRISS-qa-audit-2025.md`) auf den kanonischen 19er-Defaultpfad (Spieler-Handbuch + 18 Runtime-Module); operativer Folgestand jeweils in `internal/qa/process/hard-final-review-next-steps.md`. Durchlauf 202 schärft die Lesesicherheit in `systems/gameflow/speicher-fortsetzung.md`: Eine explizite Leseregel am großen Legacy-Bridge-HQ-Beispiel stellt klar, dass `v: 7` dort nur als Import-/Migrations-Bridge gilt und keinen kanonischen v7-Neu-Exportpfad definiert; operativer Folgestand jeweils in `internal/qa/process/hard-final-review-next-steps.md`. Durchlauf 203 schärft den Chronopolis-Play-Contract in den Runtime-SSOT-Dateien (`core/spieler-handbuch.md`, `meta/masterprompt_v6.md`, `gameplay/kampagnenstruktur.md`): Chronopolis ist als freier Infiltrationslauf mit Reaktionslogik (genau ein Beat pro bedeutsamer Aktion) und seltener Apex-Bedrohung bevorzugt auf Rückweg/Exit explizit verankert; operativer Folgestand jeweils in `internal/qa/process/hard-final-review-next-steps.md`. Durchlauf 204 synchronisiert zusätzlich die sichtbare Modul-6-Benennung auf diesen Contract (Index + Kapitelüberschrift: „Chronopolis - Freier Infiltrationslauf“ statt „Endgame-Hub“). Durchlauf 205 zieht die verbleibende Lesedrift in `core/sl-referenz.md` nach ("ohne Missionsdruck" → freier Infiltrationslauf mit Reaktionsdruck statt Freizeit-Hub). Durchlauf 206 synchronisiert die verbleibende Dev-Doku-Lesedrift in `docs/dev/chronopolis-map-blueprint.md` (Altbenennung „Endgame-Hub“ → Chronopolis-Spielmodus als freier Infiltrationslauf). Durchlauf 207 ergänzt als operativen Vorstart-Standard das Prozessdokument `internal/qa/process/playtest-readiness-gate.md` (Go/No-Go mit Setup-, Smoke-, Invarianten- und Evidence-Gate) für die nächsten Playtest-Läufe. Durchlauf 208 erzwingt die Anwendung dieses Gates zusätzlich in den operativen Vorstart-Checklisten (`docs/qa/tester-playtest-briefing.md` und `internal/qa/process/continuity-redesign-statusmatrix.md`) vor externen Testrunden. Durchlauf 209 schließt den verbleibenden Chronopolis-Kodex-Unsync: Runtime-SSOT führt Chronopolis jetzt als eigenen Sperrmodus (_Kodex dunkel, HUD lebendig_) inklusive `!offline`-Sonderantwort in `CITY` statt generischem Re-Sync-Flow. Durchlauf 210 präzisiert nach Review die Begründung (Echo-Kollapsrisiko der kodex-instanzierten CITY-Zeitlinie) und grenzt den SaveGuard-Re-Sync-Hinweis in der SL-Referenz auf reguläre Offline-Missionen außerhalb Chronopolis ein. Durchlauf 211 ergänzt den Lore-Guard `ABSOLUT-7` als kontrollierten Forschungsschnipsel und schärft parallel den Anti-Drift-Hinweis (kein Matrix-/Digitalraum-Gameplay in Chronopolis). Durchlauf 212 führt die Bezeichnungsdrift zusammen: `ABSOLUT-7/CITY` ist nun explizit als Chronopolis-Zusatzfall des Absolut-7-Projektionsmodells in Runtime-SSOT und Psi-Lore-Quelle verankert. Durchlauf 213 schließt verbleibende Mikro-Restdrift in kompakten Nutzertexten: Vollzugriff wird in HUD-/FAQ-Formulierungen explizit als außerhalb `CITY` markiert und `kodex [thema]` im Spieler-Handbuch als in `CITY` gesperrt gekennzeichnet. Durchlauf 214 verankert dafür einen dauerhaften Drift-Guard im Pflicht-Smoke (`tools/test_chronopolis_kodex_lockout_watchguard.js` + `scripts/smoke.sh`), der die Crossfile-Anker „Kodex dunkel, HUD lebendig“, `!offline`-Sperrmodus in `CITY`, `kodex [thema]`-Sperre in `CITY` und HQ-Vollzugriff außerhalb `CITY` automatisiert zusammenhält. Durchlauf 215 schließt die verbleibende Lore-Merkdrift in `core/spieler-handbuch.md` und `core/sl-referenz.md`: Zeitriss ist als Kausalwunde explizit benannt, Absolut/Nullzeit/Zeitriss werden als ein Grenzphysik-Modell zusammengeführt, und Kodex wird konsistent als Bruchlinien-Koppler statt als beliebiger Realitäts-Erschaffer geführt (inkl. Forschungssatz `ABSOLUT-7 liest keine Zukunft. Es macht Bruchlinien lesbar.`). Durchlauf 216 ergänzt im Regie-Layer der `core/sl-referenz.md` eine Leitformel am Weltstatus-Pflichtsatz, die den Missionszyklus explizit als Stabilisierung der Hauptlinie gegen Bruchwelten-Rückdruck (Riss/Echo/Kreatur) rahmt. |

## Pflegehinweis

Neue Meta-Issues werden zuerst hier erfasst und danach in Fahrplan/Log
verknüpft. Runtime-Issues bleiben primär im Fahrplan, werden aber bei
prozessualem Bedarf mit Referenz in dieser Datei gespiegelt.

## Archivierte Durchlauf-Historie

Die ausführliche Durchlauf-Historie (73–156) liegt zur besseren Lesbarkeit in
`internal/qa/process/archive/known-issues-durchlaufhistorie-73-156.md`.

Die Hard-Final-Review-Detailhistorie (157–179) liegt in
`internal/qa/process/archive/hard-final-review-durchlaufhistorie-157-179.md`.
