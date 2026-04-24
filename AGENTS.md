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

## Pull Request Descriptions

Flo liest die Description zuerst, bevor er den Diff öffnet. Leere oder einzeilige Bodies werden nicht gemergt.

Struktur doppelt verankert: `.github/PULL_REQUEST_TEMPLATE.md` zeigt im Web-UI-Formular unter einem externen Abschreckungs-Hinweis das leere Gerüst, diese Regeln gelten für alle Maintainer- und Agenten-PRs — egal ob manuell, via `gh pr create --body-file` oder durch einen Agenten erstellt.

### Pflicht-Sektionen (Reihenfolge verbindlich)

- **Was** — 1–3 Zeilen: welche Dateien, was neu/anders.
- **Warum** — 1–3 Zeilen: konkreter Auslöser, welches Problem gelöst wird.
- **Wichtige Entscheidungen** — Bullets: Trade-offs, verworfene Alternativen, Benamungen. Der für Flo wertvollste Teil.
- **Verifikation** — was wurde getestet (Kommando + kurzer Live-Output, z.B. `bash scripts/smoke.sh`). Bei Critic-Review: Rating + Kernkritik.
- **Post-Merge-TODOs** — Bullets; wenn keine vorhanden: Sektion weglassen.
- **Referenzen** — optional, nur wenn vorhanden.

### Regeln

- Deutsch, ganze Sätze. Pfade und Fachbegriffe bleiben technisch.
- Konkret statt generisch: keine "Update docs"-Bodies, keine Commit-Message-Copies.
- Verifikations-Output live kopieren, nicht rekonstruieren.
- Keine Hype-Emoji wie 🚀🔥 bei normalen Änderungen (✓ ❌ ⚠ sind OK).

Referenz-Bodies: siehe aktuelle sauber dokumentierte Merges in `git log main --merges`.



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
