# ZEITRISS® Creator Studio

Der Creator-Modus nutzt dieselbe ZEITRISS-Engine und dieselben 19
Wissensmodule wie das Spiel, aber mit einer anderen Projektanweisung. Er
setzt gespielte Geschichten in Portraits, Gruppenbilder, Wallpaper, Comics,
Motion-Konzepte, Stream-/Social-Pakete und Merch-Entwürfe um.

## Zwei getrennte Projekte

Spiel und Creator Studio niemals im selben Projekt mischen:

| Projekt | Instructions | Projektwissen | Medienfähigkeiten |
| --- | --- | --- | --- |
| Spiel | vollständiger Masterprompt oder `PROJECT_BOOTSTRAP_INSTRUCTIONS.md` | 19 Module; beim Bootstrap zusätzlich `SYSTEM_PROMPT_ONLY.md` | Bild/Video aus |
| Creator Studio | `CREATOR_BOOTSTRAP_INSTRUCTIONS.md` | 19 Module plus `SYSTEM_PROMPT_ONLY.md` | nach Plattform und Bedarf an |

Der Creator-Bootstrap und der Spiel-Bootstrap gehören nie gleichzeitig in
dasselbe Instructions-Feld.

## Quellen laden

Am stärksten arbeitet der Modus mit:

1. einem vollständigen v7-HQ-Save;
2. dem Transkript der gewünschten Szene für exakte Dialoge;
3. bestätigten Referenzbildern für Figurenkontinuität;
4. mehreren Saves/Transkripten für ein Campaign Pack.

Ein Save belegt Zustand und Fortschritt. Nur ein vollständiges Transkript
belegt genaue Dialogzeilen. Zusammenfassungen werden nicht als wörtliche
Zitate ausgegeben.

## Visual Identity

`characters[].visual_identity` speichert eine plattformneutrale
Textbeschreibung. Ein Look wird iterativ entwickelt und mit `Look Lock`
festgeschrieben. Referenzbilder bleiben Sidecar-Dateien; der Save enthält
nur `asset_id`, optional Dateiname/Hash und eine Notiz.

Textanker erhöhen die Wiedererkennbarkeit, garantieren jedoch keine
pixelidentische Ausgabe zwischen Modellen oder Plattformen. Für die beste
Kontinuität zuerst ein Model Sheet stabilisieren und danach dasselbe
Referenzbild für komplexe Gruppen- und Szenenbilder verwenden.

## Typische Starts

- `Creator laden` + Save/Transkript
- `Creator Board`
- `Look Lab für CHR-…`
- `Look Lock`
- `Wallpaper der Crew`
- `Comic Cut aus Mission 4`
- `Motion Cut der Exfil-Szene`
- `Creator Kit für den nächsten Stream`
- `Merch Forge`
- `Creator Pack`
- `Campaign Pack`

Fehlt der Plattform ein Bild- oder Videowerkzeug, erzeugt das Creator Studio
stattdessen ein produktionsfertiges Prompt-, Storyboard- und Continuity-Paket.

## Kanonstatus

- **KANON:** direkt durch Save oder Transkript belegt.
- **ADAPTIERT:** Kamera, Montage, Übergang oder sinngemäßer Dialog.
- **KONZEPT:** nichtkanonische Werbung, Variante oder freie Idee.

Der Creator-Modus erzeugt keinen Spielfortschritt. Eine Look-Lock-Revision
darf nur Visual-Metadaten und Save-Lineage verändern.

## Veröffentlichung und Lizenz

Private, nichtkommerzielle Nutzung folgt der Basislizenz. Monetarisierte
Gameplay-Videos und Streams sind nach der Creator-Zusatzfreigabe erlaubt,
wenn folgende Attribution sichtbar ist:

`ZEITRISS® – © pchospital`

Repository:
`https://github.com/pchospital-lab/ZEITRISS-md`

Merch, Print-on-Demand, bezahlte Assets, eigenständig monetarisierte
Comics/Filme/Artworks, kommerzielle Apps oder Markenintegrationen benötigen
vor Veröffentlichung beziehungsweise Verkauf eine schriftliche Vereinbarung:

`chrononaut@zeitriss.org`
