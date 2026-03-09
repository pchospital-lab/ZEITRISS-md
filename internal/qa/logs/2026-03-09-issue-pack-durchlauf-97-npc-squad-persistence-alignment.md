---
title: "QA-Log 2026-03-09 – Durchlauf 97 (NPC-Squad-Persistenzabgleich)"
status: "abgeschlossen"
run_id: "zr-019-d97"
---

# Kontext

Die Durchläufe 94-96 haben Masterprompt, Save-SSOT, Toolkit und Cinematic-
Start auf persistente NPC-Chrononauten vereinheitlicht. In
`gameplay/kampagnenstruktur.md` blieb jedoch eine Restdrift:
- Solo-Abschnitt implizierte primär Drohnen-Wingman statt explizitem
  `npc-team`-Startpfad.
- NPC-Squad-Kodex sprach noch von „temporären Verbündeten" ohne klaren
  Persistenzhinweis.

# Umgesetzte Änderungen

1. **Solo-Abschnitt an kanonischen Startpfad gebunden**
   - `gameplay/kampagnenstruktur.md`
   - Solo-Start jetzt explizit mit `npc-team 0-4` als Teamkonstellation;
     Drohne nur noch als Fallback, wenn kein Feld-NPC aktiv ist.

2. **NPC-Squad-Kodex auf Kontinuitätsmodell gehoben**
   - `gameplay/kampagnenstruktur.md`
   - Formulierung von „temporären Verbündeten" auf „wiederkehrende
     Verbündete" umgestellt.
   - Klarstellung ergaenzt: bekannte NPC-Chrononauten bleiben als
     Kontinuitätsakteure erhalten und wechseln bei Abwesenheit in HQ-/Offscreen-
     Status statt zu verschwinden.

3. **Prozessspur für Anschlusslaeufe gepflegt**
   - `internal/qa/process/known-issues.md`
   - `internal/qa/process/continuity-redesign-statusmatrix.md`
   - Durchlauf 97 als Evidenz für Modulabgleich dokumentiert.

# Ausgefuehrte Checks

1. `bash scripts/smoke.sh`
   - Ergebnis: **grün**

2. `python3 tools/lint_links.py gameplay internal/qa/plans internal/qa/logs internal/qa/process`
   - Ergebnis: **grün**

# Bewertung

Die NPC-Persistenz ist damit nicht nur im Save-/Toolkit-Kern, sondern auch im
Kampagnenstruktur-Modul konsistent verankert. Der Solo-Einstieg bleibt
anfängerfreundlich (Drohnenfallback), ohne das MMO-Kontinuitätsmodell
abzuschwächen.
