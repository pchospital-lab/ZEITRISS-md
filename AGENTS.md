# AGENTS-Richtlinien für ZEITRISS-md

## Zweck dieser Datei
Diese Datei richtet sich ausschließlich an KI-gestützte Entwicklerinnen und Entwickler (z. B. Codex, ARXION, ChatGPT). Sie dient als verbindlicher Leitfaden für Beiträge zu diesem Repository. **Sie ist nicht Teil des Runtime-Contents und darf nicht in Spieler:innen-Prompts oder das Spielsystem geladen werden.**

## Geltungsbereich
* Sprache: Verwende Deutsch. Die Ansprache richtet sich nach dem Zielmedium:
  * **Runtime-Content** (`core/`, `gameplay/`, `systems/`, `characters/`): filmischer Ton in der konsequenten Ihr-Form.
  * **Masterprompt** (`meta/masterprompt_*.md`): direkte Du-Ansprache der Spielleitung.
  * **Dev-Dokumentation** (`AGENTS.md`, `CONTRIBUTING.md`, `docs/`, `meta/` abseits des Masterprompts, Tooling-Notizen): sachlich-professioneller Stil ohne Ihr-Form; arbeite bevorzugt mit neutralen Imperativen oder Du-Ansprache.
* Umfang: Gilt für alle Dateien in diesem Repository, sofern kein untergeordnetes Verzeichnis eigene Anweisungen definiert.
* Inhaltliche Trennung: Materialien mit `tags: [meta]`, Dateien im Verzeichnis `docs/` sowie Entwicklungs-Notizen sind reiner Dev-Content. Sie dürfen nicht in In-Game-Texte oder Storymodule eingemischt werden.

## Vorarbeit vor jeder Änderung
1. Lies die betroffenen Dateien vollständig, insbesondere YAML-Header, Szenenstruktur und bestehende Stilvorgaben.
2. Prüfe, ob es zu den Dateien bereits Verweise im `master-index.json` oder in Toolkit-Dokumenten gibt. Passe Querverweise bei strukturellen Änderungen an.
3. Halte dich an die Trennung zwischen Runtime-Content (`core/`, `gameplay/`, `systems/toolkit-*`, `characters/`) und Dev-Dokumentation (`docs/`, `meta/`, Dateien mit `tags: [meta]`).

## Rollenmodell & Kollaboration
- **Repo-Agent (Codex/du)** arbeitet ausschließlich im Git-Repository, befolgt diese `AGENTS.md` sowie `CONTRIBUTING.md` und erstellt Commits bzw. PRs. Keine Runtime-Interaktion.
- **MyGPT „ZEITRISS [Ver. 4.2.2]“** ist die veröffentlichte Spielleitung. Er erhält Masterprompt, README, `master-index.json` und sämtliche Runtime-Module – jedoch keine Dev-Dokumente.
- **Beta-GPT** ist ein privat geklonter MyGPT-Stand für QA. Alle Playtests laufen hier; Ergebnisse werden in `docs/ZEITRISS-qa-audit-2025.md` oder Folgedokumenten erfasst und in Tickets/Tasks überführt.
- **Ingame-KI „Kodex“** bleibt eine reine Spielfigur, die durch den Masterprompt beschrieben wird und keinerlei Repositoriumspflichten trägt.

Halte diese Ebenen strikt getrennt: Laufzeit-Content bleibt im MyGPT, alle Entwicklungsaufgaben erfolgen über das Repo mit Codex.

## Struktur- und Formatregeln
* **YAML-Header**: Jedes Modul benötigt einen vollständigen YAML-Header mit mindestens `title`, `version` und sinnvollen `tags`. Runtime-Module dürfen maximal eine `#`-H1-Überschrift besitzen. Überschriftenhierarchie sauber aufbauen (`##`, `###`, …).
* **Szenenaufbau**: Halte alle in `CONTRIBUTING.md` dokumentierten Invarianten ein. Beispiele:
  * Core-Operationen: 12 Szenen.
  * Rift-Operationen: 14 Szenen in 3 Akten.
  * Jede Szene benennt Konflikt, Ziel und Spur (oder analog definierte Pflichtfelder).
  * Mission 5 benötigt einen Mini-Boss, Mission 10 einen Boss.
* **Nomenklatur**: Nutze aktuelle Begriffe. Beispiel: `Rift-Seeds` anstelle älterer Namen. Erkläre Fachbegriffe bei Bedarf kurz in Klammern.
* **Stil**: Kurze, aktive Sätze. Keine Umgangssprache, keine Marketing-Floskeln. Laufzeitmodule schreiben immersiv und in-world – Dev-Dokumente bleiben nüchtern, klar und ohne Rollenspielton.
* **Verlinkungen**: Kontrolliere interne Links auf korrekte Pfade. Laufzeitmodule dürfen nicht auf Dev-only-Dokumente referenzieren.

## Qualitäts-Checkliste vor dem Commit
- [ ] YAML-Header vorhanden, aktualisiert und valider YAML-Syntax.
- [ ] Struktur-Regeln (Szenenzahl, Akte, Boss/Mini-Boss, Pflichtfelder) erfüllt.
- [ ] Überschriften- und Formatvorgaben eingehalten.
- [ ] Stilprüfung: Filmische, präzise Sprache, keine Meta-Kommentare, Ansprache gemäß Zielmedium (Ihr für Runtime, Du im Masterprompt, neutraler Dev-Ton für Dokumentation).
- [ ] Terminologie konsistent (z. B. `Rift-Seeds`, `HQ`, etc.).
- [ ] Alle Links funktionsfähig, keine Referenzen auf Dev-only-Dateien in Runtime-Modulen.
- [ ] Trennung von Runtime-Content und Dev-Content respektiert.
- [ ] Falls Dateien verschoben/umbenannt wurden: Querverweise (`master-index.json`, Toolkits, README) angepasst.

## Technische Anforderungen
* Führe alle relevanten Lints und Tests aus. Mindestens:
  * `make lint`
  * `make test`
  * `scripts/smoke.sh`
* Stelle sicher, dass `pre-commit`-Hooks sauber durchlaufen. Repariere alle gemeldeten Probleme (z. B. Link-Prüfungen oder Markdown-Formatierung).
* Denke bei Textänderungen an Umlaute in deutscher Schreibweise (ä, ö, ü, ß) und korrekt gesetzte Backticks.
* Prüfe bei Storymodulen gedanklich die Regeln aus `tools/lint_runtime.py` (z. B. Boss-Positionen, Pflichtfelder). Passe Inhalte an, bevor du Änderungen einreichst.

## Umgang mit KI-Reviews
* Reiche Diffs zusammen mit dieser `AGENTS.md` an Review-Agents weiter (z. B. ARXION), damit stilistische und strukturelle Kontrollen automatisch erfolgen können.
* Wenn ein Review-Agent Verstöße meldet, behebe sie vollständig. Hinterlasse erläuternde Kommentare, falls eine Abweichung notwendig und begründet ist.

## Dokumentation von Tests
Notiere in Commit- oder PR-Beschreibungen alle ausgeführten Befehle samt Ergebnis. Bei Fehlermeldungen beschreibe Ursache und Lösung.

## Abschließende Hinweise
* Diese Datei ist verbindlich. Aktualisiere sie bei Prozessänderungen zeitnah.
* Laufzeit-Repositories dürfen nur Content enthalten, der im Toolkit oder in README-Dateien verlinkt ist. Entferne toten Content oder markiere ihn klar als `tags: [meta]`.
* Bewahre die dramaturgische Konsistenz und die Zeitlinien-Logik des ZEITRISS-Universums. Jede Änderung muss mit bestehenden Modulen harmonieren.
