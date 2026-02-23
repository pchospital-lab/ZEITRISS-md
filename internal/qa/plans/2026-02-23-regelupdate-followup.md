# Follow-up Fahrplan – Regelupdate Terminologie/Chronopolis/Save (2026-02-23)

## Kontext
Dieses Follow-up protokolliert offene QA-Befunde aus dem Regelupdate-Lauf
(EP→XP-Terminologie, Chronopolis-Tod, Save-Taktung, Gruppen-Todesentscheid).

## Offene Punkte aus Pflichtprüfungen
- ✅ Erledigt: Legacy-Dokument archiviert unter
  `meta/archive/speicher-fortsetzung.legacy.md` (nicht mehr im Runtime-Pfad).
- ✅ Erledigt: `migrate_save` ist wieder explizit im Save-Modul dokumentiert,
  `tools/lint_runtime.py` und `GM_STYLE=verbose tools/lint_runtime.py` laufen
  grün.
- ✅ Erledigt: `make lint`, `bash scripts/smoke.sh`,
  `python3 scripts/lint_doc_links.py` und `python3 scripts/lint_umlauts.py`
  laufen vollständig durch.
- ✅ Erledigt: `tools/test_economy_merge.js` nutzt im Merge-Test jetzt ein
  schema-konformes `incomingSave.ui.action_mode="uncut"`; `make test` läuft
  wieder grün.

## Nachzug ZR-011/ZR-012 + Kurskorrektur ZR-014 – HUD-UX, Seed-Status, Tonalität

Als nächster Deep-Research-Folgeschritt nach ZR-013 wurde der verbleibende
P2/P3-Regeldrift in Runtime-Modulen reduziert:

- `characters/hud-system.md`: Paradoxon-Abschnitt auf **HUD-UX statt
  Kernregel** geschärft (kein Default-Px-Malus im Anzeige-Modul; SSOT-Verweis
  ins Spieler-Handbuch).
- `gameplay/kampagnenstruktur.md` +
  `systems/gameflow/speicher-fortsetzung.md`: Seed-Status normalisiert auf
  `locked_until_episode_end/open/closed`, inklusive Dev-Checkliste und
  Save-Schema-Text.
- `gameplay/kreative-generatoren-missionen.md`: Kurskorrektur umgesetzt;
  zusätzlicher Sensitivitäts-Schalter entfernt und ZEITRISS-Standard als
  hartes 18+-Setting textlich klargestellt (kein optionaler Safety-Toggle).

Damit gelten ZR-011 und ZR-012 als nachgezogen; ZR-014 wurde als
Produktentscheidung **nicht übernommen** (kein Runtime-Requirement).

## Abschlussstand
Der Follow-up-Block ist abgeschlossen; es bestehen aktuell keine offenen
Pflichtprüfungs-Punkte mehr aus dem Regelupdate-Lauf vom 2026-02-23.

## Nachtrag Upload-Abgleich (Deep-Research-Report(4))

Die im Upload `uploads/deep-research-report(4).md` priorisierten Starttickets
wurden gegen den aktuellen Repo-Stand gegengeprüft und als abgeschlossen
markiert. Der Upload ist damit als Eingangsdokument archiviert; operative
Steuerung erfolgt ausschließlich über `internal/qa/plans/` und
`internal/qa/logs/`.

- ✅ ZR-001: Exploding-/Burst-Cap-SSOT vereinheitlicht.
- ✅ ZR-002: Px-Default ohne automatischen Strafabzug vereinheitlicht.
- ✅ ZR-003: Px-Scope für solo/npc-team vs. gruppe präzisiert.
- ✅ ZR-004: HQ-Rückkehr als Loop-Invariante durchgezogen.
- ✅ ZR-005: Chronopolis-Todesregel ohne Free-Respawn vereinheitlicht.
- ✅ ZR-006: Physicality-Gate vereinheitlicht (Armbänder nur als Tracker,
  kein Handgelenk-HUD).

- ✅ ZR-010: Korrigiert auf "Mirror ohne Auslagerung" (Runtime-Makros bleiben vollständig im Toolkit; `internal/runtime/toolkit-runtime-makros.md` bleibt reiner QA-/Review-Spiegel).

## Nachzug Entscheidung GRP/TEMP (2026-02-23)

Deep-Research-Punkt „Team-TEMP im Gruppenspiel unklar“ ist jetzt als
SSOT-Entscheidung festgezogen und in Runtime + Wissensmodule gespiegelt:

- **GRP = Gruppe**.
- **Team-TEMP** im Modus `gruppe` wird als **aufgerundeter Durchschnitt**
  geführt: `TEMP_gruppe = ceil(sum(temp aller aktiven Charaktere) / anzahl)`.
- Der Teamwert steuert **Px-ETA** und TEMP-basierte Frequenzen (z. B.
  Fahrzeug-Verfügbarkeit).
- „Forward-only mode“ wird **nicht** als Default oder Pflichtmodus
  nachgezogen; der Hinweis im Upload bleibt reine Audit-Frage ohne Umsetzung.

## Nachzug ZR-007 – Heilungs-Balance & LP-Terminologie (2026-02-23)

Im Zuge der weiteren Abarbeitung von `uploads/deep-research-report(4).md`
wurde ZR-007 im Runtime-Content vollständig nachgezogen (Terminologie +
Heilungs-Balance im Medikit-Standard).

- `characters/ausruestung-cyberware.md`: „Nano-Bindepflaster" wurde bereits auf
  **4 LP sofort** vereinheitlicht; zusätzlich wurde das **Medikit** auf **1W6 LP**
  (außerhalb des Kampfes) mit Limit **max. 1× pro Charakter und Mission**
  gesetzt.
- `characters/zustaende.md`: Stress-/Heilungsabschnitt sprachlich auf LP
  vereinheitlicht („Spieler achten auf LP ...") und der Medikit-Standard
  (1W6 LP, 1× pro Charakter/Mission) explizit gespiegelt.

Damit ist ZR-007 im Upload-Block inhaltlich abgeschlossen; ein optionaler
Feinschliff bleibt nur für zukünftige Meta-Balance-Läufe vorbehalten.

## Nachzug ZR-006 – Physicality Gate (Tracker ja, Handgelenk-HUD nein)

Im nächsten Schritt der Upload-Abarbeitung wurde der Drift zwischen Core- und
HUD-/Toolkit-Regelwerk zur Gerätephysik bereinigt.

- `core/zeitriss-core.md`: Hardware-Abschnitt auf den SSOT aus
  `characters/hud-system.md` und `systems/toolkit-gpt-spielleiter.md`
  gezogen. Armbänder bleiben als Tracker zulässig, HUD-Projektion bleibt
  exklusiv auf Linse/Comlink/Terminal; externe Projektoren bleiben
  ausgeschlossen.

Damit ist ZR-006 als inhaltlicher Terminologie-/Regelabgleich abgeschlossen;
damit sind alle priorisierten Upload-Punkte (ZR-001 bis ZR-007 sowie ZR-010) im
aktuellen Follow-up als abgeschlossen dokumentiert.

## Nachzug ZR-008 – Fremdfraktion statt harter Alien-Kanon (2026-02-23)

Als nächster sinnvoller Deep-Research-Folgeschritt wurde die Tonalitätsfrage aus
`uploads/deep-research-report(4).md` (ZR-008) in den Gameplay-Modulen bereinigt.

- `gameplay/kampagnenuebersicht.md`: Lore-Text zu „außerirdischem Kontakt" und
  „Galaktischer Föderation" auf **Cover-/Gerüchte-Status** gestellt, damit der
  Default-Sci-Fi-Thriller konsistent bleibt und optionale Fremdlore nicht als
  harter Kanon gelesen wird.
- `gameplay/kreative-generatoren-missionen.md`: Einzelne Generator-Beispiele von
  „Alienvolk/Alien-Relikt/Fremdes Leben" auf **Fremdfraktion**, **Fremd-Relikt**
  und **Unbekannte Signaturen** harmonisiert.

Damit ist ZR-008 im laufenden Follow-up als abgeschlossen nachgezogen; die
P0/P1-Closure bleibt unverändert, ergänzt um diesen P2-Konsistenzpass.


## Nachzug ZR-009 – Level-Up-Regel konsolidiert (2026-02-23)

Als nächster sinnvoller Deep-Research-Folgeschritt wurde die offene
Progressions-Drift (Attribut vs. Talent vs. SYS) im Runtime-Textkorpus
vereinheitlicht.

- `core/zeitriss-core.md`: Aufstiegsregel als SSOT präzisiert:
  pro Stufe genau **eine** Wahl (`+1 Attribut` **oder** `Talent/Upgrade`
  **oder** `+1 SYS`).
- `characters/charaktererschaffung-grundlagen.md`: Level-Up-Abschnitt auf
  dieselbe Dreifach-Wahl harmonisiert; frühere "optional beides"-Lesart
  entfernt.
- `core/sl-referenz.md`: Default ohne Doppel-Upgrades pro Level klargestellt.
- Spiegelung in Wissens-/Runtime-Modulen nachgezogen:
  `core/spieler-handbuch.md` (Debrief-Upgrade-Hinweis) und
  `systems/toolkit-gpt-spielleiter.md` (HQ-Loop + Level-Up-HUD-Toast).

Damit ist ZR-009 aus `uploads/deep-research-report(4).md` im laufenden
Follow-up als abgeschlossen nachgezogen; der Upload-Block bleibt damit
konsistent im SSOT-Pfad dokumentiert.

## Nachzug ZR-013 – Glossar-SSOT & Terminologie-Links (2026-02-23)

Als nächster sinnvoller Deep-Research-Folgeschritt wurde die offene
Terminologie-Bündelung (ZR-013) umgesetzt, um Drift zwischen HUD, Kampagnen-
und Core-Texten zu reduzieren.

- Glossar-SSOT in `core/spieler-handbuch.md` gebündelt (Kernkürzel SG, LP, SYS,
  PP, TEMP sowie Loop-Kürzel Px, CU, FS, IA, RW inkl. Team-TEMP-Formel).
- Spiegelung in Wissensmodulen ergänzt:
  `core/spieler-handbuch.md`, `characters/hud-system.md` und
  `gameplay/kampagnenstruktur.md` verlinken nun explizit auf das Glossar-SSOT.
- `gameplay/kampagnenstruktur.md` wurde zusätzlich auf die konsolidierte
  Level-Up-Wahl (`+1 Attribut` oder `Talent/Upgrade` oder `+1 SYS`) nachgezogen.
- Struktur-/Linkpfad aktualisiert: `README.md`, `characters/hud-system.md` und
  `gameplay/kampagnenstruktur.md` verweisen auf das Glossar im Spieler-Handbuch.

Damit ist ZR-013 aus `uploads/deep-research-report(4).md` im laufenden
Follow-up als abgeschlossen dokumentiert.
