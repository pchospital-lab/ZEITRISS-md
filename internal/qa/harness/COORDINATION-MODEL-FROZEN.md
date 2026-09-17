# ZEITRISS Multiplayer — Koordinationsmodell (EINGEFROREN 2026-09-17, Flo-Entscheid)

> Dieses Modell ist **gesetzt**. Nicht neu verhandeln, nicht wegdriften. Bei Konflikt
> gewinnt dieses Dokument. Es bildet den echten Koop-Flow (docs/koop-online-spielen.md) ab.

## Der gefrorene Flow (pro Abschnitt)

1. **Frischer SL-Chat.** Neue Sektion = neuer Chat, JSONs werden reinkopiert, KI-SL öffnet den HQ-Hub.
2. **Anker = Leader.** Der Spieler, der den **ersten** Chrononaut-JSON setzt, ist Leader für den
   **ganzen Abschnitt** (fix, keine Turn-Rotation). Sein Save bestimmt die Kampagne; die anderen
   steigen als Join-Import ein (eigene Kampagne pausiert).
3. **NUR der Leader schreibt** in den Plattform-/SL-Chat. Alle anderen Spieler können den Chat
   **nur lesen**, nie selbst schreiben — sie wirken ausschließlich passiv über den Leader.
4. **Absprache im separaten Kanal** (in echt: Messenger; bei uns: Absprache-Kanal-Datei):
   - **tell** — die Runde bespricht jede Row gemeinsam, der Leader interpretiert + tippt.
   - **strict** — jeder nennt direkt, was seine Figur tut, der Leader gibt es unverändert weiter.
   - In BEIDEN Fällen: der Leader gibt **jede Row** nach Absprache in den Plattform-Chat — eine
     konsolidierte Nachricht pro Runde, nie N Einzelnachrichten der Spieler.
5. **Kein Mid-Mission-Save.** Gespeichert wird nur im HQ.
6. **Level-Up VOR dem Speichern** (Debrief: die eine Aufstiegswahl je Figur, live sichtbar).
7. **HQ-`!save` → N getrennte v7-Blöcke**, einer pro anwesender Figur (kein Sammel-Save).
8. **Persona-State-Lernen dateigestützt:** zusätzlich zum v7-Chrononaut-Save pflegt jede Persona
   ihren eigenen Persona-State-JSON (v2), fortgeschrieben aus dem SL-Ergebnis + eigener Reflexion.
9. **Carry-Forward:** aktualisierte Saves + States sind Input des nächsten Abschnitts (`-current`).
10. **Ein Abschnitt pro Lauf + harter Stopp am Anker:** fertig, wenn ALLE Personas beide JSONs
    aktualisiert + abgelegt haben. Dann kommen wir rein, prüfen, stoßen den nächsten Abschnitt an.

## Regel-Anker (nicht brechen)
- **Mini-Boss an MISSION 5, Episoden-Boss an MISSION 10** — NICHT Szene 5/10 (Core-Ops = 12 Szenen).
- v7-Save-Schema, HUD-Disziplin, Psi immer PP UND SYS, Würfel `1W6 + ⌊Attribut/2⌋ + Talent + Gear`.

## Status der Umsetzung
`faithful_section.py` implementiert Punkte 2–10 bereits datei-gestützt (nur `sl.say(leader_msg)`
postet an die SL — Punkt 3 erfüllt). Offene Layer: „echte autonome Sub-Spieler" als Träger statt
stateless Brains (nächster Schritt nach dem Infrastruktur-Fix).
