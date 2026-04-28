---
title: "QA-Status: PvP/Bio-Nachcheck (2026-04-28)"
version: 1.0.0
tags: [qa, pvp, charaktere]
---

# QA-Status: PvP/Bio-Nachcheck (2026-04-28)

Quelle: `uploads/ZEITRISS_agentenpaket_pvp_bio_nachcheck.md` +
`uploads/zeitriss_pvp_bio_backlog.json`.

## Umsetzungsstand (Repo)

### P0

- [x] **P0-01** Arena vergibt kein Px mehr (Runtime-Texte/Exit angepasst).
- [x] **P0-02** PvP-only-Progressionsvertrag dokumentiert
      (Training-XP/Missionsäquivalent, kein Px/keine Seeds).
- [x] **P0-03** Cashout/Pending/Push als Kanon ergänzt.
- [x] **P0-04** `ui.action_mode` im Masterprompt-Save-Template ergänzt.
- [x] **P0-05** `previous_mode`-Fallback auf `mixed` abgesichert.

### P1

- [x] **P1-01** Player-facing Begriffe auf Grundform/Körperprofil umgestellt.
- [x] **P1-02** Rekrutierungs-/Körpergefühl physischer formuliert.
- [x] **P1-03** Psi-Prämisse als rationaler Magieersatz in der Chargenlogik geschärft.
- [x] **P1-04** Quick-Build-Sprache von Rasse/Rassenmods auf Grundform/Profil-Mods gedreht.
- [x] **P1-05** First-Win vs Repeat-Malus deterministisch dokumentiert.
- [x] **P1-06** Arena-Anti-Grind von `campaign.episode` auf Contract-Fenster entkoppelt.
- [x] **P1-07** Arena-HUD mit Banked/Pending/Risiko ergänzt.

### P2

- [x] **P2-01** UI-Persistenztext auf 7 Felder konsistent.
- [x] **P2-02** README-HUD-Beispiel ohne alten `4/10`-Look.

## Nächster QA-Step (Playtest-Reihenfolge)

1. **PVP-01** PvP-only L1 → Cashout → Levelpfad prüfen.
2. **PVP-02** Push-your-luck (Pending-Verlust) durchspielen.
3. **SAVE-01** Strict-Export nach PvP gegen Export-Schema validieren.
4. **XMODE-01** Core → PvP → Rift auf Mode- und Ökonomie-Drift prüfen.

## Checkliste für den nächsten Agenten

- [ ] Playtest-Befunddatei unter `docs/qa/playtest-befund-pvp-only-cashout.md` anlegen.
- [ ] Ergebnisse gegen diese Statusdatei spiegeln (Haken + Kurzfazit pro Testfall).
- [ ] Falls Drift auftaucht: direkt Ticket im Backlog-JSON ergänzen.
