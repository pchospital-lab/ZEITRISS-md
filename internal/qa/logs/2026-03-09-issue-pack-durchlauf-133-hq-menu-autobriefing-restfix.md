---
title: "QA-Log 2026-03-09 – Durchlauf 133 (HQ-Menü Restfix ohne Auto-Briefing)"
status: "abgeschlossen"
run_id: "zr-021-d133"
---

# Kontext

Nach den Durchläufen 131/132 blieb in der SL-Referenz noch ein alter Menütext
stehen (`Auto-HQ & Save ... danach folgt das nächste Briefing`), der dem
vereinbarten Save-Rhythmus widersprach (HQ stabilisieren -> `!save` anbieten ->
neuen Chat empfehlen).

# Umgesetzte Änderungen

1. **HQ-Menü Option 3 entkoppelt vom Auto-Briefing**
   - `core/sl-referenz.md`: Option 3 jetzt als `Auto-HQ -> Save anbieten` mit
     explizitem Hinweis auf **kein** Auto-Briefing im selben Zug.

2. **Save-Contract sichtbar im Fließtext verankert**
   - `core/sl-referenz.md`: Kodex-Hinweis für stabilen HQ-Zustand + Empfehlung
     für neuen Chat nach JSON-Export direkt an die Option gekoppelt.

3. **Folgeschritt als bewusste Entscheidung präzisiert**
   - `core/sl-referenz.md`: Nach dem HQ-Menü nur explizites Fortsetzen,
     Speichern oder HQ-Verbleib; kein impliziter Kampagnensprung.

# Ausgeführte Checks

1. `bash scripts/smoke.sh`

# Bewertung

Der HQ-Rhythmus ist im spielleitungsnahen Runtime-Modul jetzt vollständig
synchron zu Masterprompt/Toolkit/Speichermodul: Save-Angebot statt
Auto-Weiterdruck, klarer Chat-Wechsel-Hinweis und bewusstes Briefing-Follow-up.
