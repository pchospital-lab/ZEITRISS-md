# Critic-Review: feat/cineastische-kaempfe

**Modell:** Opus 4.7 (thinking high)  |  **Gelaufen:** 2026-05-27T20:17+02:00  |  **Hash (Base):** e593b507 · Patch uncommitted (Working-Tree-Diff, +123/-0 über 3 Files)

## Verdict

**GO mit Mini-Fix.** Patch trifft das Highlander-Feedback präzise, bricht die §E-Probe-Invariante nicht, ist sauber als Skirmish-Pflichtgate positioniert. Fünf Mini-Fixes nötig vor Merge: (1) Mode-Kollision mit `PRECISION`, (2) NSC-Begriff für Squad-Modus weichen, (3) Beat-2-Probe vollständig zeigen, (4) Toolkit-Kampfsequenz-Eintrag (§5) und sl-referenz Action-Contract-Block nachziehen, (5) ein verirrter Cross-Link in `masterprompt §C` zeigt auf "Cineastische Schlachten" statt "Cineastische Kampf-Beats". Kein Showstopper.

## Smoke

✓ `git diff --stat` plausibel (+98 / +15 / +10).
✓ Anchor `{#cineastische-kampf-beats}` existiert genau einmal in `core/wuerfelmechanik.md`.
✓ `masterprompt_v6.md`-Insertion sitzt direkt nach Exfil-Stress-Pflichtgate (Z.140 ff), Bullet-Tiefe konsistent mit Nachbarn.
✓ `kampagnenstruktur.md`-Insertion zwischen Pacing-Absatz und Staffel-Skeleton, kein Strukturbruch.
✗ Masterprompt-Insertion Z.156 verweist auf `core/wuerfelmechanik.md §Cineastische Schlachten` — gemeint ist aber `§Cineastische Kampf-Beats`. Falscher Anchor → SL liest nachher das Massengefechts-Kapitel statt das neue.

## Befunde (5)

### 1. Konflikt-Abgrenzung Skirmish vs. Massengefecht — **OK mit einer Falsch-Referenz**

`core/wuerfelmechanik.md` Z.398 sagt explizit *„Einzelkämpfe und Skirmishes (zwei bis sechs Gegner, kein Massengefecht)"*. Die bestehende `## Cineastische Schlachten`-Sektion (Z.495+) ist für **Massengefechte/Erfolgspool/Waagschale**. Sauber abgegrenzt — kein SL wird die Mechanik verwechseln, weil der Beat-Pool keine Erfolgspool-Sprache benutzt und das Massengefechts-Kapitel keine Pflicht-Inkarnationen einführt.

**ABER:** `masterprompt_v6.md` Z.156 schließt mit *„Vollständige Spezifikation und Beat-Pool: `core/wuerfelmechanik.md` §Cineastische Schlachten."* — das ist ein **Cross-Link-Fehler**. Gemeint ist `§Cineastische Kampf-Beats`. Falls jemand dem Link folgt, landet er im Erfolgspool-System.

**Fix (1 Wort):** Z.156 `§Cineastische Schlachten` → `§Cineastische Kampf-Beats`.

**Nachzieh-Pflicht (außerhalb des Patch):**
- `core/spieler-handbuch.md` Z.381 *„Kampf-Kurzablauf"* — schlanker Mechanik-Block, sollte am Ende einen 1-Satz-Pointer auf `core/wuerfelmechanik.md#cineastische-kampf-beats` und Masterprompt §C bekommen, damit Spieler:innen wissen, wo die Beschreibungs-Norm steht.
- `core/sl-referenz.md` Z.1326 *„Action-Contract"*-Block wiederholt die filmische Norm in eigenen Worten. Sollte ebenfalls auf das neue Pflichtgate verweisen, sonst entstehen zwei Quellen-of-Truth zur Kampf-Beschreibung.

### 2. Probe-Pflicht-Konsistenz (§E) — **OK, aber Beat-2-Beispiel unvollständig**

§E Z.245 *„WÜRFELPROBEN SIND PFLICHT"* bleibt intakt. Mein Pflichtgate sagt drei Mal explizit *„um die Probe herum, nicht statt ihrer"* (masterprompt Z.155, wuerfelmechanik Z.403, Pflichtgate-Spec-Blockquote). Ein SL kann das nicht als „Probe optional" lesen.

**Aber Beat 2 im Beispiel** (`wuerfelmechanik.md` Z.460 ff) zeigt:
```
`Kodex: Probe-Template — Schleichen/Deckung…`
```

Bricht mit Ellipse ab. Eine LLM-SL liest das als *„Probe-Template wird abgekürzt, weil unwichtig"* und kopiert das Muster nachher in echten Output. **Konkretes Risiko:** Halbe Probe-Templates im Live-Spiel — schon mehrfach in `meta/symptome.md`-artigen Drift-Reports gesehen.

**Fix:** Beat 2 vollständige Probe ausschreiben, z. B.:
```
`Kodex: Probe-Template — 1W6 + ⌊GES/2⌋ + Talent Schleichen +1.`
`Probe: Deckungsrolle → W6: [4] + 3 + 1 = 8 vs SG 7 → Erfolg`
```

Damit ist das Beispiel selbst eine **Lehrvorlage**, keine Auslassungs-Falle.

### 3. Squad/Multiplayer-Kompatibilität — **Fix nötig (Wording)**

Beobachtung korrekt: In Squad-Sessions sind Voronov/Amara **Spielercharaktere** (siehe Masterprompt §I Squad-Manöver, Z.178 ff & Z.713 ff). Im Patch heißt es konsequent **NSC-Stimmen** — formal also keine Pflicht-Erfüllung möglich, wenn die Crew nur aus 3 Spieler:innen besteht und keine NSC-Begleiter dabei sind.

Drei Sub-Probleme:
1. **Masterprompt Z.147** *„Voronov ruft eine Warnung, Amara meldet über Comlink…"* — beide sind in Squad-Save-Profilen Spielercharaktere. Beispiel ist Solo-zentriert.
2. **Beat-Pool-Tabelle Z.430** *„Comlink-Koordination"* zitiert Voronov und Amara als NSC-Vorbild — gleiches Problem.
3. **Pflicht-Inkarnation 4** ist hart als *„NSC-Stimmen"* benannt — semantisch ausschließend gegen reinen Spieler-Squad.

**Fix-Variante A (minimal):** Begriff auf *„Kampf-Stimmen (NSC oder Squad-Mate)"* umstellen. Eine Edit-Stelle in masterprompt §C („NSC-Stimmen im Kampf" → „Kampf-Stimmen im Kampf (NSC oder Squad-Mate)"), spiegelbildlich in `wuerfelmechanik.md` §4 der Pflicht-Inkarnationen, plus 1 Satz: *„In Squad-Sessions zählen Squad-Mate-Stimmen (Spielercharaktere) gleichwertig zur Pflicht-Erfüllung; Begleit-NSCs sind nicht Voraussetzung."*

**Fix-Variante B (sauberer):** Pflicht-Inkarnation 4 reformulieren zu *„Stimmen im Kampf (Crew oder Welt)"* und Begleit-Beispiele neutralisieren: *„ein Crew-Mate ruft eine Warnung über Comlink, ein Gegner schreit, ein Zivilist duckt sich und ruft Hilfe"*. Damit ist die Regel modal-agnostisch.

Empfehlung: **Variante B**, weil die Solo-Variante (NSC-Begleiter) ein **Sub-Fall** der allgemeinen Regel ist und sich semantisch sauber unterordnet.

### 4. Action-Contract (§A) & Absatz-Verzahnung — **Mode-Kollision mit PRECISION**

§A Z.27 Action-Contract sagt *„filmische Beats/Outcome … nie als Schritt-für-Schritt-How-to"* — mein Pflichtgate steht damit **im Geist** überein (sensorische Verankerung statt Mechanik-Litanei). Keine harte Kollision.

**ABER zwei Sub-Konflikte:**

**a) PRECISION-Mode (`systems/toolkit-gpt-spielleiter.md` Z.486 ff):**

PRECISION-Mode sagt explizit:
- Z.488 *„Kurze, sachliche Sätze. Keine Metaphern."*
- Z.751 ff Kampfsequenz-Template: *„Regel: max. 2 Sätze Wirkung → Pressure → Decision."*

Mein Pflichtgate fordert *„sensorische Verankerung pro Beat"* mit Vorlagen wie *„Holz splittert unter den Aufschlägen. Patronenhülsen klirren auf den Steinboden — jemand aus dem Nebenraum schlägt Rückzug."* — das sind 3 Sätze, Metaphern (*„klirren"* ist sinnlich, *„schlägt Rückzug"* ist personifiziert), genau das, was PRECISION verbietet.

**Risiko:** Ein PRECISION-Spieler erlebt Pflichtgate ⊕ PRECISION als widersprüchlich, die SL kippt zu einer der beiden Seiten.

**Fix:** In Masterprompt §C einen Mode-Hinweis ergänzen: *„In `klassik`-Mode (Default) und `film`-Mode voll wirksam. In `precision`-Mode reduziert auf je 1 Sinnesanker + 1 Umgebungs-Referenz pro Beat, max. 2 Sätze pro Beat. Taktische Variation und Kampf-Stimmen bleiben Pflicht."* Das stellt klar, dass PRECISION keine Ausnahme vom Pflichtgate ist, aber die Dosis dem Mode angepasst wird.

**b) §G Ausgabeformat Z.538:**

§G sagt *„mindestens 3 Absätze, bei Kampf/Konflikten 4-6"* — mein Pflichtgate sagt **nichts** zu Absatzlängen. Konsequenz: Ein SL kann formal die Pflicht-Inkarnationen pro Beat erfüllen und trotzdem unter 4 Absätzen bleiben (z. B. drei kurze Beats in einem Absatz zusammengezogen). Das ist nicht falsch, aber unverbunden.

**Fix:** 1 Satz in masterprompt §C ergänzen: *„Pflicht-Inkarnationen sind kompatibel mit §G Ausgabeformat: Kampfszenen 4–6 Absätze, **eine** Pflicht-Inkarnation pro Beat-Absatz, nicht alle vier in einem Absatz."* Damit ist klar, wie sich die zwei Regelungen kombinieren.

### 5. Cross-Verweise — **2 Fehler, 1 Stilfrage**

- ✗ **`masterprompt_v6.md` Z.156** verweist auf `core/wuerfelmechanik.md §Cineastische Schlachten` — falsch, gemeint `§Cineastische Kampf-Beats`. (Siehe Befund 1.)
- ✓ **`masterprompt §G`** *„Aktion → Probe → Konsequenz → Kodex-Status → neue Lage"* — existiert wortgetreu in `meta/masterprompt_v6.md` Z.539. Cross-Link in `wuerfelmechanik.md` Z.401 valide.
- ✓ **Anchor `{#cineastische-kampf-beats}`** ist sauber gesetzt, einmalig im Repo, keine ID-Kollision.
- ✓ **`kampagnenstruktur.md` Z.884** verweist auf *„Masterprompt §C"* und *„`core/wuerfelmechanik.md` §Cineastische Kampf-Beats"* — beide valide.
- ⚠ **Stilfrage:** Die `§`-Notation ist im Masterprompt etabliert (`§A`, `§C`, `§E`, `§G`). Im Patch wird zwischen *„Masterprompt §C **Kampfszenen-Pflichtgate**"* (mit explizitem Pflichtgate-Namen) und *„Masterprompt §C"* (allein, in kampagnenstruktur.md) gewechselt. Konsistent mit existierenden Pflichtgate-Referenzen (Exfil-Stress, Briefing-Output) — kein Fix nötig, aber notiert.

## Empfehlung

**GO mit Mini-Fix.** Vier punktuelle Edits + zwei Nachzieh-PRs:

**In diesem Patch (vor Merge):**

1. **`meta/masterprompt_v6.md` Z.156**, Anchor-Fix:
   ```diff
   - Vollständige Spezifikation und Beat-Pool: `core/wuerfelmechanik.md` §Cineastische Schlachten.
   + Vollständige Spezifikation und Beat-Pool: `core/wuerfelmechanik.md` §Cineastische Kampf-Beats.
   ```

2. **`meta/masterprompt_v6.md` Z.147** + spiegelbildlich `core/wuerfelmechanik.md` Z.418, Pflicht-Inkarnation 4 umbenennen auf **Variante B** („Stimmen im Kampf (Crew oder Welt)"). Beispielzeile in `wuerfelmechanik.md` Beat-Pool *„Comlink-Koordination"* neutral halten (statt expliziter Voronov/Amara-Zitate).

3. **`core/wuerfelmechanik.md` Z.460 (Beat 2)**, vollständige Probe-Zeile einsetzen:
   ```diff
   - `Kodex: Probe-Template — Schleichen/Deckung…`
   + `Kodex: Probe-Template — 1W6 + ⌊GES/2⌋ + Talent Schleichen +1.`
   + `Probe: Deckungsrolle → W6: [4] + 3 + 1 = 8 vs SG 7 → Erfolg`
   ```

4. **`meta/masterprompt_v6.md` §C neuer Bullet**, vor der Begründungs-Zeile, ein PRECISION-Mode-Disclaimer + §G-Verzahnung (siehe Befund 4a/4b für genauen Wortlaut, je 1 Satz).

**Als Nachzieh-PR (separater Branch, nicht blocking):**

- `core/spieler-handbuch.md` Z.387 (Kampf-Kurzablauf) — 1-Satz-Pointer auf das Pflichtgate ergänzen.
- `core/sl-referenz.md` Z.1326 (Action-Contract-Block) — 1-Satz-Verweis ergänzen.
- `systems/toolkit-gpt-spielleiter.md` Z.751 (Kampfsequenz-Template) — Hinweis, dass PRECISION-Beispiel die Mode-Spezial-Variante ist und Klassik/Film den Pflichtgate-Pfad nutzen.

**Risikoeinschätzung:** Bei Merge nur mit Fix 1-3 ist Drift-Risiko niedrig (Solo-Highlander-Profil betroffen). Fix 2 (Squad-Wording) verhindert, dass Squad-Sessions die Pflicht-Inkarnation 4 formal nicht erfüllen können. Ohne Fix 4 bleibt PRECISION-Mode ein latenter Bruch — der wird auffallen, sobald der erste PRECISION-User Kampf spielt.

**Nicht blockierend, aber im Hinterkopf:** Wenn nach diesem Patch noch Highlander-Bestätigung läuft, dort gezielt prüfen, ob `Beat-Pool` und `SL-Choreografie-Werkzeuge` SL-seitig **erkannt und angewendet** werden, oder ob sie als „nice-to-have-Doku" ignoriert wurden. Letzteres würde ein zweites Pflichtgate-Iterations-Loop nach sich ziehen.
