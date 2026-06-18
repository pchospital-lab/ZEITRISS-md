---
title: "Playtest-Evidenz 2026 (automatisierte Persona-Läufe)"
version: 1.0.0
tags: [meta, qa]
---

# Playtest-Evidenz 2026

> Seit 2026-06-18 im Repo (vorher nur im privaten Agent-Workspace).
> Run-Artefakte automatisierter Persona-Playtests — gehört **nicht** zum
> Spielinhalt, **nicht** in den Wissensspeicher.

Jeder Unterordner ist ein Lauf, benannt `YYYY-MM-DD[-HHMM]-<kurzname>`. Die
Harness-Scripts, die diese Läufe erzeugen, liegen unter
[`../../harness/`](../../harness/).

## Was in einem Run liegt

- `_bericht.md` / `AUSWERTUNG.md` / `BEFUND.md` — die kuratierte Auswertung
  (sharebar, gut lesbar — der eigentliche Wert).
- `_live.log` / `*.jsonl` / `*.out` — rohe Turn-für-Turn-Transkripte (Paper-Trail).
- `*.json` / `*.csv` — Save-Snapshots, Token-/Kosten-Metriken.

## Run-Reihen (Überblick)

- **2026-04-19** — episode1-mini (Solo Sarah) + W10-Schwellen-Probe (erste Harness-Runs).
- **2026-04-21/22/23/27** — Gruppen-/Core-Ops-Debugging (phase2-group, mp-tracking,
  verify-runA–D, postfix/runde3b).
- **2026-04-25 persona-driven** — erster Zwei-KI-Architektur-Test (Showcase-Kandidat).
- **2026-05-26/28** — Highlander-Regel, episode1-mini, Pflichtgate-Verify.
- **2026-06-02** — Drift-Audit.
- **2026-06-15** — solo-canary-noob + solo-journey-noob (Onboarding-Spielgefühl).
- **2026-06-16** — split-merge-Matrix (4-1/3-2/resplit/konflikt) + phase3-5er-wallet
  (Wallet-SSOT-Beweis) + g3-Token-Probe.
- **2026-06-17** — coreops-split-merge (smoke/full/merge-only), shared_echoes-Routing.

Lose Top-Level-Dateien (`hqpool-analyse-*`, `HQPOOL-ENTSCHEIDUNG.md`,
`concealment-patch.diff`) sind Analyse-/Design-Artefakte aus den jeweiligen
Sessions, nicht einem einzelnen Run zugeordnet.

## Verhältnis zur älteren Evidenz

Die kuratierte Beta-/Modellvergleichs-Evidenz von 2025–Q1 2026 liegt eine
Ebene höher direkt in [`../`](../) (Ordner `playtest-2026-02-*` …
`playtest-2026-03-17`). Dieser Ordner bündelt die **automatisierten
Harness-Läufe ab April 2026**.
