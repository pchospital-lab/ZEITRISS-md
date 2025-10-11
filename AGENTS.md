# AGENTS-Richtlinien für ZEITRISS-md

## Zweck & Fokus
Diese Datei adressiert ausschließlich Repo-Agenten wie dich (Codex, ChatGPT, ARXION). Sie bündelt
agentenspezifische Pflichten und verweist für allgemeine Beitragsregeln, QA-Abläufe und Compliance
auf [CONTRIBUTING.md](CONTRIBUTING.md). **AGENTS.md gehört nicht zum Runtime-Content und darf nicht
in Prompts oder Spielsysteme übernommen werden.**

## Grundprinzipien
- Arbeite durchgehend auf Deutsch und beachte die Zielgruppenansprache gemäß
  [CONTRIBUTING.md → Sprach- & Formatregeln](CONTRIBUTING.md#grundregeln).
- Prüfe vor jedem Eingriff, ob unterhalb des Zielpfads zusätzliche Richtlinien existieren.
- Halte Dev-Dokumente (`tags: [meta]`, `docs/`, `meta/` außerhalb des Masterprompts) strikt von
  Runtime-Content getrennt.
- **Spiegle jede Laufzeitänderung (runtime.js, Tools) sofort in den Wissensmodulen (README, Runtime-Markdowns, Toolkit-Makros)**
  und dokumentiere den Mirror in Commit/PR sowie – falls noch offen – im QA-Log.
- Das Pflicht-Testpaket für Repo-Agent:innen ist ausschließlich in
  [CONTRIBUTING.md → Verpflichtende Prüfungen](CONTRIBUTING.md#verpflichtende-pruefungen)
  definiert; QA-Reports müssen es nicht mehr als To-do aufführen.

## Arbeitsablauf des Repo-Agenten
1. **Vorbereitung** – Lies die betroffenen Dateien vollständig und gleiche Strukturvorgaben mit der
   [Qualitäts- und Compliance-Checkliste](CONTRIBUTING.md#qualitaets-und-compliance-checkliste)
   ab. Pflege bei strukturellen Änderungen die Verweise in `master-index.json`, README und
   Toolkits.
2. **Umsetzung** – Entwickle Änderungen im Repo, dokumentiere Quellen (z. B. QA-Logs) in Commit- und
   PR-Texten und halte die Rollenabgrenzung aus
   [README → Dokumenten-Landkarte](README.md#dokumenten-landkarte) ein.
   Laufzeitfeatures müssen parallel als Regel- oder Prozessbeschreibung in den Wissensmodulen landen,
   damit produktive GPTs ohne lokale Skripte identisch reagieren.
3. **Prüfung** – Führe den in [CONTRIBUTING.md → Verpflichtende Prüfungen](CONTRIBUTING.md#verpflichtende-pruefungen)
   beschriebenen Testumfang aus. Ergänze projektspezifische Checks (`tools/`, `scripts/`) bei Bedarf.
4. **Dokumentation** – Notiere alle Befehle samt Ergebnis im Commit/PR, aktualisiere QA-Belege und
   melde verbleibende Abweichungen transparent.

## Kollaboration & Übergaben
- **Maintainer:innen** verantworten Uploads und Plattform-Spiegelungen laut
  `docs/maintainer-ops.md`. Übernimm ihre QA-Reports unverändert in die internen Dokumente.
- **Tester:innen** folgen `docs/qa/tester-playtest-briefing.md`. Du synchronisierst Findings mit
  `internal/qa/audits/` und `internal/qa/plans/`.
- **Beta-GPT** dient ausschließlich QA-Läufen. **MyGPT ZEITRISS** erhält nur Runtime-relevante
  Artefakte; Dev-Dokumente bleiben intern.
- **Ingame-KI „Kodex“** ist reine Spiellore ohne Repositoriumspflichten.

Halte Artefakt-Übergaben sauber getrennt: Maintainer:innen und Tester:innen liefern Chatlogs,
Checklisten und Protokolle, du implementierst die daraus abgeleiteten Tasks im Repo.

## Dokumentation & Nachverfolgung
- Archiviere QA-Logs, Fahrpläne und Audits an den vorgesehenen Orten unter `internal/qa/`.
- Verweise in Commits auf relevante QA- oder Review-Dokumente.
- Stimme dich bei Prozessänderungen eng mit den Maintainer:innen ab und aktualisiere diese Datei
  nur für agentenspezifische Anpassungen. Allgemeine Regeln pflegst du in
  [CONTRIBUTING.md](CONTRIBUTING.md).
