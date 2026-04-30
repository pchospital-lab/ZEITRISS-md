# Chronopolis-Dynamik: Arbeitsplan (Step-by-Step)

Ziel: Die freie Chronopolis-Regie (Beats statt Szenencount) reproduzierbar in Runtime, Wissensspeicher und QA verankern.

## 0) Scope und SSOT festziehen

1. `gameplay/kampagnenstruktur.md` als SSOT für Chronopolis-Regeln markieren (Beats, Pools, Exit-Druck, keine Saves).
2. Prüfen, ob widersprüchliche Aussagen in weiteren WS-Modulen existieren.
3. Ergebnis als kurze „In/Out of Scope“-Liste dokumentieren.

**Erledigt, wenn:** Ein klarer SSOT-Abschnitt und keine Regelkonflikte mehr vorhanden sind.

## 1) Runtime-Lücke explizit schließen

1. In `toolkit-runtime-makros.md` einen eigenen Chronopolis-Beat-Loop ergänzen.
2. Trigger definieren: „nach jeder bedeutsamen Aktion genau 1 Reaktions-Beat“.
3. Prioritätsreihenfolge festlegen: `encounter_pool` / `nsc_generator` / `twist_pool` / selten `para_creature`.
4. Exit-Druck nach großem Gewinn als Regel kodieren (ohne festen Szenenzähler).

**Erledigt, wenn:** Start-Makro nicht nur Guards/HUD setzt, sondern den Beat-Loop sichtbar initialisiert.

## 2) Makro-Vertrag (I/O) konkretisieren

1. Für alle neuen Chronopolis-Makros Input/Output als Mini-Vertrag dokumentieren.
2. Pflichtzustand im Save-Kontext trennen:
   - persistente Felder (dürfen in Saves),
   - Runtime-Transienten (dürfen nicht persistiert werden).
3. Guardrails ergänzen: keine Seeds/Px/Boss als Standardpfad, optionaler Apex nur nach Regeltrigger.

**Erledigt, wenn:** Ein anderer Maintainer die Makros ohne implizites Wissen nachbauen könnte.

## 3) Wissensspeicher-Synchronisierung

1. Regeländerungen aus Runtime in die betroffenen WS-Slots spiegeln.
2. Begriffe vereinheitlichen (insb. Buff/Modifikator) und negative Beispiele im Masterprompt verankern.
3. Chronopolis-Sektion auf „Beats + Generatoren + Tools“ schärfen, ohne feste Szenenbeispiele zu erzwingen.

**Erledigt, wenn:** „Was nicht im WS steht, existiert nicht“ für die neue Dynamik vollständig erfüllt ist.

## 4) QA-Matrix für Stabilität

1. Regressionsfälle für Chronopolis anlegen:
   - erfolgreicher Start mit Optionen,
   - Reaktions-Beat nach Aktion,
   - Exit-Druck nach großem Gewinn,
   - sauberer Exit zurück HQ.
2. Negativfälle anlegen:
   - stuck in Chargen,
   - Run ohne Auswahloptionen,
   - falscher Persistenzzustand nach Reload.
3. Modellvergleich (mind. 2 LLMs) aufnehmen, damit Instabilitäten sichtbar werden.

**Erledigt, wenn:** Jeder bekannte Ausfallmodus als Testfall mit erwarteter Reaktion vorliegt.

## 5) Verifikation (Pflicht + empfohlen)

- Pflicht: `bash scripts/smoke.sh`
- Empfohlen:
  - gezielter Persona-Playtest nur Chronopolis-Loop,
  - Cross-Mode-Flow: Core → Arena → Rift → Chronopolis → Save/Load-Check.

**Erledigt, wenn:** Smoke grün ist und Chronopolis-spezifische Checks reproduzierbar dokumentiert sind.

## 6) Abschlusskriterien für „wieder sauber anschließbar“

- [ ] Beat-Loop in Runtime dokumentiert und anschließbar.
- [ ] WS-Module konsistent aktualisiert.
- [ ] QA-Fälle + erwartete Ergebnisse im Repo hinterlegt.
- [ ] Keine Save-/Mode-Regressions gegen v7-Invarianten.
- [ ] Änderungsnotiz mit offenen Restpunkten vorhanden.

## Reihenfolgeempfehlung für die Umsetzung

1. Scope/SSOT (0)
2. Runtime-Loop + Makro-Vertrag (1–2)
3. WS-Sync (3)
4. QA-Matrix + Verifikation (4–5)
5. Abschlusscheckliste abhaken (6)

So bleibt jeder Zwischenstand nachvollziehbar und ihr könnt nach jedem Schritt sicher wieder einsteigen.
