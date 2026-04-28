---
title: Nachcheck-Status — Anschlussplan
date: 2026-04-28
status: aktiv
---

# Nachcheck-Status (schlank)

Ziel: Klarer Anschluss nach dem letzten Drift-Fix, ohne neue Mammutliste.
Quelle: `uploads/ZEITRISS_agentenpaket_nachcheck.md` + `uploads/zeitriss_nachcheck_backlog.json`.

## Bereits erledigt

- **P0 Save/Start-SSOT** aus dem Nachcheck ist umgesetzt (klassischer Start mit Chargen-Save-Gate, HQ-Load-Router, `campaign.mode` ohne `rift`, Import/Export-Schema-Split, Rift-Trigger auf **Px 5**).
- **P1-008** erledigt: Persistente Konflikte laufen auf
  `logs.flags.continuity_conflicts[]` (Trace-Event `merge_conflicts` bleibt).
- **P1-010** erledigt: Rift-Standardloot nutzt Ermittlungsakten/Para-Spuren/
  experimentelle Gear; Relikte bleiben Core-/Story-Beute.

## Offen (nächster sinnvoller Block)

1. **P1-006 Arena-Persistenzvertrag finalisieren**
   - persistent vs. transient Felder hart trennen (`queue_state`, `resume_token`,
     `previous_mode`, First-Win-/Diminishing-Counter).
2. **P1-007 Seed-Cap-Drift restlos entfernen**
   - überall klar: **kein Solo-Hardcap**, Cap **12 nur beim HQ-Merge**.
3. **P1-012 Chronopolis-Schärfung**
   - Formulierungen auf „Kodex stabilisiert/dechiffriert reale Bruchlinie“
     konsolidieren (kein VR-/Simulations-Frame).

## Empfohlener nächster Schritt (ein Sprint)

- **Patch-Sprint "Arena+Seeds"** (P1-006 + P1-007 zusammen).
- Danach **gezielter Nachcheck nur für Chronopolis-Texte** (P1-012).

## Mini-Verifikation nach jedem Sprint

1. `bash scripts/smoke.sh`
2. Fokus-Playtests gemäß `docs/testing.md`:
   - Rift: `RIFT-01..03`
   - Chronopolis: `CHRONO-01..03`
   - PvP/Arena: `PVP-01..03`
   - Cross-Mode: `MULTI-01..03`, `CROSS-01`

## Definition of Done für den nächsten PR

- Keine konkurrierenden Aussagen zu Arena-/Seed-Persistenz in
  `core/sl-referenz.md`, `systems/gameflow/speicher-fortsetzung.md`,
  `gameplay/kampagnenstruktur.md`, `meta/masterprompt_v6.md`.
- Smoke grün.
- PR-Body nennt exakt: **was gefixt**, **was bewusst offen bleibt**.
