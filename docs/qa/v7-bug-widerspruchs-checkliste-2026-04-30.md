# ZEITRISS v7 – Abarbeitungs-Checkliste (Stand 30.04.2026)

Quelle: interner Bericht „ZEITRISS V7 – Bug- und Widerspruchsliste (Shadow-Noir-Flair)“.

## Blocker

- [x] **#1 Split-/Merge-Kanon konsolidieren**
  - [x] Formulierung „Rift nur nach Episodenende“ im Save-/Flow-Modul entschärft (`launch_rift`).
  - [x] Alte Legacy-Spuren („nur nach Episodenende“) in den SSOT-Startregeln bereinigt (Toolkit-Abschnitt Core vs Rift).
  - [x] Episodenzähler-Verhalten bei Rift-Split explizit im SSOT verankern.
- [x] **#2 Optionales Modul als Pflicht-Abhängigkeit auflösen**
  - [x] Verweise aus `charaktererschaffung-grundlagen.md` auf optionale Inhalte geprüft; keine Pflicht-Abhängigkeit auf Modul 3B mehr im Default-Startpfad.
  - [x] Pflichtwissen verbleibt in den Grundlagen; optionale Vertiefungen bleiben als Zusatzmaterial gekennzeichnet.
- [ ] **#3 Dev-/QA-Material vom Runtime-Kanon trennen**
  - [ ] Lange QA-Fixtures und Meta-Beratung aus WS-Modulen auslagern oder als Import-only markieren.
- [x] **#4 Startpfad vereinheitlichen**
  - [x] Natürlicher Startpfad als Standardpfad verankert; `schnell` bleibt explizit optionale Fast-Lane (SSOT-Startregeln + Verweis bereinigt).

## Fehler

- [ ] **#5 Legacy-JSON im aktiven Wissensspeicher entschärfen**
- [x] **#6 Veraltete Fraktionswahl-Formulierung bereinigen** (Cinematic-Text sprachlich neutralisiert).
- [x] **#7 HQ-Entwicklungsdarstellung angleichen**
  - [x] HQ-Kanon im Kampagnenmodul als statische Nullzeit-Anlage ohne Basisbau verankert; Fortschritt nur über Freigaben/Beziehungen.
- [x] **#8 Slot-/Modul-Zahl synchronisieren**
  - [x] Terminologie auf 19 Wissensspeicher-Slots vereinheitlicht (Spieler-Handbuch + 18 Runtime-Module; Masterprompt separat).

## Warnung / Info

- [x] **#9 Buff-/Temporär-Begriffe vereinheitlichen**
  - [x] `core/wuerfelmechanik.md` ergänzt: Buff = temporärer Modifikator (synonym); Buffs ändern nie die Würfelart, sondern zählen additiv nach dem Wurf.
  - [x] Klarstellung ergänzt: Talent-„Schwelle“ meint narrativen Tierfortschritt, keine separate Würfelschwelle.
- [x] **#10 W10-Buff-Halluzinationen mit Negativbeispielen absichern**
  - [x] SSOT-Würfelregel um explizites Negativbeispiel ergänzt (`GES 9 + Injektor +3` bleibt W6).
  - [x] Formelpfad präzisiert: temporäre Boni additiv nach dem Wurf, kein Würfelarten-Wechsel durch Buffs.
- [x] **#11 Chargen-Save-Gate im Startflow erzwingen**
  - [x] Masterprompt erzwingt nach Chargen im klassischen Pfad: Pflicht-HQ-Heimkehr → einmaliges Kodex-Save-Angebot → HQ-Menü mit expliziter `!save`-Option.
  - [x] Briefing wird erst nach expliziter Spielerentscheidung erlaubt; Fast-Lane bleibt als dokumentierte Ausnahme ohne Chargen-Save-Gate.
- [x] **#12 Probe-Template vor Würfen standardisieren**
  - [x] Masterprompt ergänzt: verbindliche Kodex-Ansage „Probe-Template“ vor jeder riskanten Probe.
  - [x] Würfelmodul ergänzt: gleiches Pflicht-Template als Regelanker gegen Schwellen-/Buff-Halluzinationen.
- [ ] **#13 SaveGuard-Doku vollständig mit Schema synchronisieren**
- [x] **#14 Rift-Split: Episode/Stresstransfer eindeutig regeln**
  - [x] SSOT ergänzt: `launch_rift` erhöht `campaign.episode` nicht, Rift läuft als `phase:"rift"`.
  - [x] SSOT ergänzt: Stress-Reset beim HQ-Transfer folgt dem gespeicherten HQ-Basiswert.
- [ ] **#15 LP-vs-Legacy-Terminologie inkl. JSON-Watchguard harmonisieren**
- [x] **#16 Cinematic-Elemente als optional markieren** (expliziter Hinweis ergänzt).

## Nächste sinnvolle PR-Reihenfolge

1. Blocker #1–#4 (Regelkonsistenz + Startpfad)
2. Fehler #5–#8 (Kanon-Säuberung)
3. Warnungen/Infos #9–#16 (Watchguards + Feinschliff)
