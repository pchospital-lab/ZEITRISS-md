---
title: "Uploads-Ablage"
version: 1.0.0
tags: [meta]
---

# Uploads-Ablage

Dieser Ordner ist eine **Eingangsablage** für externe Review-/Upload-Artefakte.

## Arbeitsregel

1. Upload-Artefakt hier ablegen.
2. Relevante Punkte in `internal/qa/process/` bzw. `docs/qa/` überführen.
3. Operativen Status ausschließlich in den QA-Dokumenten pflegen.
4. Upload-Artefakte ohne verbleibende Referenz aus `uploads/` entfernen.

Damit bleibt klar: **Uploads sind Quelleingang**, die verbindliche Umsetzung und
Nachverfolgung passiert unter `internal/qa/`.

## Retention (Stand 2026-04-28)

Im Repo bleiben nur Uploads, die mindestens eines erfüllen:

- werden von bestehenden QA-/Archivdokumenten referenziert, oder
- sind durch einen Watchguard explizit als historischer Snapshot verankert.

Nicht mehr referenzierte Uploads werden entfernt, sobald ihr Inhalt in
`internal/qa/` oder `docs/qa/` dokumentiert ist.
