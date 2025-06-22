---
title: "ZEITRISS 4.0 – Codex-Suchfilter"
version: 4.0
tags: [systems]
---

# Codex-Suchfilter nach Tags

Die Codex-Datenbank wächst schnell und enthält inzwischen weit über hundert Einträge. Um langes Scrollen zu vermeiden, können Spieler die Suche nun per **Tag-Filter** einschränken. Die Filter arbeiten additiv und akzeptieren folgende Kategorien:

- **Epoche** (z.B. `1850-1914`, `1950-1989`, `2080+`)
- **Technikstufe** (I–V)
- **Gegnertyp** (z.B. `Konzern`, `Temporalwesen`)

Ein Kommando wie `codex suche epoche:1950-1989 gegner:Konzern` listet nur Einträge, die beide Tags besitzen.

```jsonc
// Beispiel für einen Codex-Eintrag mit Tags
{
  "titel": "Orbital-Wachdrohne",
  "tags": ["2080+", "Tech-IV", "Konzern"]
}
```

Die Filter funktionieren serverseitig, daher ist die Trefferliste sofort sortiert. Mehrere Tags können kombiniert werden. Ohne Angaben zeigt `codex suche` wie gewohnt alle Ergebnisse.
