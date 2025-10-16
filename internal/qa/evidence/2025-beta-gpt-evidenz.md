---
title: "QA-Evidenz Beta-GPT 2025"
version: 0.1.0
tags: [meta, qa]
---

# QA-Evidenz – Beta-GPT Läufe 2025

Dieses Protokoll listet die für die Beta-GPT-Regressionsläufe geforderten
Nachweise. Sobald die Maintainer:innen den jeweiligen Lauf erneut "live"
fahren, werden die HUD-/Save-/Dispatcher-Auszüge hier ergänzt und in den
QA-Logs verlinkt.

## 2025-07-05 – Save/HUD/Arena-Deltas

Referenzen: QA-Log [2025-07-05](../logs/2025-beta-qa-log.md#2025-07-05--tester-beta-gpt--schema-hud-und-arena-deltas),
QA-Fahrplan §„Maßnahmenpaket Beta-GPT 2025-07“. Die technischen Fixes sind
abgeschlossen; es fehlen lediglich die Nachweise.

- [ ] **Migration 5→6 (DeepSave):** Vorher-/Nachher-JSON für einen
      Gruppensave, der den Wechsel von `save_version: 5` auf `save_version: 6`
      dokumentiert.

```json
// TODO: DeepSave-Diff hier einfügen
```

- [ ] **Foreshadow/HUD-Reset:** Screenshot oder HUD-Log mit `Foreshadow 2/2`
      vor Missionsstart sowie `FS 0/2` nach `StartMission()`; zusätzlich die
      QA-Journal-Notiz zum Reset.

```text
TODO: HUD-Auszug + QA-Journal-Zitat ergänzen
```

- [ ] **Arena- & City-Smoke:** Dispatcher-Transkript mit `Speichern blockiert – Arena aktiv`
      sowie City-Minimaltest (`!chrono stock`, Warn-Banner). Ein kurzer Debrief-Ausschnitt
      genügt.

```text
TODO: Arena-/City-Auszüge einfügen
```

## 2025-07-18 – Save/HUD/Compliance Regression

Referenzen: QA-Log [2025-07-18](../logs/2025-beta-qa-log.md#2025-07-18--tester-beta-gpt--savehudcompliance-regression),
QA-Fahrplan §„Maßnahmenpaket Beta-GPT 2025-07-18“.

- [ ] **Exfil- & Wallet-Autoinit:** Save-Ausschnitt, der den Rücksprung von
      `campaign.exfil.active` sowie die Wallet-Initialisierung vor dem Debrief
      zeigt.

```json
// TODO: Exfil-/Wallet-Trace einfügen
```

- [ ] **SF-OFF Persistenz + Arena Psi-Log:** HUD-Log mit `SF-OFF` Badge und
      zugehöriger `logs.psi[]`-Zeile (`phase_strike_tax`).

```text
TODO: HUD-/Psi-Log-Auszug ergänzen
```

- [ ] **Dispatcher-Hinweise & Semver-Text:** Ausschnitt aus dem Start-Dispatcher,
      der `!radio clear`/`!alias clear` nennt und den vereinheitlichten
      Semver-Warntext enthält.

```text
TODO: Dispatcher-Text einfügen
```

## 2025-10-15 – Acceptance-/HUD-/Accessibility-Deltas

Referenzen: QA-Log [2025-10-15](../logs/2025-beta-qa-log.md#2025-10-15--tester-beta-gpt--acceptancehudsave-drift) sowie
QA-Fahrplan §„Maßnahmenpaket Beta-GPT 2025-10-15“.

- [ ] **Acceptance-Smoke 15 Schritte:** Dokumentierter Lauf (Checkliste oder
      HUD-Protokoll), der die Schritte 1–15 durchläuft und die neuen Punkte für
      Accessibility, City und Arena enthält.

```text
TODO: Acceptance-Protokoll ergänzen
```

- [ ] **Save-Migration Legacy-Gruppensave:** Beispiel für einen v5-Gruppensave,
      der durch den Loader auf Schema v6 gehoben wird (inkl. `allow_entry_choice`
      Flag und Arena-Phase).

```json
// TODO: Legacy-Gruppensave → v6 hier einfügen
```

- [ ] **HUD-Dumps & Accessibility-Dialog:** Screenshot oder HUD-Log mit
      `SF-OFF` Auto-Reset, Gate-Badge Persistenz (M5/M10) sowie dem neuen
      `!accessibility`-Dialog.

```text
TODO: HUD-/Dialog-Auszüge einfügen
```

- [ ] **Dispatcher-Trigger & Cinematic-Header:** Transkript, das die Option
      `trigger` beim Start-Dispatcher und den erzwingenden Cinematic-Header nach
      dem Briefing festhält.

```text
TODO: Dispatcher-/Cinematic-Auszug ergänzen
```

> **Hinweis:** Sobald ein Kasten abgehakt ist, bitte die betreffenden
> QA-Log-Abschnitte aktualisieren und im Audit den neuen Evidenzstand
> vermerken.
