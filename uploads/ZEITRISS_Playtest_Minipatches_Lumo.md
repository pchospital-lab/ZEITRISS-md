# ZEITRISS – Playtest-Minipatches nach Lumo-Feedback

## Ziel

Nur kleine, risikoarme Text-/Contract-Härtungen. Kein Umbau der Inhalte, kein neues Subsystem, keine Save-Schema-Erweiterung solange der Referenzpfad (OpenWebUI + Sonnet) stabil läuft.

---

## 1) Load-Flow auf HQ-Router ziehen (statt „Mission fortsetzen“)

### Problem

Schwächere Modelle interpretieren einen HQ-DeepSave nach Debrief teils als „offene Mission“.

### Patch-Orte

- `core/sl-referenz.md`
- `systems/toolkit-gpt-spielleiter.md`
- optional `core/spieler-handbuch.md`

### Zieltext

**Ersetze sinngemäß jeden unscharfen Load-Satz durch:**

> **HQ-Load-Standard:** Ein HQ-DeepSave lädt **immer** in einen freien HQ-Zustand,
> nicht in eine laufende Mission. Nach Recap folgt ein kurzer **Load-Router**:
> **Schnell-HQ**, **HQ manuell**, **Briefing anfordern**, **Chronopolis** (falls frei),
> **Rift-Board** (falls frei), **Arena** (falls relevant). Eine Mission gilt nach
> Debrief/HQ-Rückkehr als abgeschlossen und wird nach Load nicht „halb offen“
> weitergespielt.

**Optionaler Techniksatz:**

> **Load-Priorität:** Für Post-Load-Routing ist bei HQ-Saves `continuity.last_seen.location="HQ"`
> maßgeblich; eine gespeicherte Mission wird daraus **nicht** rekonstruiert.

---

## 2) SaveGuard für HQ-Saves entspannen: Transienten normalisieren statt blocken

### Problem

Die aktuellen Guards sind für schwächere Modelle unnötig streng. Wenn ein Modell
Stress/Psi-Heat/SYS-Runtime nicht sauber als HQ-resettiert begreift, blockiert es
fälschlich den Save.

### Patch-Orte

- `systems/gameflow/speicher-fortsetzung.md`
- `systems/toolkit-gpt-spielleiter.md`
- optional kurzer Spiegel in `core/sl-referenz.md`

### Zieltext

**Ergänze direkt beim SaveGuard / HQ-Save-Contract:**

> **HQ-Save-Normalisierung:** Ist `location="HQ"` und liegt **kein** aktiver Einsatz
> mehr vor (`CITY`, Arena, aktives Exfil-, Transfer- oder Queue-State ausgenommen),
> normalisiert der HQ-Save vor dem Export alle **transienten Felder** auf HQ-Basis:
> `stress`, `psi_heat`, `SYS_runtime`, `SYS_used`, `cooldowns`, Exfil-/Timer-Reste.
> Diese Felder blockieren den HQ-Save **nicht**, solange die Crew bereits wieder frei
> im ITI steht.
>
> **SYS-Guard-Korrektur:** `sys_installed` folgt dem Charaktersystem und prüft
> **`sys_installed ≤ attr.SYS`**, nicht `sys_installed == attr.SYS`. Freie SYS-Slots
> sind ein gültiger Charakterzustand und dürfen keinen HQ-Save sperren.

**Pseudocode-Richtung:**

```pseudo
assert state.location == "HQ"
assert not state.city_active
assert not state.arena_active
assert not state.exfil_active
assert state.character.sys_installed <= state.character.attr.SYS
normalize_hq_transients()
serialize_v7()
```

**Wichtig:** Kein neues Save-Feld. Nur Guard-Logik und Serializer-Vertrag härten.

---

## 3) Alias-Härtung für HQ-Orte

### Problem

„Zero Time Lounge“ ist kanonisch, aber Spieler sagen natürlich „Nullzeitbar“.
„Werkstatt“ taucht im Freeplay-Menü auf, ist aber als Hauptort nicht gleich klar.
Schwächere Modelle behandeln solche Begriffe sonst wie neue Orte.

### Patch-Orte

- `core/sl-referenz.md`
- `systems/toolkit-gpt-spielleiter.md`
- optional `core/spieler-handbuch.md`

### Zieltext

> **HQ-Alias-SSOT:**
>
> - `Nullzeitbar` = **Zero Time Lounge** (vollwertiger HQ-Ort, savebar)
> - `Bar` = **Zero Time Lounge**
> - `Werkstatt` = Tech-/Werkstattzone im **Research-Wing** bzw. zugehörigen ITI-Servicezonen
> - `Research-Wing` = Sammelbegriff für **Kodex-Archiv + Med-Lab + Werkstattzonen**
> - `Crew-Quarters` = **Quartiere**
>
> Alle diese Bezeichnungen bleiben **HQ** und sind gültige Save-Kontexte.

---

## 4) Spielerführung nach Debrief: ein klarer Stabilitätspfad

### Problem

Der richtige Rhythmus ist implizit da, aber nicht deutlich genug als „beste Praxis“.
Gerade auf Lumo hilft eine explizite Nach-Debrief-Leitung.

### Patch-Orte

- `core/spieler-handbuch.md`
- `core/sl-referenz.md`
- optional `meta/masterprompt_v6.md`

### Zieltext

> **Empfohlener Stabilitätspfad:**
>
> 1. **Debrief / Score-Screen**
> 2. **Level-Up jetzt abschließen** (`+1 Attribut` **oder** `Talent/Upgrade` **oder** `+1 SYS`)
> 3. Danach **HQ wählen**: Schnell-HQ / manuell / Auto-HQ
> 4. **Speichern**, sobald ihr frei im HQ steht
> 5. **Neuer Chat** für den nächsten Einsatz oder längere HQ-Phase
>
> Der Spieler muss das nicht perfekt timen; die KI-SL soll diesen Pfad aktiv,
> aber unaufdringlich anbieten.

**Kodex-Kurzsatz direkt nach Debrief:**

> `Kodex: Einsatz abgeschlossen. Upgrade jetzt möglich. Danach HQ-Freiraum oder Deepsave.`

---

## 5) ITI-Hierarchie / MMO-Gefühl schärfen

### Problem

Der große, geschäftige ITI-Komplex ist angelegt, aber einzelne Texte machen
Commander Renier noch zu direkt zum Erstkontakt.

### Patch-Orte

- `systems/toolkit-gpt-spielleiter.md`
- `core/sl-referenz.md`
- optional `gameplay/kampagnenstruktur.md`

### Zieltext

> **Dienstweg-Guard:** Rekruten und Feldagenten sprechen im Alltag zuerst mit
> **Dienstpersonal, Archivpersonal, Med-Techs, Quartiermeisterei, Hangar-Dispo
> oder Wachoffizieren**. **Commander Renier** ist **kein Standard-Erstkontakt**,
> sondern erscheint vor allem bei Eskalationen, strategischen Weichenstellungen,
> außergewöhnlichen Leistungen oder fraktionsübergreifenden Krisen.
>
> **Fraktionsführer** bleiben sichtbar und wichtig, aber selten direkt verfügbar;
> meist laufen Termine, Prüfungen und Aufgaben über ihre Leute.
>
> **HQ-Stimmungsregel:** In jedem Heimkehr-Beat 1 sichtbares Zeichen, dass der ITI
> groß und beschäftigt ist: anderes Team im Transit, Archivwagen, Med-Tech-Schicht,
> Sicherheitsdurchsage, Hangarverkehr, gesperrter Gang, Schichtwechsel.

**Rollen-Satz für Renier anpassen:**

> `Commander Arnaud Renier — strategische Leitung, Eskalationen, seltene persönliche Audienzen.`

**Service-Anker aktivieren statt nur optional erwähnen:**

- `ITI-HALDEN` = Wachoffizier / Duty Desk
- `ITI-NOX` = Quartiermeisterei / Beschaffung
- `ITI-JUNO` = Med-Tech / Implantatroutine
- `ITI-CASS` = Hangar-Dispo / Fahrzeugfreigaben

---

## 6) Gegnerbild härten: extern standard, ITI-Verrat selten

### Problem

Das Repo tendiert schon in die richtige Richtung, aber schwächere Modelle greifen
zu oft auf „jemand im ITI ist korrupt“ als Billig-Twist zurück.

### Patch-Orte

- `systems/toolkit-gpt-spielleiter.md`
- optional `core/sl-referenz.md`
- optional `core/spieler-handbuch.md`

### Zieltext

> **Gegnerbild-Default:** Core-Ops richten sich standardmäßig gegen
> **Fremdfraktionen, externe Zeitverschwörungen, Chrono-Kartelle,
> staatsnahe Schattennetze oder historische Machtblöcke**.
> ITI-interne Korruption, Verrat oder Fraktionsdurchstiche sind **seltene Ausnahmen**
> und dürfen nicht als Standarderklärung für Missionsdruck dienen.
>
> **Preserve und Trigger** sind im Grundsatz **ITI-interne Verbündete gegen äußere Bedrohungen**,
> nicht die Standardgegner des Spiels.

---

## 7) Preserve/Trigger: nur patchen, wenn dieser Designwunsch weiter gilt

### Beobachtung

Der aktuelle Textstand behandelt `mixed` als Standard und macht `preserve/trigger`
vor einem Fraktionsübertritt praktisch zweitrangig.

### Nur patchen, falls ausdrücklich gewollt

Wenn der gewünschte Fantasy-Case wirklich bleibt: „Spieler sollen schon ab Start
optional reinen Preserve- oder Trigger-Pool wählen können“, dann nur diesen kleinen
Textpatch machen:

> **Kampagnenmodus:** `mixed` bleibt Standard. Auf ausdrücklichen Wunsch darf der
> Spieler jedoch bereits im **ersten HQ vor dem ersten Briefing** auf
> `preserve` oder `trigger` wechseln. Ein Fraktionsübertritt vertieft diese Wahl
> narrativ, ist aber nicht zwingend nötig, um den Missionspool spielerisch zu fixieren.

Kein anderer Systemumbau nötig.

---

## 8) Anti-Loop-Bremse für lange Missionen

### Problem

Gegen Missionsende neigen schwächere Modelle zu Wiederholungsschleifen.

### Patch-Ort

- `systems/toolkit-gpt-spielleiter.md`

### Zieltext

> **Anti-Loop-Guard:** Wiederhole keinen Druck- oder Hindernis-Beat zweimal
> hintereinander ohne **neue Lageänderung** (neuer Ort, neue Fraktion,
> neuer Ressourcenverlust, neue Verletzung, neue Information oder klares
> Exfil-Fenster). Wenn das Primärziel erfüllt ist und der Spieler keinen
> bewussten Umweg erzwingt, kippt die Regie zügig in **Cleanup / Exfil / Heimkehr**
> statt in einen neuen Vollkreis aus denselben Stakes.

---

## Meine Priorität (von höchstem Nutzen / geringstem Risiko)

1. **Load-Flow auf HQ-Router ziehen**
2. **SaveGuard-Transienten normalisieren statt blocken**
3. **Alias-Härtung für Nullzeitbar / Werkstatt / HQ-Orte**
4. **Renier aus der Erstkontakt-Rolle rausnehmen + Dienstweg-Guard**
5. **Externe Gegner als Default explizit härten**
6. **Anti-Loop-Guard**
7. **Preserve/Trigger nur patchen, wenn der ursprüngliche Designwille wirklich wieder gilt**

## Was ich NICHT ändern würde

- kein neues Save-Schema-Feld nur für „post_debrief“ / „skill pending“
- keinen Ausbau des Wissensspeichers
- keine weiteren HQ-Subsysteme
- keine neue Fraktionsmechanik
- keine zusätzliche Speichertiefe
