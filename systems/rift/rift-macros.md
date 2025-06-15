---
title: "ZEITRISS 4.0 – Modul 18A: Rift Macros"
version: 4.0
tags: [systems]
---

# ZEITRISS 4.0 – Modul 18A: Rift Macros

Dieses Dokument beschreibt die Makrofunktionen, die im Rahmen des
Core-&-Rift-Loops verwendet werden. Sie sind als pseudocode-artige
Beispiele gedacht und dienen der Implementation in einem künftigen
ZEITRISS-Toolkit.

## ClusterCreate()
Erzeugt 1–2 neue Rift-Seeds, wenn der Paradox-Level 5 erreicht.
Die Seeds werden aus der `RiftSeedTable.json` gewürfelt und dem
Savegame als offener Riss hinzugefügt.

## ClusterDashboard()
Gibt eine strukturierte Liste aller offenen Riss-Einträge aus dem
Spielstand zurück. Beispiel:
```json
"OpenRifts": [
  {"ID":"R-71","Seed":"Emerald Kraken","Severity":1,"Deadline":-10}
]
```

## LaunchRift(id)
Startet eine einzelne Rift-Mission auf Basis des angegebenen Seeds.
Nach Abschluss wird der Eintrag im Savegame entfernt oder bei
Scheitern hochgestuft.

## ScanArtifact()
Eine Spezialfunktion für die Contra-Fraktion. Das erfolgreiche
Scannen eines Artefakts liefert Chrono Units oder Baupläne und erhöht
die `Severity` des betreffenden Risses um +1.
