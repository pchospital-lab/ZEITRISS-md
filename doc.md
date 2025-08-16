---
title: "Runtime Helper Guide"
version: 1.0
tags: [meta]
---

# Runtime Helper Guide

> Übersicht über zentrale Makros für Kampagnenfluss und Funkchecks.

## Inhaltsverzeichnis
- [Einleitung](#einleitung)
- [Nutzung](#nutzung)
- [API / Makros](#api--makros)
- [Beispiele](#beispiele)
- [Changelog](#changelog)

## Einleitung
Dieses Dokument sammelt kurze Hinweise zu häufig genutzten Runtime-Makros.

## Nutzung
Binde die Makros über `systems/toolkit-gpt-spielleiter.md` ein. Setze das Flag
`GM_STYLE` auf `precision`, wenn strenge Guards aktiv sein sollen.

## API / Makros
### `DelayConflict(threshold=4, allow=[])`
Verzögert Konfliktszenen bis zur angegebenen Szene. Optional erlaubt eine
Liste `allow` frühe Überfälle wie `ambush` oder `vehicle_chase`.

### `comms_check(device, range)`
Prüft Gerät und Reichweite. Wird durch `must_comms(opts)` ergänzt.

### `must_comms(opts)`
Zentraler Guard für Funkverkehr. Wirft `CommsCheck failed: require valid device/range or relay/jammer override.`
bei ungültigem Gerät oder Reichweite.

### `can_open_conflict(type)`
Liefert `true`, wenn Konflikte vor `DelayConflict`-Threshold erlaubt sind
(`ambush`/`vehicle_chase` etc.), sonst `false`.

### `assert_foreshadow(count=2)`
Warnung im PRECISION-Stil, falls weniger als `count` Hinweise für spätere
Bosskämpfe gesetzt wurden.

## Beispiele
```js
// Kurzes Beispiel
DelayConflict(4, ["ambush"]);
```

## Changelog

- 2025-08-15: Erste Version, lint-konform.
