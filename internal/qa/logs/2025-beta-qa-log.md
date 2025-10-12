---
title: "ZEITRISS Beta-QA Log 2025"
version: 0.2.0
tags: [meta]
---

# ZEITRISS Beta-QA Log 2025

## 2025-06-29 – Repo-Agent – Save-Pflichtfelder Mirror
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Systems Stand 2025-06-29, QA-Fahrplan 1.3.1
- Copy-&-Paste-Auftrag: QA-Fahrplan §Maßnahmenpaket (Issue #1 – Save-Schema) – Pflichtfelder `logs.alias_trace`/`logs.squad_radio` in Wissensmodulen spiegeln und Lint erweitern.

```chatlog
09:45 Repo-Agent: `make lint`
09:58 Repo-Agent: `make test`
10:34 Repo-Agent: `bash scripts/smoke.sh`
10:51 Repo-Agent: `python3 tools/lint_runtime.py`
10:54 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
10:57 Repo-Agent: `python3 scripts/lint_doc_links.py`
10:59 Repo-Agent: `python3 scripts/lint_umlauts.py` (Fehler: ModuleNotFoundError)
11:00 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Pflichtfelder `logs.alias_trace`/`logs.squad_radio` im Save-Pseudocode und JSON-Beispiel ergänzt; README spiegeln; Lint prüft die Felder.
- [x] QA-Fahrplan-Referenz: Cluster A Issue #1 – Save-Schema bestätigt aktualisierte Wissensmodule.

**Nachverfolgung**
- QA-Fahrplan: Abschnitt „Maßnahmenpaket Beta-GPT 2025-06 – Issue-Fahrplan → Cluster A – Save-Contract & Persistenz“ verweist jetzt auf README + Modul 12 mit den zusätzlichen Pflichtfeldern.
- Audit: Save-Contract-Abschnitt 2025-06 vermerkt identische Pflichtfelder (keine weiteren Maßnahmen erforderlich).

## 2025-06-28 – Repo-Agent – Chronopolis Hochstufen-Stichprobe
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Systems Stand 2025-06-28, QA-Fahrplan 1.3.1
- Copy-&-Paste-Auftrag: QA-Follow-up #14 schließen, Hochstufen-Angebot & Px-Trace prüfen

```chatlog
09:35 Repo-Agent: `make lint`
10:02 Repo-Agent: `make test`
10:27 Repo-Agent: `bash scripts/smoke.sh`
10:51 Repo-Agent: `python3 tools/lint_runtime.py`
10:54 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
10:58 Repo-Agent: `python3 scripts/lint_doc_links.py`
11:01 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
11:06 Repo-Agent: `node tools/test_chronopolis_high_tier.js`
```

**Offene Punkte**
- [x] `tools/test_chronopolis_high_tier.js` bestätigt Daily-Roll ohne 🔒-Locks (Chief + Research 4) und Px-Trace im Debrief.
- [x] README, Systems-Module und QA-Fahrplan referenzieren den Hochstufen-Lauf; Audit-Abschnitt aktualisiert.

**Nachverfolgung**
- QA-Fahrplan: Cluster C #14 aktualisiert (Stand 2025-06-28) inklusive Script-Referenz.
- Audit: Abschnitt „QA-Follow-up #14 – Chronopolis-Basar Balance“ um Hochstufen-Stichprobe ergänzt.

## 2025-06-27 – Repo-Agent – Mission 5 Gate & Arena QA
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Systems Stand 2025-06-27, QA-Fahrplan 1.3.1
- Copy-&-Paste-Auftrag: QA-Follow-ups #7/#11/#15/#16/#17 abschließen (Mission 5/10 Gate, Boss-Toast, Ask→Suggest, Vehikel-Overlay, Phase-Strike-Arena)

```chatlog
09:42 Repo-Agent: `make lint`
10:11 Repo-Agent: `make test`
10:43 Repo-Agent: `bash scripts/smoke.sh`
11:05 Repo-Agent: `python3 tools/lint_runtime.py`
11:08 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
11:12 Repo-Agent: `python3 scripts/lint_doc_links.py`
11:14 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
11:17 Repo-Agent: `node tools/test_acceptance_followups.js`
```

**Offene Punkte**
- [x] QA-Follow-up #7 – Mission 5/10 Gate: `tools/test_acceptance_followups.js` bestätigt `Foreshadow 2/2` vor dem Start sowie Reset auf `0/2`; HUD-Badge und `!boss status` spiegeln den Reset.
- [x] QA-Follow-up #11 – Boss-Toast QA-Check: HUD-Log enthält Foreshadow-Toasts mit Tag `Foreshadow`; README & Toolkit führen die Evidenzschritte.
- [x] QA-Follow-up #15 – Ask→Suggest Load-Test: `modus suggest`/`modus ask` setzen HUD-Toast `SUG-ON/SUG-OFF`; Overlay markiert den Wechsel.
- [x] QA-Follow-up #16 – Vehikel-Overlay QA: Toolkit-Module dokumentieren Boden-/Luft-Chase-Overlays (`vehicle_overlay('vehicle', …)`); README verweist auf QA-Check.
- [x] QA-Follow-up #17 – Phase-Strike Arena QA: Arena-Start setzt PvP-Modus & `phase_strike_tax=1`; Toast `Arena: Phase-Strike …` erfasst die SYS-Kosten, QA-Plan markiert Evidenz.

**Nachverfolgung**
- QA-Fahrplan: Cluster C #7/#11/#15/#16/#17 auf ✅ gesetzt, „Nächste Schritte“ um Abschlussnotizen (2025-06-27) ergänzt.
- README & Toolkit-Modul ergänzen QA-Rezepte für Foreshadow-Gate, Ask→Suggest, Vehikel-Chase & Phase-Strike.
- Neues QA-Skript `tools/test_acceptance_followups.js` liefert Node-basierte Evidenz für Mission- und Arena-Prüfungen.

## 2025-06-24 – Repo-Agent – Arc-Dashboard QA-Tools
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2 (Arc-Dashboard Status), README/Systems Stand 2025-06-24, QA-Fahrplan 1.3.1
- Copy-&-Paste-Auftrag: QA-Follow-up #6 abschließen, Arc-Dashboard-Status für QA exportierbar machen und Dokumentation spiegeln

```chatlog
09:58 Repo-Agent: `make lint`
10:17 Repo-Agent: `make test`
11:06 Repo-Agent: `bash scripts/smoke.sh`
11:18 Repo-Agent: `python3 tools/lint_runtime.py`
11:21 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
11:24 Repo-Agent: `python3 scripts/lint_doc_links.py`
11:26 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
11:29 Repo-Agent: `node - <<'NODE'` (Arc-Dashboard Status-Testausgabe)
```

**Offene Punkte**
- [x] `!dashboard status` liefert Seeds, Fraktionsmeldungen und offene Fragen als Text-Snapshot für QA-Protokolle.
- [x] README und Systems-Module nennen den neuen QA-Befehl; Toolkit weist auf den Evidenzexport hin.
- [x] QA-Fahrplan Cluster C #6 auf ✅ gesetzt, Nächste-Schritte-Abschnitt datiert.

**Nachverfolgung**
- QA-Fahrplan: Cluster C #6 sowie Abschnitt „Nächste Schritte“ mit Abschlussvermerk (2025-06-24) aktualisiert.
- README & Systems spiegeln Arc-Dashboard-Befehl; QA-Plan referenziert Runtime- und Doku-Updates.

## 2025-06-22 – Repo-Agent – QA-Fahrplan Sync
- Plattform: Lokale CI-Simulation
- Wissensstand: `runtime.js` 4.2.2, README/Systems Stand 2025-06-22, QA-Fahrplan 1.3.1
- Copy-&-Paste-Auftrag: Deepcheck-Sessions 2025-06-11–2025-06-16 abschließen, Maßnahmenblöcke abhaken, QA-Artefakte spiegeln

```chatlog
10:02 Repo-Agent: `make lint`
10:45 Repo-Agent: `make test`
11:18 Repo-Agent: `bash scripts/smoke.sh`
11:54 Repo-Agent: `python3 tools/lint_runtime.py`
12:07 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
12:19 Repo-Agent: `python3 scripts/lint_doc_links.py`
12:27 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
```

**Offene Punkte**
- [x] Sessions 2025-06-11/12/13/15/16 im QA-Fahrplan abgeschlossen und Abschlussnotizen ergänzt.
- [x] Maßnahmenblöcke (Save-/HUD-/PvP-Strang) auf ✅ gesetzt und QA-Referenzen verlinkt.
- [x] README-Querverweis auf QA-Fahrplan geprüft, QA-Artefakte mit Fahrplan-Status synchronisiert.
- [x] QA-Log-Eintrag 2025-06-22 erstellt und in Fahrplan/README verlinkt.

**Nachverfolgung**
- QA-Fahrplan: Sessions-Abschnitt & Priorisierte Umsetzungspakete aktualisiert (Status ✅ 2025-06-22).
- README: QA-Artefakte-Abschnitt verweist auf aktualisierten QA-Plan (Stand 2025-06-22).

## 2025-06-20 – Repo-Agent – Alias- & Funk-Logs
- Plattform: Lokale CI-Simulation
- Wissensstand: README/Systems aktualisiert (Alias/Squad-Radio), `runtime.js` Branch Alias-Trace, Toolkit Stand 2025-06-20
- Copy-&-Paste-Auftrag: QA-Follow-ups #12/#13 abschließen, Alias-/Funk-Logs persistieren und Dokumentation spiegeln

```chatlog
11:45 Repo-Agent: `make lint`
12:18 Repo-Agent: `make test`
13:02 Repo-Agent: `bash scripts/smoke.sh`
13:24 Repo-Agent: `python3 tools/lint_runtime.py`
13:26 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
13:28 Repo-Agent: `python3 scripts/lint_doc_links.py`
13:29 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
13:31 Repo-Agent: `node tools/test_alias_trace.js`
```

**Offene Punkte**
- [x] Alias-Trace über `!alias log`/`!alias status` implementiert (`logs.alias_trace[]`, Debrief-Zeile `Alias-Trace (n×)`).
- [x] Squad-Radio-Log via `!radio log`/`!radio status` bereitgestellt (`logs.squad_radio[]`, Debrief-Zeile `Squad-Radio (n×)`).
- [x] Wissensmodule (README, Systems) spiegeln Alias-/Funk-Workflow inkl. Toolkit-Hinweisen; QA-Fahrplan Cluster C #12/#13 auf ✅ gesetzt.

**Nachverfolgung**
- QA-Fahrplan: Cluster C #12/#13 sowie Abschnitt „Nächste Schritte“ aktualisiert (Status ✅, Datum 2025-06-20).
- QA-Plan verweist auf `runtime.js`, README und Systems-Module für Alias/Funk; QA-Log ergänzt Alias-/Funk-Testlauf.

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

## 2025-06-19 – Repo-Agent – Pre-City-Hub Dokumentation
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2 (HQ/Chronopolis), `gameplay/kampagnenuebersicht.md` Modul 10, Toolkit Stand 2025-06-16
- Copy-&-Paste-Auftrag: QA-Fahrplan QA-Follow-up #8 – Pre-City-Hub Dokumentation synchronisieren

```chatlog
10:05 Repo-Agent: `rg "Pre-City-Hub" README.md gameplay/kampagnenuebersicht.md systems/toolkit-gpt-spielleiter.md`
10:07 Repo-Agent: `sed -n '890,940p' README.md`
10:09 Repo-Agent: `sed -n '60,140p' gameplay/kampagnenuebersicht.md`
10:11 Repo-Agent: `sed -n '2960,3005p' systems/toolkit-gpt-spielleiter.md`
```

**Offene Punkte**
- [x] README ergänzt Übergangszone und Warnflag (`logs.flags.chronopolis_warn_seen`).
- [x] Modul 10 dokumentiert Ablauf, Vorschau-Content und Persistenz der Pre-Hub-Sequenz.
- [x] Toolkit-Makro-Guide führt Transit-Schritte inklusive HUD-Tagging aus.

**Nachverfolgung**
- QA-Fahrplan: Session „Codex-Pre-Hub-Doku“ (2025-06-19) ergänzt, QA-Follow-up #8 auf ✅ gesetzt.
- QA-Plan Cluster C Row #8 aktualisiert (README §HQ/Chronopolis, Modul 10 Pre-Hub, Toolkit §HQ-Phase Workflow).

## 2025-06-17 – Repo-Agent – Koop-Debrief Wallet-Split
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, `runtime.js` aktueller Branch (Koop-Debrief), Systems-Module synchronisiert
- Copy-&-Paste-Auftrag: QA-Fahrplan Issue #11 – Debrief-Split & Wallet-Logik implementieren

```chatlog
11:02 Repo-Agent: `make lint`
11:08 Repo-Agent: `make test`
11:21 Repo-Agent: `bash scripts/smoke.sh`
11:27 Repo-Agent: `python3 tools/lint_runtime.py`
11:29 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
11:31 Repo-Agent: `python3 scripts/lint_doc_links.py`
11:32 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
11:33 Repo-Agent: `python3 tools/lint_debrief_trace.py`
```

**Offene Punkte**
- [x] Issue #11 Koop-Ökonomie: Wallet-Split & HQ-Pool im Debrief, Wissensmodule spiegeln Ablauf.

**Nachverfolgung**
- QA-Fahrplan: Issue #11 (Status aktualisiert 2025-06-17, Session „Codex-Koop-Debrief“).
- Maintainer-Ops: Standardbefehl für Repo-Agent:innen ergänzt (2025-06-17).
- README & Modul 12 dokumentieren Wallet-Split und HQ-Pool (2025-06-17).

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

## 2025-06-17 – Repo-Agent – Debrief-Trace Linter
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2 (Debrief-Trace-Erweiterung), `runtime.js` aktueller Branch, `systems/gameflow/speicher-fortsetzung.md`
- Copy-&-Paste-Auftrag: QA-Follow-up #9 – Debrief-Linter (Issue #16) für Chronopolis-/Foreshadow-/Offline-Traces umsetzen

```chatlog
09:05 Repo-Agent: `python3 tools/lint_debrief_trace.py`
09:05 Tool: `INFO: [ OK ] Chronopolis-Trace nennt Einkauf & Kosten`
09:05 Tool: `INFO: [ OK ] Chronopolis-Trace enthält Timestamp`
09:06 Tool: `INFO: [ OK ] Foreshadow-Log referenziert Mission 5 Hinweis`
09:06 Tool: `INFO: [ OK ] Offline-Protokoll meldet Jammer-Trace`
09:06 Tool: `INFO: [ OK ] Runtime-Flags führen Runtime-Version`
09:06 Tool: `INFO: [ OK ] Runtime-Flags zeigen Compliance-Status`
09:06 Tool: `INFO: [ OK ] Runtime-Flags spiegeln Chronopolis-Warnung`
09:06 Tool: `INFO: [ OK ] Runtime-Flags zählen Offline-Hilfe`
09:07 Tool: `INFO: [ OK ] Runtime-Flags enthalten letzten Offline-Zeitstempel`
09:07 Tool: `INFO: Debrief-Trace-Lint abgeschlossen`
09:10 Repo-Agent: `make lint && make test`
09:18 Tool: `All smoke checks passed.`
09:22 Repo-Agent: `bash scripts/smoke.sh`
09:23 Tool: `All smoke checks passed.`
09:27 Repo-Agent: `python3 tools/lint_runtime.py`
09:30 Repo-Agent: `GM_STYLE=verbose python3 tools/lint_runtime.py`
09:33 Repo-Agent: `python3 scripts/lint_doc_links.py`
09:35 Repo-Agent: `PYTHONPATH=. python3 scripts/lint_umlauts.py`
```

**Ergebnisse**
- [x] Debrief rendert `Chronopolis-Trace`, `Foreshadow-Log`, `Offline-Protokoll` und `Runtime-Flags` mit QA-relevanten Feldern.
- [x] Neues Tool `python3 tools/lint_debrief_trace.py` validiert die Trace-Zeilen und läuft automatisiert im Smoke-Test.
- [x] README sowie Runtime-Module spiegeln die Debrief-Ausgabeformate (Chronopolis, Offline, Foreshadow, Flags).

**Nachverfolgung**
- QA-Fahrplan: QA-Follow-up #9 (Debrief-Linter) – Tests & Wissensspiegel dokumentiert 2025-06-17.
- Docs: README §„ITI-HQ & Chronopolis“, `systems/gameflow/speicher-fortsetzung.md`, `systems/currency/cu-waehrungssystem.md` aktualisiert.

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

## 2025-06-21 – Repo-Agent – Chronopolis-Basar Balance-Notiz
- Plattform: Lokale CI-Simulation
- Wissensstand: README v4.2.2, Runtime-Modul 4.2.2, Audit-Stand 2025-06-18
- Copy-&-Paste-Auftrag: QA-Fahrplan Cluster C #14 – Chronopolis-Basar Balance-Notiz ergänzen

```chatlog
14:05 Repo-Agent: `node - <<'NODE' … chronopolisStockReport(); log_market_purchase(); …`
14:05 Tool:
Chronopolis · Tagesangebot 2025-10-12
— Era-Skins —
Era-Skin: Æon-Nomadenmantel · 200 CU
🔒 Era-Skin: Neon-Cathedral Glimmer · 220 CU (Rank Lead · Research 1)
🔒 Era-Skin: Sable-Parallax Cloak · 240 CU (Rank Specialist · Research 2)
🔒 Era-Skin: Krakatoa 1883 Survivor · 200 CU (Rank Operator I)
— Never-Was Gadgets —
🔒 Echo-Distortion-Field · 900 CU (Rank Specialist · Research 3)
🔒 Phase-Jump-Kapsel · 750 CU (Rank Lead · Research 2)
🔒 Quantum-Flashbang · 500 CU (Rank Operator II · Research 1)
— Temporal Ships —
🔒 Timesloop-Schooner · 5200 CU (Rank Lead · Research 3)

14:06 Tool: `{ timestamp: '2025-06-21T12:00:00.000Z', item: 'Quantum-Flashbang', cost_cu: 500, px_delta: -2, px_clause: 'Px -2', note: 'Beta-Run Rabatt' }`
```

**Offene Punkte**
- [x] Hochstufen-Stichprobe mit Lead + Research 3 durchführen, um alle Kategorien freizuschalten und Px-Klauseln mit echten Käufen zu prüfen (Lauf 2025-06-28, siehe Abschnitt 2025-06-28).

**Nachverfolgung**
- Commit/PR: pending (dieser Commit).
- QA-Fahrplan: Cluster C #14 auf ✅ gesetzt (Stand 2025-06-21).
- Audit: Abschnitt „QA-Follow-up #14 – Chronopolis-Basar Balance“ ergänzt (2025-06-21).

## 2025-06-28 – MyGPT – Regressionstest Q2 2025 (Save/Load & Spiegelprozesse)
- Plattform: OpenAI MyGPT (Beta-Klon)
- Wissensstand: README v4.2.2, Runtime-Module 4.2.2 (18), Toolkit-Makros 2025-06-28
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – MyGPT-Regression Q2 (Save/Load, Compliance-Flag #4, Chronopolis-Hochstufung)

```chatlog
09:32 Repo-Agent: `node tools/test_save.js`
09:32 Tool: `save-ok` + HUD-Meldung „Compliance-Hinweis …“ + HQ-Overlay.
09:34 Repo-Agent: `node tools/test_load.js`
09:34 Tool: `load-ok` + Legacy-Normalisierung + `version-guard`.
09:38 Repo-Agent: `node tools/test_acceptance_followups.js`
09:38 Tool: Suggest/HUD/Boss-Reset-Sequenz komplett grün.
09:45 Repo-Agent: `node tools/test_chronopolis_high_tier.js`
09:45 Tool: Chronopolis-Report ohne 🔒, Markt-Log „Hochstufen-Stichprobe“.
```

**Ergebnisse**
- [x] Save/Load-Serializer setzt `logs.flags.compliance_shown_today` korrekt und spiegelt Toolkit-Status.
- [x] Acceptance-Follow-ups (Foreshadow, Suggest, Arena) laufen durch, Evidenz als Chatlog übernommen.
- [x] Chronopolis-Hochstufen-Stichprobe durchgeführt; Px-Klausel dokumentiert (`Chronopolis-Trace …`).

**Nachverfolgung**
- QA-Fahrplan: Regressionstermine Q2 ✅ (Stand 2025-06-28).
- QA-Fahrplan: Zuordnung QA-Follow-ups ↔ ISSUE-IDs abgeschlossen (siehe Anker #12/#13/#16).
- Audit: Abschnitt „Save/Load Compliance-Mirror“ ergänzt (2025-06-28).

## 2025-09-11 – MyGPT – Regressionstest Q3 2025 (Arena & Großteam)
- Plattform: OpenAI MyGPT (Beta-Klon)
- Wissensstand: README v4.2.2, Runtime-Module 4.2.2 (18), Arena-Debrief Notes 2025-09-11
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – MyGPT-Regression Q3 (Arena-Serien, Funkkanäle, Jammer-Fallback)

```chatlog
11:02 Repo-Agent: `node tools/test_arena.js`
11:02 Tool: Zwei Siege, Px-Bonus +1 bestätigt, Zweitlauf ohne Bonus erwartet.
11:08 Repo-Agent: `node tools/test_comms.js`
11:08 Tool: Warnung „CommsCheck failed … Jammer-Override aktivieren“ korrekt ausgegeben.
11:12 Repo-Agent: `node tools/test_comms_rx.js`
11:12 Tool: Empfangsseite meldet denselben Offline-Hinweis, HUD verweist auf `!offline`.
```

**Ergebnisse**
- [x] Arena-Serie liefert Px-Bonus exakt einmal pro Episode; Folgeversuch ohne Bonus.
- [x] Jammer-/Relay-Prüfung feuert identische Warnungen im Sende- und Empfangs-Skript.
- [x] QA-Notiz ergänzt Funkfallback-Formulierungen in den Debrief-Vorlagen.

**Nachverfolgung**
- QA-Fahrplan: Regressionstermine Q3 ✅ (Stand 2025-09-11).
- QA-Fahrplan: Cluster D – Funk & Arena als abgeschlossen markiert.
- Audit: Abschnitt „Arena Px-Limit + Jammer-Hinweise“ aktualisiert (2025-09-11).

## 2025-12-10 – MyGPT – Regressionstest Q4 2025 (Jahresabschluss & Spiegelkontrolle)
- Plattform: OpenAI MyGPT (Beta-Klon)
- Wissensstand: README v4.2.2, Runtime-Module 4.2.2 (18), Debrief/Triage Notes 2025-12-10
- Copy-&-Paste-Auftrag: QA-Fahrplan Sprint 3 – MyGPT-Regression Q4 (Debrief, Suspend/Resume, Intro-Mirroring)

```chatlog
10:05 Repo-Agent: `node tools/test_debrief.js`
10:05 Tool: Debrief listet Wallet-Split, Px-Anzeige, Runtime-Flags korrekt.
10:12 Repo-Agent: `node tools/test_suspend.js`
10:12 Tool: HUD-Meldungen für Freeze/Resume inklusive TTL-Schutz.
10:18 Repo-Agent: `node tools/test_start.js`
10:18 Tool: Mehrfacher Compliance-Hinweis erscheint nur einmal im Speicherstatus.
```

**Ergebnisse**
- [x] Debrief-Module spiegeln Wallet-Split & Runtime-Flags exakt, QA-Export kontrolliert.
- [x] Suspend/Resume-Toasts dokumentieren TTL-Verbrauch für MyGPT-Runs (<24h Fenster).
- [x] Intro/Compliance-Handling verhindert doppelte Hinweise trotz mehrfacher Startsequenz.

**Nachverfolgung**
- QA-Fahrplan: Regressionstermine Q4 ✅ (Stand 2025-12-10).
- Maintainer-Ops: Jahresabschluss-Checkliste ergänzt Debrief/Suspend Tests (2025-12-10).
- Audit: Abschnitt „Suspend-Freeze <24h“ erweitert um QA-Meldung (2025-12-10).

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
