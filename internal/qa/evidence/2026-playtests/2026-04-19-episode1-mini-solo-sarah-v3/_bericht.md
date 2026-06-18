# Mini-Playtest v3: Episode 1 Solo Lvl 1 (Sarah)

**Datum:** 2026-04-19 18:58
**Modell:** anthropic/claude-sonnet-4.6 + ZEITRISS v4.2.6 Uncut (gepatcht: Chargen-Save-Gate)

## Verbesserungen v3

- Chat 2 HQ-Erkundung: strikt 4 Turns, dann Save
- Mission-Chats: injizieren Turn 1 Briefing-Request (kein passiver Sarah-Dialog)
- Mission-Persona: handlungsorientiert, nicht HQ-RP-neugierig
- Score-Screen als Mission-Ende-Primaersignal
- Turn-Budget Mission: 32 (12 Szenen + Briefing + Debrief + Puffer)

## Kette

| Chat | Turns | Sauber beendet | Save |
|------|-------|-----|-----|
| Chat 1: Chargen | 4 | JA | JA |
| Chat 2: HQ-Erkundung | 5 | JA | JA |
| Chat 3: Mission 1 | 32 | NEIN | JA |
| Chat 4: Mission 2 | 32 | NEIN | NEIN |
| Chat 5: Mission 3 | 32 | NEIN | NEIN |

**Gesamt-Turns:** 105  |  **Erfolgreich:** 2/5

## Save-Groessen

- `save-after-chargen.json`: 3969 bytes
- `save-after-hq.json`: 5224 bytes
- `save-after-mission1.json`: 7709 bytes
