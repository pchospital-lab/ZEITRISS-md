# AGENTS-Richtlinien für ZEITRISS-md

## Zweck dieser Datei
Diese Datei richtet sich ausschließlich an KI-gestützte Entwicklerinnen und Entwickler
(z. B. Codex, ARXION, ChatGPT). Sie dient als verbindlicher Leitfaden für Beiträge zu diesem
Repository. **Sie ist nicht Teil des Runtime-Contents und darf nicht in Spieler:innen-Prompts
oder das Spielsystem geladen werden.**

## Geltungsbereich
- Sprache: Verwende Deutsch. Die Ansprache richtet sich nach dem Zielmedium.
  - **Runtime-Content** (`core/`, `gameplay/`, `systems/`, `characters/`): filmischer Ton in der
    konsequenten Ihr-Form.
  - **Masterprompt** (`meta/masterprompt_*.md`): direkte Du-Ansprache der Spielleitung.
  - **Dev-Dokumentation** (`AGENTS.md`, `CONTRIBUTING.md`, `docs/`, `meta/` abseits des
    Masterprompts, Tooling-Notizen): sachlich-professioneller Stil ohne Ihr-Form; arbeite
    bevorzugt mit neutralen Imperativen oder Du-Ansprache.
- Umfang: Die Regeln gelten für alle Dateien in diesem Repository, sofern kein untergeordnetes
  Verzeichnis eigene Anweisungen vorgibt.
- Inhaltliche Trennung: Materialien mit `tags: [meta]`, Dateien im Verzeichnis `docs/` sowie
  Entwicklungsnotizen sind reiner Dev-Content. Sie dürfen nicht in In-Game-Texte oder
  Storymodule eingemischt werden.

## Vorarbeit vor jeder Änderung
1. Lies die betroffenen Dateien vollständig, insbesondere YAML-Header, Szenenstruktur und
   bestehende Stilvorgaben.
2. Prüfe, ob es zu den Dateien Verweise im `master-index.json` oder in Toolkit-Dokumenten gibt.
   Passe Querverweise bei strukturellen Änderungen an.
3. Halte die Trennung zwischen Runtime-Content (`core/`, `gameplay/`, `systems/toolkit-*`,
   `characters/`) und Dev-Dokumentation (`docs/`, `meta/`, Dateien mit `tags: [meta]`) ein.

## Rollenmodell & Kollaboration
- **Repo-Agent (Codex/du)** arbeitet ausschließlich im Git-Repository, befolgt diese
  `AGENTS.md` sowie `CONTRIBUTING.md` und erstellt Commits bzw. PRs. Keine Runtime-Interaktion.
- **MyGPT „ZEITRISS [Ver. 4.2.2]“** ist die veröffentlichte Spielleitung. Er erhält Masterprompt,
  README, `master-index.json` und sämtliche Runtime-Module – jedoch keine Dev-Dokumente.
- **Beta-GPT** ist ein privat geklonter MyGPT-Stand für QA. Alle Playtests laufen hier;
  Ergebnisse landen in `docs/ZEITRISS-qa-audit-2025.md` oder Folgedokumenten und werden in
  Tickets bzw. Tasks überführt.
- **Ingame-KI „Kodex“** bleibt eine reine Spielfigur. Sie wird durch den Masterprompt beschrieben
  und trägt keinerlei Repositoriumspflichten.

Halte diese Ebenen strikt getrennt: Laufzeit-Content bleibt im MyGPT, alle Entwicklungsaufgaben
erfolgen über das Repo mit Codex.

## Struktur- und Formatregeln
- **YAML-Header**: Jedes Modul benötigt einen vollständigen Header mit mindestens `title`,
  `version` und sinnvollen `tags`. Runtime-Module dürfen maximal eine `#`-H1-Überschrift
  besitzen. Baue die Überschriftenhierarchie sauber auf (`##`, `###`, …).
- **Masterprompt-Ausnahme**: `meta/masterprompt_*.md` steht seit Version 4.2.2 ohne YAML-Header
  im Repo. Halte den Text unter 8 000 Zeichen (≈ 8 k Window) und überprüfe Copy-&-Paste-Workflows
  nach jeder Anpassung.
- **Szenenaufbau**: Befolge alle in `CONTRIBUTING.md` dokumentierten Invarianten.
  - Core-Operationen: 12 Szenen.
  - Rift-Operationen: 14 Szenen in drei Akten.
  - Jede Szene benennt Konflikt, Ziel und Spur (oder analog definierte Pflichtfelder).
  - Mission 5 benötigt einen Mini-Boss, Mission 10 einen Boss.
- **Nomenklatur**: Nutze aktuelle Begriffe (z. B. `Rift-Seeds` anstelle älterer Namen). Erkläre
  Fachbegriffe bei Bedarf kurz in Klammern.
- **Stil**: Schreibe in kurzen, aktiven Sätzen. Keine Umgangssprache, keine Marketing-Floskeln.
  Laufzeitmodule bleiben immersiv und in-world; Dev-Dokumente bleiben nüchtern, klar und ohne
  Rollenspielton.
- **Verlinkungen**: Kontrolliere interne Links auf korrekte Pfade. Laufzeitmodule dürfen nicht auf
  Dev-only-Dokumente referenzieren.

## Qualitäts-Checkliste vor dem Commit
- [ ] YAML-Header vorhanden, aktualisiert und syntaktisch korrekt.
- [ ] Strukturregeln (Szenenzahl, Akte, Boss/Mini-Boss, Pflichtfelder) erfüllt.
- [ ] Überschriften- und Formatvorgaben eingehalten.
- [ ] Stilprüfung bestanden: filmische Sprache für Runtime, Du-Ansprache im Masterprompt,
      sachlicher Ton für Dev-Dokumente.
- [ ] Terminologie konsistent (z. B. `Rift-Seeds`, `HQ`).
- [ ] Alle Links funktionsfähig, keine Referenzen auf Dev-only-Dokumente in Runtime-Modulen.
- [ ] Trennung von Runtime-Content und Dev-Content respektiert.
- [ ] Bei Datei-Verschiebungen: Querverweise (`master-index.json`, Toolkits, README) angepasst.

## Technische Anforderungen
- Führe alle relevanten Lints und Tests aus. Mindestumfang:
  - `make lint`
  - `make test`
  - `bash scripts/smoke.sh`
- Ergänze projektspezifische Checks bei Bedarf (z. B. `python3 tools/lint_runtime.py`).
- Stelle sicher, dass `pre-commit`-Hooks sauber durchlaufen. Repariere alle gemeldeten Probleme
  wie Link-Prüfungen oder Markdown-Formatierung.
- Verwende bei Textänderungen konsequent deutsche Umlaute (ä, ö, ü, ß) und korrekt gesetzte
  Backticks.

## Umgang mit KI-Reviews
- Reiche Diffs zusammen mit dieser `AGENTS.md` an Review-Agents weiter (z. B. ARXION), damit
  stilistische und strukturelle Kontrollen automatisch erfolgen.
- Beta-GPT-Playtests liefern dir vollständige Chatlogs und Findings-Listen. Übernimm die Ergebnisse
  in die QA-Dokumente, gleiche sie mit bestehenden Tickets ab und behebe dokumentierte Abweichungen.
- Vergleichs-KIs mit Repo-Lesezugriff (z. B. ARXION) melden Auffälligkeiten separat. Pflege deren
  Auswertungen in die passenden Dateien ein und dokumentiere Begründungen für unvermeidbare
  Abweichungen in Kommentaren oder PR-Notizen.

## Dokumentation von Tests
Notiere in Commit- oder PR-Beschreibungen alle ausgeführten Befehle samt Ergebnis. Beschreibe bei
Fehlern Ursache und Lösung.

## Abschließende Hinweise
- Diese Datei ist verbindlich. Aktualisiere sie bei Prozessänderungen zeitnah.
- Laufzeit-Repositories dürfen nur Content enthalten, der im Toolkit oder in README-Dateien
  verlinkt ist. Entferne toten Content oder markiere ihn klar als `tags: [meta]`.
- Bewahre die dramaturgische Konsistenz und die Zeitlinien-Logik des ZEITRISS-Universums. Jede
  Änderung muss mit bestehenden Modulen harmonieren.
