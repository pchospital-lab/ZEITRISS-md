---
title: "ZEITRISS Beta-QA Log 2025"
version: 0.2.0
tags: [meta]
---

# ZEITRISS Beta-QA Log 2025

## Zweck
Dieses Log sammelt unveränderte Ergebnisse aus Beta-GPT- und MyGPT-Testläufen. Es
ist die Arbeitsgrundlage, um Copy-&-Paste-Protokolle aus den GPT-Chats in
konkrete Aufgaben im QA-Fahrplan zu überführen und deren Abarbeitung
nachzuvollziehen.

## Workflow
1. Maintainer:innen oder Tester:innen führen den Playtest gemäß
   [Tester-Playtest-Briefing](../../../docs/qa/tester-playtest-briefing.md)
   aus, lassen den GPT den kompletten QA-Lauf autonom simulieren und kopieren
   das vollständige Chatprotokoll in einen neuen Abschnitt dieses Logs.
2. Kennzeichne zu Beginn jedes Abschnitts Datum, Plattform, Build und genutzte
   Wissensbasis. Standardplattform ist das OpenAI-MyGPT im Beta-Klon.
   Weitere Plattformen werden nur nach Freigabe gespiegelt und dokumentiert,
   falls Abweichungen auftreten.
3. Füge das Protokoll unverändert als Codeblock ein. Sensible Informationen
   werden vor dem Einfügen entfernt oder anonymisiert.
4. Belasse die vom GPT erzeugten `ISSUE`-, `Lösungsvorschlag`-, `To-do`- und
   `Nächste Schritte`-Blöcke unverändert unterhalb des Chatlogs; ergänzende
   Randnotizen sind optional.
5. Verlinke den Abschnitt im QA-Fahrplan und priorisiere die gemeldeten Blöcke.
6. Sobald Codex einen Punkt bearbeitet hat, aktualisiere das Log mit Verweis auf
   Commit, PR oder Ticket.

## 2025-06-11 – Repo-Agent – HQ-Save Pflichtfelder
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, runtime.js aktueller Branch (Save-Schema)
- Copy-&-Paste-Auftrag: QA-Fahrplan Maßnahmenpaket #1 – Save-Schema absichern

```chatlog
10:12 Repo-Agent: `make lint`
10:13 Tool: `Level 25: Summary: OK`
10:14 Repo-Agent: `make test`
10:17 Tool: `All smoke checks passed.`
10:18 Repo-Agent: `bash scripts/smoke.sh`
10:19 Tool: `All smoke checks passed.`
```

**Offene Punkte**
- [x] Issue #1 HQ-Save-Pflichtfelder gegen Defaults absichern.

**Nachverfolgung**
- Commit/PR: 3e4f306
- QA-Fahrplan: Maßnahmenpaket Issue #1 (Status aktualisiert 2025-06-11).
- QA-Audit: Issue #1 als erledigt markiert (2025-06-11).

## 2025-06-13 – Repo-Agent – PvP-Modus-Flag Acceptance-Smoke
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, `runtime.js` aktueller Branch (Arena-Modus)
- Copy-&-Paste-Auftrag: QA-Fahrplan Cluster C Issue #2 – PvP-Szenario für Acceptance-Smoke ergänzen

```chatlog
16:45 Repo-Agent: `node - <<'NODE'
const rt = require('./runtime.js');
const { state, handleArenaCommand, save_deep, phase_strike_cost } = rt;
state.economy.credits = 1000;
state.character.id = 'qa-agentin';
state.character.name = 'QA-Agentin';
state.character.rank = 'Recruit';
state.character.lvl = 8;
state.character.stress = 0;
state.team.members = [];
state.team.stress = 0;
state.team.psi_heat = 0;
state.campaign.episode = 2;
state.campaign.mode = 'preserve';
state.campaign.scene = 0;
state.campaign.paradoxon_index = 0;
state.campaign.scene_total = 12;
console.log('Vor Arena:', state.campaign.mode, state.arena.phase_strike_tax, phase_strike_cost());
console.log(handleArenaCommand('!arena start team 2 mode sparring'));
console.log('Arena aktiv:', state.campaign.mode, state.arena.phase_strike_tax, phase_strike_cost());
try {
  save_deep();
} catch (err) {
  console.log('Save während Arena:', err.message);
}
console.log(handleArenaCommand('!arena exit'));
state.team.stress = 0;
state.team.psi_heat = 0;
state.character.stress = 0;
const saveExit = JSON.parse(save_deep());
console.log('Arena Ende:', state.campaign.mode, state.arena.phase_strike_tax, phase_strike_cost());
console.log('Save mode:', saveExit.campaign.mode);
NODE`
16:45 Tool: `Vor Arena: preserve 0 2`
16:45 Tool: `[ARENA] Arena initiiert · Tier 2 · Gebühr 260 CU · Px-Bonus verfügbar`
16:45 Tool: `Arena initiiert · Tier 2 · Gebühr 260 CU · Offene Wüstenruine · Px-Bonus verfügbar`
16:45 Tool: `Arena aktiv: pvp 1 3`
16:45 Tool: `Save während Arena: SaveGuard: Arena aktiv – HQ-Save gesperrt.`
16:45 Tool: `[ARENA] Arena Ende · Score 0:0 · Keine Px-Belohnung (Serie verloren)`
16:45 Tool: `Arena Ende · Score 0:0 · Keine Px-Belohnung (Serie verloren)`
16:45 Tool: `Arena Ende: preserve 0 2`
16:45 Tool: `Save mode: preserve`
```

**Ergebnisse**
- [x] PvP-Flag aktiviert `phase_strike_cost()` → 3 und blockiert HQ-Save während Arena.
- [x] `!arena exit` setzt `phase_strike_cost()` zurück auf 2.
- [x] HQ-Save nach Arena bestätigt `campaign.mode: "preserve"`.

**Nachverfolgung**
- QA-Fahrplan: Cluster C Issue #2 (Acceptance-Smoke #14/#15 dokumentiert 2025-06-13).
- Docs: `docs/qa/tester-playtest-briefing.md` (PvP-Prüfschritte ergänzt).

## 2025-06-14 – Repo-Agent – Offline-Audit Jammer-Szenario
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, `runtime.js` aktueller Branch (Offline-Fallback)
- Copy-&-Paste-Auftrag: QA-Fahrplan Cluster C Issue #10 – Jammer-Suspend/Resume dokumentieren

```chatlog
08:40 Repo-Agent: `node - <<'NODE'
const rt = require('./runtime.js');
const { StartMission, offline_help, jam_now, render_offline_protocol, state, require_uplink } = rt;
StartMission();
state.campaign = { episode: 3, mission: 5, mode: 'preserve', objective: 'Test Mission', px: 2 };
state.location = 'Einsatzort';
state.phase = 'core';
state.scene = { index: 3, total: 12 };
state.comms.device = 'comlink';
state.comms.range_m = 5000;
console.log(offline_help('auto'));
jam_now(true);
state.comms.range_m = 1500;
try {
  require_uplink(state, 'radio_tx');
} catch (err){
  console.log('require_uplink error:', err.message);
}
console.log(offline_help('jammer'));
jam_now(false);
state.comms.range_m = 5000;
console.log(offline_help('resume'));
console.log('Offline log entries:', state.logs.offline);
console.log('Rendered protocol:', render_offline_protocol());
NODE`
08:40 Tool: `[OFFLINE] Kodex-Uplink getrennt – Mission läuft weiter mit HUD-Lokaldaten.`
08:40 Tool: `Kodex Offline-FAQ (ITI↔Kodex-Uplink im Einsatz gekappt):`
08:40 Tool: `- Terminal oder Hardline suchen, Relay koppeln, Jammer-Override prüfen – Kodex bleibt bis dahin stumm.`
08:40 Tool: `- Mission normal fortsetzen: HUD liefert lokale Logs, neue Saves gibt es weiterhin erst zurück im HQ.`
08:40 Tool: `- Ask→Suggest-Fallback nutzen: Aktionen als „Vorschlag:“ markieren und Bestätigung abwarten.`
08:40 Tool: ``
08:40 Tool: `Offline-Protokoll (1×): Fallback · Gerät comlink · Jammer frei · Reichweite 5000m · Relais 0 · Szene 3/12 · EP 3 · MS 5`
08:40 Tool: `require_uplink error: Kodex-Uplink getrennt – Mission läuft weiter mit HUD-Lokaldaten. !offline zeigt das Feldprotokoll bis zum HQ-Re-Sync.`
08:40 Tool: `Kodex Offline-FAQ (ITI↔Kodex-Uplink im Einsatz gekappt):`
08:40 Tool: `- Terminal oder Hardline suchen, Relay koppeln, Jammer-Override prüfen – Kodex bleibt bis dahin stumm.`
08:40 Tool: `- Mission normal fortsetzen: HUD liefert lokale Logs, neue Saves gibt es weiterhin erst zurück im HQ.`
08:40 Tool: `- Ask→Suggest-Fallback nutzen: Aktionen als „Vorschlag:“ markieren und Bestätigung abwarten.`
08:40 Tool: ``
08:40 Tool: `Offline-Protokoll (3×): jammer · Gerät comlink · Jammer aktiv · Reichweite 1500m · Relais 0 · Szene 3/12 · EP 3 · MS 5`
08:40 Tool: `Kodex Offline-FAQ (ITI↔Kodex-Uplink im Einsatz gekappt):`
08:40 Tool: `- Terminal oder Hardline suchen, Relay koppeln, Jammer-Override prüfen – Kodex bleibt bis dahin stumm.`
08:40 Tool: `- Mission normal fortsetzen: HUD liefert lokale Logs, neue Saves gibt es weiterhin erst zurück im HQ.`
08:40 Tool: `- Ask→Suggest-Fallback nutzen: Aktionen als „Vorschlag:“ markieren und Bestätigung abwarten.`
08:40 Tool: ``
08:40 Tool: `Offline-Protokoll (4×): resume · Gerät comlink · Jammer frei · Reichweite 5000m · Relais 0 · Szene 3/12 · EP 3 · MS 5`
08:40 Tool: `Offline log entries: [`
08:40 Tool: `  {"timestamp":"2025-10-12T14:26:44.344Z","reason":"auto","status":"offline","device":"comlink","jammed":false,"range_m":5000,"relays":0,"count":1,"scene_index":3,"scene_total":12,"episode":3,"mission":5,"location":"Einsatzort","phase":"core","gm_style":"verbose"},`
08:40 Tool: `  {"timestamp":"2025-10-12T14:26:44.345Z","reason":"auto","status":"offline","device":"comlink","jammed":true,"range_m":1500,"relays":0,"count":2,"scene_index":3,"scene_total":12,"episode":3,"mission":5,"location":"Einsatzort","phase":"core","gm_style":"verbose"},`
08:40 Tool: `  {"timestamp":"2025-10-12T14:26:44.346Z","reason":"jammer","status":"offline","device":"comlink","jammed":true,"range_m":1500,"relays":0,"count":3,"scene_index":3,"scene_total":12,"episode":3,"mission":5,"location":"Einsatzort","phase":"core","gm_style":"verbose"},`
08:40 Tool: `  {"timestamp":"2025-10-12T14:26:44.347Z","reason":"resume","status":"offline","device":"comlink","jammed":false,"range_m":5000,"relays":0,"count":4,"scene_index":3,"scene_total":12,"episode":3,"mission":5,"location":"Einsatzort","phase":"core","gm_style":"verbose"}`
08:40 Tool: `]`
08:40 Tool: `Rendered protocol: Offline-Protokoll (4×): resume · Gerät comlink · Jammer frei · Reichweite 5000m · Relais 0 · Szene 3/12 · EP 3 · MS 5`
```

**Ergebnisse**
- [x] Jammer-Suspend protokolliert (`reason: "jammer"`, `jammed: true`, Reichweite 1500 m).
- [x] Resume-Pfad dokumentiert (`reason: "resume"`, Jammer frei, Reichweite 5000 m).
- [x] Offline-Log-Trace (`render_offline_protocol()`) im QA-Log festgehalten.
- [x] `python3 tools/lint_runtime.py` bestätigt YAML-/Save-Prüfungen (Level 25 OK).

**Nachverfolgung**
- QA-Fahrplan: Cluster C Issue #10 (Offline-Audit Jammer-Szenario) – Status aktualisiert 2025-06-14.
- Docs: `docs/qa/tester-playtest-briefing.md` (Offline-Fallback-Hinweis deckt Jammer-Flow ab).

## 2025-04-02 – Maintainer-Team – Regressionstestplanung
- Plattform: OpenAI MyGPT (Beta-Klon) – Planungsrunde
- Wissensstand: README v4.2.2, master-index.json, Runtime-Module (18)
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – Regressionstermine festlegen

```chatlog
09:10 QA-Koordination: Terminierung der MyGPT-Regressionstests Q2–Q4 2025.
09:12 Maintainer-Team: Q2-Fenster 09.–13.06.2025 (Spiegelprozesse & Save/Load).
09:14 Maintainer-Team: Q3-Fenster 08.–12.09.2025 (Arena-/Großteam-Fokus).
09:16 Maintainer-Team: Q4-Fenster 08.–12.12.2025 (Jahresabschluss & Spiegelkontrolle).
09:18 Repo-Agent: Fahrplan-Tabelle aktualisieren, QA-Log bei Lauf ergänzen.
```

**Offene Punkte**
- [x] Q1 2025 Regressionstest dokumentieren (Abschnitt 2025-03-19).
- [ ] Q2 2025 Regressionstest 09.–13.06.2025 abschließen und loggen.
- [ ] Q3 2025 Regressionstest 08.–12.09.2025 abschließen und loggen.
- [ ] Q4 2025 Regressionstest 08.–12.12.2025 abschließen und loggen.

**Nachverfolgung**
- Commit/PR: 3338360 (Docs: QA-Termine formatiert).
- QA-Fahrplan: Sprint 3 – Wiederkehrende MyGPT-Regressionstests (Status aktualisiert 2025-04-02).
- Maintainer-Ops: Regressionstest-Zeitplan ergänzt 2025-04-02.

## 2025-10-05 – Repo-Agent – Runtime-Lint Pflichtfelder
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, Docs-Stand 2025-10-05
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – YAML-Header & Pflichtfelder absichern

```chatlog
10:12 Repo-Agent: `python3 tools/lint_runtime.py`
10:12 Tool: `INFO: [ OK ] core/wuerfelmechanik.md – YAML-Header vollständig`
10:12 Tool: `INFO: [ OK ] systems/gameflow/speicher-fortsetzung.md – YAML-Header vollständig`
10:12 Tool: `INFO: [ OK ] Save-Pflichtfeld \`campaign.px\` dokumentiert`
10:12 Tool: `INFO: [ OK ] Save-Pflichtfeld \`ui\` dokumentiert`
10:12 Tool: `Level 25: Summary: OK`
```

**Offene Punkte**
- [x] YAML-Header-Prüfung im Runtime-Lint ergänzen.
- [x] Save-Pflichtfelder automatisiert kontrollieren.

**Nachverfolgung**
- Commit/PR: 868883a (Add runtime lint for YAML headers and Pflichtfelder).
- QA-Fahrplan: Sprint 3 – Tooling erweitern (Status aktualisiert 2025-10-05).

## 2025-03-30 – Repo-Agent – Tooling-Evaluierung Link-Lint
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, Docs-Stand 2025-03-30
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – Link-Lint evaluieren

```chatlog
03:15 Repo-Agent: `python3 tools/lint_links.py README.md docs internal/qa`
03:15 Tool: `Alle geprüften Links verweisen auf existierende Dateien.`
03:16 Repo-Agent: Link-Lint in `make lint` eingebunden.
```

**Offene Punkte**
- [x] QA-Fahrplan Sprint 3 – Link-Lint abhaken (Eintrag aktualisiert).

**Nachverfolgung**
- Commit/PR: 445b8ed (Add docs link lint evaluation).
- QA-Fahrplan: Sprint 3 – Automatisierte Link-Prüfung (Status aktualisiert 2025-03-30).

## 2025-03-19 – Beta GPT – Build 4.2.2 (Acceptance-Smoke-Abgleich)
- Plattform: OpenAI MyGPT (Beta-Klon)
- Wissensstand: README v4.2.2, master-index.json, Runtime-Module (18)
- Copy-&-Paste-Auftrag: Acceptance-Smoke-Regression (Dispatcher-Checkliste)

```chatlog
03:05 Repo-Agent: `GM_STYLE=precision node tools/test_foreshadow.js`
03:05 Tool: `Foreshadow low: 0/2`
03:06 Repo-Agent: `node - <<'NODE' … !sf off → scene_overlay`
03:06 Tool: `[SF-OFF] Self-Reflection deaktiviert – Fokus bleibt extern.`
03:07 Tool: `EP 0 · MS 0 · SC 0/12 · MODE verbose · Objective: ? · ANCR ? · RW 08:00 · Px 0 · SYS 0 · Lvl - · FR:beobachter · SF-OFF`
03:08 Repo-Agent: `node - <<'NODE' … psi_heat=1 → save_deep()`
03:08 Tool: `SaveGuard: Psi-Heat > 0.`
03:10 Repo-Agent: Laufzeitscan `runtime.scene_overlay()` / `assert_foreshadow()` / `migrate_save()`; Abgleich mit [Acceptance-Smoke](../../../docs/qa/tester-playtest-briefing.md#acceptance-smoke-checkliste).
03:12 Repo-Agent: Ergebnis → Checkliste deckt Skripte ab, QA-Fahrplan aktualisieren.
```

**Offene Punkte**
- [x] Acceptance-Smoke-Checkliste um Boss-Gates, HUD-Badges und Psi-Heat
      verifizieren (Logeintrag ergänzt).

**Nachverfolgung**
- Commits: e4d2872 (docs: acceptance smoke abgleich), e5da4ad (docs: korrigiere markdown-zeilenumbrueche).
- QA-Fahrplan: Sprint 2 – Acceptance-Smoke-Checkliste (Status: abgeschlossen 2025-03-23).

## 2025-03-17 – Beta GPT – Build 4.2.2
- Plattform: Proton LUMO (offline)
- Wissensstand: README v4.2.2, master-index.json, Runtime-Module (18)
- Copy-&-Paste-Auftrag: siehe `docs/qa/tester-playtest-briefing.md` Abschnitt "Beta"

```chatlog
03:11 Tester: Lade README, Core und Systems.
03:15 Tester: Finde keinen Link zum QA-Fahrplan im README.
03:18 Tester: CONTRIBUTING verweist beim QA-Log auf das Audit.
03:24 Maintainer: QA-Fahrplan nennt noch keinen initialen Logeintrag.
03:31 Tester: Übergabe abgeschlossen, bitte in Codex aufnehmen.
```

**Offene Punkte**
- [x] README um direkte Links zu QA-Fahrplan, Audit und Beta-QA-Log ergänzen. → umgesetzt in README "QA-Artefakte & Nachverfolgung" (Sprint 1).
- [x] CONTRIBUTING-Abschnitt "Beta-GPT & QA-Übergaben" gegen aktuellen QA-Zyklus tauschen. → aktualisiert mit Log-/Audit-Pfaden und Synchronisationsschritt.
- [x] QA-Log initialisieren und Beta-Protokoll verlinken. → dieser Eintrag dokumentiert den Startpunkt.

**Nachverfolgung**
- Commits: 131046d (docs: synchronisiere qa-workflow-dokumente), 03dad05 (docs: schärfe rollen für qa-übergaben), e5da4ad (docs: korrigiere markdown-zeilenumbrueche).
- QA-Fahrplan: Sprint 1 – README-Querverweise, QA-Log initialisieren, CONTRIBUTING anpassen.
- Maintainer-Ops: Version 1.2.0 dokumentiert MyGPT als alleinige QA-Plattform und den Spiegelprozess
  (Sprint 2 – Spiegelprozesse).

## Abschnittsvorlage
```
## 2025-03-17 – Beta GPT – Build 4.2.2
- Plattform: Proton LUMO (offline)
- Wissensstand: README v4.2.2, master-index.json, Runtime-Module (18)
- Copy-&-Paste-Auftrag: siehe `docs/qa/tester-playtest-briefing.md` Abschnitt "Beta"

```chatlog
<ungefiltertes Protokoll>
```

**Offene Punkte**
- [ ] Zusammenfassung des QA-Befunds (z. B. "Arena belohnt Px doppelt")
- [ ] ...

**Nachverfolgung**
- Commit/PR: `docs:xxxx`
- QA-Fahrplan: Abschnitt 1.2
```

## Pflegehinweise
- Bewahre jeden Abschnitt in chronologischer Reihenfolge auf (neuste oben).
- Verweise in Commit- oder PR-Beschreibungen auf den entsprechenden Abschnitt.
- Entferne keinen historischen Eintrag; markiere Korrekturen mit einem kurzen
  Hinweis ("Korrigiert am …").
- Sobald alle offenen Punkte erledigt sind, markiere den Abschnitt als
  abgeschlossen und dokumentiere das Datum.
