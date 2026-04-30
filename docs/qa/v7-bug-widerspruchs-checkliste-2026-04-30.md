# ZEITRISS v7 – Abarbeitungs-Checkliste (Stand 30.04.2026)

Quelle: interner Bericht „ZEITRISS V7 – Bug- und Widerspruchsliste (Shadow-Noir-Flair)“.

## Blocker

- [ ] **#1 Split-/Merge-Kanon konsolidieren**
  - [x] Formulierung „Rift nur nach Episodenende“ im Save-/Flow-Modul entschärft (`launch_rift`).
  - [ ] Alte Legacy-Spuren („nur nach Episodenende“) vollständig in allen betroffenen Modulen bereinigen.
  - [ ] Episodenzähler-Verhalten bei Rift-Split explizit im SSOT verankern.
- [ ] **#2 Optionales Modul als Pflicht-Abhängigkeit auflösen**
  - [ ] Verweise aus `charaktererschaffung-grundlagen.md` auf optionale Inhalte prüfen/reduzieren.
  - [ ] Pflichtwissen in Grundlagen spiegeln oder als optional markieren.
- [ ] **#3 Dev-/QA-Material vom Runtime-Kanon trennen**
  - [ ] Lange QA-Fixtures und Meta-Beratung aus WS-Modulen auslagern oder als Import-only markieren.
- [ ] **#4 Startpfad vereinheitlichen**
  - [ ] Natürlicher Startpfad überall als Standard; `schnell` nur als optionale Fast-Lane.

## Fehler

- [ ] **#5 Legacy-JSON im aktiven Wissensspeicher entschärfen**
- [x] **#6 Veraltete Fraktionswahl-Formulierung bereinigen** (Cinematic-Text sprachlich neutralisiert).
- [ ] **#7 HQ-Entwicklungsdarstellung angleichen**
- [ ] **#8 Slot-/Modul-Zahl synchronisieren** (19 Runtime-Module + Spieler-Handbuch)

## Warnung / Info

- [ ] **#9 Buff-/Temporär-Begriffe vereinheitlichen**
- [ ] **#10 W10-Buff-Halluzinationen mit Negativbeispielen absichern**
- [ ] **#11 Chargen-Save-Gate im Startflow erzwingen**
- [ ] **#12 Probe-Template vor Würfen standardisieren**
- [ ] **#13 SaveGuard-Doku vollständig mit Schema synchronisieren**
- [ ] **#14 Rift-Split: Episode/Stresstransfer eindeutig regeln**
- [ ] **#15 LP/HP-Terminologie inkl. JSON-Watchguard harmonisieren**
- [x] **#16 Cinematic-Elemente als optional markieren** (expliziter Hinweis ergänzt).

## Nächste sinnvolle PR-Reihenfolge

1. Blocker #1–#4 (Regelkonsistenz + Startpfad)
2. Fehler #5–#8 (Kanon-Säuberung)
3. Warnungen/Infos #9–#16 (Watchguards + Feinschliff)
