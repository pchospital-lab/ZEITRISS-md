# Erweiterte Kritik — Verlust-Patch

> Branch: `feat/verlust-beats-und-heat-lebenszyklus`
> Audit-Datum: 2026-06-02
> Hinweis: Kritiker-Worker brach vor dem Vollschreiben ab (nur Skelett). Befunde
> hier von Altair selbst an der Quelle verifiziert (grep/read/node/smoke).

## A — Save-Schema-Konsistenz
- `campaign.heat` im JSON-Template (masterprompt:979), Export-Schema als Property
  (nicht in required), Pfadbaum (speicher:334), Migrations-Default 0. ✅
- node JSON.parse: beide Schemas + Masterprompt-JSON-Block VALID. ✅
- heat optional → korrekt NICHT in Export-Pflichtfeldliste Z220 (Watchguard-Pin
  intakt), aber im Detail-Pfadbaum Z334 + Template. Aufteilung konsistent mit
  research/prestige-Muster. ✅

## B — Heat-Lebenszyklus
- Anstieg (Spotlight/Anachronismus/laut), Abbau (HQ -1/Episode, Spuren verwischen),
  Cap 5 konsistent mit HUD `Heat 0/5`. ✅ Vollständiger Zyklus, kein monotoner Anstieg.
- psi_heat (per-Char) vs campaign.heat (Crew) sauber getrennt. ✅

## C — Fail-Forward-Verdeckung
- Als Pflicht für ALLE Verlust-Beats formuliert (masterprompt §F Heat-Gate Regel 4). ✅
- KEIN Widerspruch zum Tod-Handling: Tod ist offene Spieler-WAHL (Respawn/heroisch),
  die Fail-Forward-AUTOMATIK bleibt verdeckt. Wahl offen, Mechanismus verdeckt — sauber abgegrenzt. ✅

## D — Balance / Frust-Vermeidung
- Jede negative Achse hat einen Ausweg: Heat→Abbau, Stress→HQ-Reset(0),
  Fraktion-aktiv→auf eine Szene begrenzt (kampagnenstruktur:201), Scheitern→Folgespur. ✅
- Keine Death-Spiral: Fraktions-Eingriff ist begrenzt, nicht endlos. ✅

## E — Multiplayer/Koop
- LÜCKE GEFUNDEN + GEFIXT: campaign.heat hatte keine Split/Merge-Regel (anders als
  campaign.px). Ergänzt (speicher:6a): in beide Saves kopiert, Merge per max
  (kein Doppel-Anstieg). Konsistent mit px-„kein Doppel-Gewinn"-Philosophie. ✅
- Stress per-Char / Heat Crew-weit — Trennung im MP konsistent. ✅

## F — Pflicht-Invarianten + Regressionen
- smoke.sh: All smoke checks passed (Exit 0). Keine Invariante gebrochen
  (Px-Tabelle, Boss-Timing, 12/14, stress_max, LP, KI-SL unberührt). ✅
- Beat-Dosierungs-Rang: alle 11 genannten Beats existieren als reale Anker (verifiziert). ✅

## G — Sichtbarkeit
- Alle Patch-Teile in Spielflächen (masterprompt/kampagnenstruktur/zustaende/
  sl-referenz/speicher = System-Prompt + KB-Slots). Nichts dev-only. ✅

## H — Übergreifender Session-Blick (das wichtigste Signal)
- **17 unique Pflichtgates**, Masterprompt **~34,4k Token** (von ~32,8k zu
  Session-Beginn). §F ist 212 Zeilen — ein großer Gate-Block.
- Diese Session hat ~6 neue Gates ergänzt. Jedes gerechtfertigt, aber die SUMME
  drückt über die Komprimierungs-Schwelle (>30k, MEMORY-Notiz).
- Beat-Prioritäten konsistent, keine widersprüchlichen Ränge. Kein Ton-Bruch.
- **Empfehlung: Komprimierungs-Pass als nächste eigene Session** (verbose
  Gate-Beispiele in KBs auslagern, Masterprompt nur Regel + Verweis). KEIN
  Merge-Blocker für diesen Patch.

## Gesamturteil
**MERGE OK.** Der Patch ist sauber, Smoke grün, Save-Schema konsistent, die eine
Koop-Lücke (Heat-Split) gefixt. Kein kritischer Befund offen.

Übergreifend: Der Token-/Gate-Druck ist das reale nächste Thema — nicht dieser
Patch, sondern die Summe aller Session-Patches. Komprimierungs-Pass empfohlen,
bevor weitere Gates dazukommen.
