---
title: "Beitragsrichtlinien"
version: 2.0.0
tags: [meta]
---

# Beitragsrichtlinien

## Für Außenstehende

**Pull Requests werden nicht angenommen.** ZEITRISS wird vom Maintainer direkt
gepflegt. Wenn dir etwas auffällt — Regelfehler, Balancing, Ideen, Tippfehler —
erstelle bitte ein [Issue](https://github.com/pchospital-lab/ZEITRISS-md/issues).

Sicherheitsmeldungen: siehe [SECURITY.md](SECURITY.md).

## Für den Maintainer & Repo-Agenten

### Workflow

1. Branch von `main` erstellen.
2. Änderungen committen (prägnante Commit-Nachrichten, Imperativ).
3. `bash scripts/smoke.sh` ausführen — muss grün sein.
4. Branch pushen → auf GitHub squash & merge.

### Was wo hingehört

| Inhalt                        | Ort                                             |    Im Wissensspeicher?    |
| ----------------------------- | ----------------------------------------------- | :-----------------------: |
| Spielregeln, Mechaniken, Lore | `core/`, `characters/`, `gameplay/`, `systems/` |     ✅ Ja (19 Slots)      |
| System-Prompt für die KI-SL   | `meta/masterprompt_v6.md`                       | Separat als System-Prompt |
| GitHub-Landingpage            | `README.md`                                     |          ❌ Nein          |
| Setup-Anleitung               | `docs/setup-guide.md`                           |          ❌ Nein          |
| CI-Tests, Linter              | `tools/`, `scripts/`, `runtime.js`              |          ❌ Nein          |
| Playtest-Evidence             | `internal/qa/evidence/`                         |          ❌ Nein          |
| Archiv/Legacy                 | `meta/archive/`                                 |          ❌ Nein          |

### Pflicht-Checks

```bash
bash scripts/smoke.sh    # Einziger Pflicht-Check
```

Optional: `python3 -m unittest -q`, `python3 tools/lint_runtime.py`

### Formatierung

- UTF-8, max. 100 Zeichen pro Zeile.
- YAML-Header bei allen Modulen (Ausnahme: Masterprompt).
- Bindestriche (`-`) als Aufzählungszeichen.
- Deutsche Umlaute im Fließtext, ASCII-Ersatz nur in Code/IDs.

### Invarianten (nicht brechen)

Siehe [AGENTS.md](AGENTS.md#pflicht-invarianten-nicht-brechen).

### Begriffe

- **LP** (nicht HP) in spieler-sichtigen Texten.
- **KI-SL** oder **Spielleitung** (nicht "GPT").
- **Vier Stages** bei Rift-Ops (nicht "drei Akte").
- **characters[]** im Save (nicht `party.characters[]`).

© 2025-2026 pchospital – ZEITRISS® – private use only. See LICENSE.
