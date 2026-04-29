# AGENTS.md — Richtlinien für Repo-Agenten

> Diese Datei richtet sich an KI-Agenten die am Repository arbeiten.
> Sie gehört **nicht** zum Spielinhalt und wird nicht in den Wissensspeicher geladen.

## Grundprinzipien

- **Sprache:** Deutsch. Technische Keys/IDs dürfen englisch sein.
- **Runtime vs. Dev:** Spielinhalte (19 WS-Dateien + Masterprompt) strikt von
  Dev-Dokumentation (`docs/`, `internal/`, `meta/archive/`, `runtime.js`, `tools/`) trennen.
- **Jede Regeländerung in den WS-Dateien verankern.** Die KI-SL sieht nur die
  19 Wissensspeicher-Module + Masterprompt. Was nicht dort steht, existiert
  im Spiel nicht.
- **runtime.js = CI-Tests, nicht Spiellogik.** Änderungen dort müssen parallel
  in den WS-Dateien gespiegelt werden.

## Arbeitsablauf

1. **Lesen** — Betroffene Dateien vollständig lesen. Schema-SSOT ist der Masterprompt.
2. **Ändern** — Branch erstellen, Änderungen committen, `bash scripts/smoke.sh` ausführen.
3. **Prüfen** — CI-Smoke muss grün sein. Keine Eigenregeln erfinden.
4. **Pushen** — Branch pushen. Flo reviewed und merged auf GitHub.

## QA-Workflows

Zwei komplementäre Test-Zugänge (beide dokumentiert unter `docs/`):

- **Menschlicher Tester / manueller Playtest:** [`docs/qa/tester-playtest-briefing.md`](docs/qa/tester-playtest-briefing.md)
- **Automatisierter Persona-Playtest (Repo-Agent):** [`docs/testing.md`](docs/testing.md)

Wenn du als Repo-Agent ZEITRISS testen sollst, liest du `docs/testing.md`
(Preset-Infos, Regressions-Matrix, Preflight-Checks, Cross-Findings).

## Pull Request Descriptions

Flo liest die Description zuerst, bevor er den Diff öffnet. Unser Workflow:

- **Ein Commit pro Branch**, dann Squash-Merge durch Flo.
- GitHub nimmt beim Squash-Merge die **Commit-Message** als Default-Vorschlag für den PR-Body und damit auch für die Main-Commit-Message.
- Darum ist der richtige Ort für die Pflicht-Struktur die **Commit-Message selbst**, nicht ein separater PR-Body.

### Pflicht-Struktur (gilt in der Commit-Message)

```
<type>(<scope>): <kurzes Subject, max. 72 Zeichen>

## Was

1–3 Zeilen: welche Dateien, was neu/anders.

## Warum

1–3 Zeilen: konkreter Auslöser, welches Problem gelöst wird.

## Wichtige Entscheidungen

- Bullets: Trade-offs, verworfene Alternativen, Benamungen. Der für Flo wertvollste Teil.

## Verifikation

Konkret getestet mit welchem Kommando? (Dieses Repo: siehe CI-Smoke bzw. Repo-Konvention.) Bei Critic-Review: Rating + Kernkritik.
Nur kompakte Patchnotes-Form:

- 1–3 Kommandos (z. B. `bash scripts/smoke.sh`)
- Je Kommando eine kurze Ergebniszeile (`OK`/`FAIL` + Kernhinweis)
- Keine rohen Voll-Logs, keine mehrfachen `Summary: OK`-Blöcke
- Lange Outputs nur als Artefakt/Anhang referenzieren

## Post-Merge-TODOs

- Bullets; wenn keine vorhanden: Sektion weglassen.

## Referenzen

- Optional, nur wenn vorhanden.
```

### Regeln

- Subject konventional (`fix(x):`, `docs(y):`, `feat(z):`), Imperativ, Deutsch oder Englisch je nach Repo-Konvention.
- Die Sektions-Überschriften (`## Was`, `## Warum`, …) kommen **wörtlich** in den Commit-Body — sie rendern im gemergten `git log` und im GitHub-PR-Preview sauber als Markdown.
- Konkret statt generisch: keine "Update docs"-Bodies, keine Commit-Message-Copies von anderen Commits.
- Verifikations-Output live kopieren, nicht rekonstruieren — aber auf kompaktes Ergebnis kürzen (patchnotes-tauglich).
- Keine Hype-Emoji wie 🚀🔥 bei normalen Änderungen (✓ ❌ ⚠ sind OK).

### Im Web-UI beim PR-Erstellen

1. GitHub lädt zuerst `PULL_REQUEST_TEMPLATE.md` in die Textarea (nur der Abschreckungs-Hinweis für externe Besucher).
2. Darunter — oder als Ersatz — erscheint die letzte Commit-Message als Body-Vorschlag.
3. **Unsere Commit-Message hat die Pflicht-Struktur bereits drin.** Die Textarea kann man so lassen oder das Template oben abtrennen — Flo entscheidet beim Merge.
4. Squash-Merge: GitHub übernimmt Commit-Message als Main-Commit-Body. Fertig lesbar in `git log`.

Historischer Anker: ARXION #504 (gemergt 2026-04-25) war die Main-Commit-Message, die unlesbar wurde — Auslöser für diese Umstellung.

## Pflicht-Invarianten (nicht brechen)

- **Save-Schema v7** — Template im Masterprompt ist SSOT.
- **Boss-Timing:** Core-Mission 5 (Mini), Mission 10 (Boss); Rift-Szene 10.
- **12 Szenen** (Core-Ops), **14 Szenen in 4 Stages** (Rift-Ops).
- **Px-Tabelle:** TEMP 1–2 → +1 alle 2 Miss. | 3–5 → +1 | 6–8 → +2 | 9–11 → +2 | 12–14 → +3.
- **Attribut-Cap:** Max 6 bei Chargen, Summe 18.
- **Equipment:** `{name, type, tier}` — einheitliches Format.
- **Psi-Kosten:** Immer PP UND SYS angeben.
- **LP** (nicht HP) in spieler-sichtigen Texten.
- **"KI-SL"** oder **"Spielleitung"** (nicht "GPT").

## Wissensspeicher-Architektur

- **19 Slots** (Spieler-Handbuch + 18 Runtime-Module) + **Masterprompt** separat als System-Prompt.
- README = GitHub-Landingpage, wird **nicht** in den WS geladen.
- `master-index.json` = Steuerungsdatei für das Setup-Script.
- `speicher-fortsetzung.md` = SSOT-Doku für Save-System (enthält v6-Beispiele als Migrations-Referenz).

## CI-Smoke

```bash
bash scripts/smoke.sh
```

Das ist der einzige Pflicht-Check. Alles andere ist optional.
