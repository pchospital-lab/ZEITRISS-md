---
title: "Issue-Pack Fahrplan – Durchlauf 28"
version: 0.1.0
tags: [qa, plan]
---

# Issue-Pack Fahrplan – Durchlauf 28

Quelle: Fortsetzung ZR-016 (Maintainer-Hinweise zu Setup-Default, Epochenbegriffen und Save-Pflichtfeldern).

## Ziel

Kleine, anschlussfähige Konsistenzrunde:
- Setup-Script auf Sonnet 4.6 als Standardmodell ziehen.
- Verbleibende Epochenrollen-Wording mit `:innen` bei Schaman/Wahrsager aus Runtime-Modulen entfernen.
- Save-v7-Beispiel um explizite Talentführung schärfen und Epochenfahrzeug-Abgrenzung dokumentieren.

## Scope dieses Durchlaufs

- Setup-Default:
  - `scripts/setup-openwebui.sh`
- Runtime-Wording:
  - `gameplay/kampagnenuebersicht.md`
  - `systems/kp-kraefte-psi.md`
- Save-SSOT-Klarstellung:
  - `systems/gameflow/speicher-fortsetzung.md`
- QA-Nachführung:
  - neues Log `internal/qa/logs/2026-03-07-issue-pack-durchlauf-28.md`
  - Update `internal/qa/process/known-issues.md` (ZR-016)

## Nicht im Scope

- Umbau historischer QA-Evidenzdateien mit DeepSeek-Verweisen.
- Neue Runtime.js-Features.
- Neue Pflichtfelder jenseits des bestehenden v7-Kanons.

## Exit-Kriterium für Durchlauf 28

- Setup-Default zeigt Sonnet 4.6 statt DeepSeek.
- Keine Treffer mehr für `Schaman:innen` / `Wahrsager:innen` in aktiven Runtime-Modulen.
- Save-v7-Kanonblock nennt `talents[]` explizit im Charakterbeispiel und grenzt Epochenfahrzeuge als Nicht-Pflichtfeld sauber ab.
- `bash scripts/smoke.sh` ist grün.
