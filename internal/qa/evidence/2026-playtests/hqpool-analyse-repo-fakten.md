# hq_pool-Analyse – Repo-Fakten (ZEITRISS 4.2.6)

**Stand:** 2026-06-16  
**Analysiert durch:** Subagent (reine Repo-Lektüre, keine Änderungen)  
**Scope:** ZEITRISS-md-git, alle relevanten Quelldateien  

---

## a) Wofür wird `hq_pool` konkret benutzt?

### 1. Primärer Team-Kontostand / Kanonischer Anker

`economy.hq_pool` ist der **einzige kanonische HQ-Kontostand** einer Session.  
- `systems/currency/cu-waehrungssystem.md:52` — „`economy.hq_pool` ist das einzige kanonische HQ-Konto."
- `core/sl-referenz.md:1272` — „als `economy.hq_pool` der einzige kanonische Team-Kontostand."
- `systems/gameflow/speicher-fortsetzung.md:17` — SSOT-Anker: „Economy-Sync bleibt konsistent (`economy.hq_pool` als Primäranker)."

### 2. Eingangs-Puffer für Missionsprämien (vor Wallet-Split)

Belohnungen aus Missionen fließen zuerst in den HQ-Pool, danach werden sie per `apply_wallet_split()` auf die Wallets verteilt.  
- `systems/currency/cu-waehrungssystem.md:52–60` — Debrief-Reihenfolge: HQ-Buchung → dann Wallet-Split auf `characters[].wallet`.
- `core/sl-referenz.md:1263–1267` — „Koop-Teams erhalten … `HQ-Pool: … CU verfügbar` für den Restbestand (`economy.hq_pool`)."

### 3. Hazard-Pay-Eingang (priorisiert, vor Split)

`hazard_pay`-Angaben landen **zuerst** im HQ-Pool, bevor die Wallet-Verteilung läuft.  
- `systems/gameflow/speicher-fortsetzung.md:1572` — „Runtime den Betrag zuerst auf `economy.hq_pool` und loggt `Hazard-Pay: … CU priorisiert`"
- `core/sl-referenz.md:1279` — „Hazard-Pay wird vor dem Split verbucht … landen direkt im HQ-Pool"

### 4. Arena-Gebühr (Abzug aus HQ-Pool)

`arenaStart()` zieht die Arena-Eintrittsgebühr aus dem gemeinsamen `economy.hq_pool` (bzw. dem Primary-Currency-Feld):  
- `systems/currency/cu-waehrungssystem.md:57` — Cross-Mode-Sequenz: „`arenaStart()` (Gebühr aus `economy.hq_pool`)"
- `gameplay/kampagnenstruktur.md:2038` — „Kodex zieht den Betrag aus dem primären Economy-Feld und schreibt ihn in `economy.hq_pool`"
- `core/sl-referenz.md:438–441` — „Phase-Strike Arena. `arenaStart(options)` zieht die Arena-Gebühr aus `economy` … Die Gebühr wird parallel im HQ-Pool (`economy.hq_pool`) geführt"
- `systems/toolkit-gpt-spielleiter.md:500` — „synchronisiert den Betrag per `sync_primary_currency()` auf `economy.hq_pool`"
- Runtime-Beleg: `runtime.js:282–283` — `ARENA_BASE_FEE = 250` plus prozentualer Anteil; `runtime.js:6793` — `writeArenaCurrency(key, value - fee, 'arena_fee')` ruft intern `sync_primary_currency()` auf.

### 5. Markt/Shop-Käufe (Debrief/Chronopolis)

`log_market_purchase()` bucht Einkäufe direkt vom Primary-Currency-Feld ab, das über `sync_primary_currency()` immer mit `hq_pool` in Einklang gehalten wird. Das Ergebnis erscheint im Debrief als `Chronopolis-Trace (n×)`.  
- `systems/currency/cu-waehrungssystem.md:396–431` — `log_market_purchase()` + `run_shop_checks()`  
- `systems/gameflow/speicher-fortsetzung.md:1232` — `log_market_purchase()` schreibt in `logs.market[]`
- `runtime.js:1711–1737` — `log_market_purchase()` liest `economy.cu` über `resolve_primary_currency()`, zieht Kosten ab.

### 6. Briefing-Rohrpost-Käufe (optional aus HQ-Pool oder persönlicher Wallet)

Im Briefing können Agenten per Rohrpost aus dem HQ-Shop nachkaufen; Abbuchung wahlweise aus persönlicher Wallet oder HQ-Pool (nach Squad-Abstimmung).  
- `meta/masterprompt_v6.md:322` — „CU-Abbuchung aus dem persönlichen Wallet (oder HQ-Pool bei Squad-Abstimmung)"
- `systems/toolkit-gpt-spielleiter.md:248–249` — identisch

### 7. Economy-Audit-Bänder (Reporting 120/512/900+)

Bei jedem HQ-Save prüft `economy_audit()` den `hq_pool`-Stand gegen Zielbänder und erzeugt ggf. einen Toast.  
- `systems/gameflow/speicher-fortsetzung.md:376–387` — `economy_audit()` meldet `hq_pool`, `wallet_sum`, `wallet_count`, `wallet_avg`, Zielbänder 120/512/900+.
- `core/sl-referenz.md:1000–1006` — „Beim HQ-Save ergänzt die Runtime außerdem ein `economy_audit`-Trace"
- `runtime.js:5987` — `hq_pool: { min: hqMin, max: hqMax }` (Zielband)
- `runtime.js:6051` — `hq_pool: hqPool` im Audit-Output

**Richtwerte:**  
| Level-Band | HQ-Pool Zielbereich |
|------------|---------------------|
| 120        | 8 000–10 000 CU     |
| 512        | 25 000–30 000 CU    |
| 900+       | 45 000–60 000 CU    |

### 8. Session-Anker bei Split/Merge

Bei Team-Split wird `economy.hq_pool` gleichmäßig aufgeteilt; beim Merge addiert.  
- `systems/gameflow/speicher-fortsetzung.md:1471` — „`economy.hq_pool` gleichmäßig verteilen"
- `systems/gameflow/speicher-fortsetzung.md:1495` — „`economy.hq_pool` aus beiden Saves addieren"
- `core/sl-referenz.md:330` — Session-Anker-HQ-Pool hat Vorrang bei Multi-Import

### 9. Solo→Koop-Umstieg: Verschiebung alter Solo-Guthaben in hq_pool

Beim Moduswechsel Solo→Koop werden alle bisherigen Solo-CUs in den HQ-Pool verschoben.  
- `core/sl-referenz.md:1268–1269` — „`initialize_wallets_from_roster()` verschiebt alte Solo-Guthaben vollständig in den HQ-Pool"
- `systems/gameflow/speicher-fortsetzung.md:1599` — Beschreibung desselben Ablaufs

### 10. Charakterbogen-Anzeige (`!bogen`)

Der `!bogen`-Befehl zeigt den `hq_pool` als laufenden Team-Ökonomie-Überblick.  
- `systems/gameflow/speicher-fortsetzung.md:1664` — „Team-Ökonomie (`economy.hq_pool`)"

### 11. Koop→Solo-Extraktion

Bei Koop→Solo bleibt der `hq_pool` ankergeführt (nicht zurückgesetzt), Character-Wallet wird extrahiert.  
- `systems/gameflow/speicher-fortsetzung.md:873` — „`economy.hq_pool` bleibt ankergeführt"

### 12. Legacy-Migration: economy.cu → hq_pool

Beim Laden alter Saves (v6) wird `economy.cu` auf `economy.hq_pool` normalisiert.  
- `core/sl-referenz.md:276` — „`economy.cu` wird auf `economy.hq_pool` normalisiert"
- `systems/gameflow/speicher-fortsetzung.md:467` — identisch

---

## b) Welche Makros/Funktionen LESEN / SCHREIBEN hq_pool?

### SCHREIBEN (Wert wird gesetzt/verändert)

| Funktion / Makro | Was es schreibt | Beleg |
|-----------------|-----------------|-------|
| `apply_wallet_split()` | Missionsprämie fließt ein, Wallet-Anteile werden abgezogen; `economy.cu` (Primary) wird via `sync_primary_currency()` synchronisiert | `runtime.js:5858–5909` |
| `arenaStart()` / `writeArenaCurrency()` | Arena-Gebühr wird abgezogen via `sync_primary_currency()` | `runtime.js:6773–6807` |
| `log_market_purchase()` | Kaufkosten von `economy.cu` abgezogen, via `sync_primary_currency()` synchronisiert | `runtime.js:1711–1737` |
| `sync_primary_currency()` | Synchronisiert `economy.cu` + `economy.credits` (Primary-Keys); `hq_pool` im v7-Save ist der docuemntierte Name dafür | `runtime.js:2674–2695` |
| `initialize_wallets_from_roster()` | Verschiebt Solo-Guthaben in Pool (zu Economy); öffnet Wallets | `runtime.js:5909` / `sl-referenz.md:1268` |
| `sync_hq_pool()` | Explizit erwähnt in Cross-Mode-Sequenz | `speicher-fortsetzung.md:843` |

> **Technische Anmerkung:** `runtime.js` arbeitet intern mit `economy.cu` und `economy.credits` als Primary-Keys (`ECONOMY_PRIMARY_KEYS = ['credits', 'cu', 'balance', 'assets']`, Z.2622). Das Feld `hq_pool` _erscheint nicht als Runtime-Schreibziel in runtime.js_ — es ist der **v7-Schema-Name** desselben Wertes. `prepare_save_economy()` (`runtime.js:8168`) synct und exportiert via `economy.cu`; die KI-SL ohne runtime.js schreibt nativ `economy.hq_pool`. Die Docs bezeichnen das Gleiche.

### LESEN (Wert wird abgefragt)

| Funktion / Makro | Was es liest | Beleg |
|-----------------|--------------|-------|
| `build_economy_audit()` | Liest `economy.cu` (= hq_pool), berechnet Deltabänder | `runtime.js:6018–6069` |
| `economy_audit_guidelines()` | Liest Level-Band, gibt Zielrange für hq_pool zurück | `runtime.js:5954–5992` |
| `readArenaCurrency()` | Liest Economy-Primary-Key für Arena-Gebühr-Berechnung | `runtime.js:6664–6675` |
| `apply_wallet_split()` | Liest `economy.cu` vor dem Split als Ausgangsbasis | `runtime.js:5862` |
| `resolve_economy_audit_level()` | Liest Level aus Session, bestimmt Band | `runtime.js:5994` |
| `!bogen`-Debrief | Zeigt `economy.hq_pool` als HUD-Output | `speicher-fortsetzung.md:1664` |
| Session-Anker-Merge | Prüft `economy.hq_pool`, um Gast-Saves zu verwerfen | `speicher-fortsetzung.md:859` |

---

## c) Käufe/Ausgaben, die NUR aus hq_pool gehen und NICHT aus persönlichen Wallets?

**Klarer Befund: explizit NUR aus hq_pool:**

1. **Arena-Gebühr** (`arenaStart()`) — Die Gebühr (250 CU + 1–3 % des Vermögens) geht aus dem Primary-Economy-Feld, das im Kontext des gesamten Teams der hq_pool ist (`kampagnenstruktur.md:2038`, `sl-referenz.md:438–441`, `toolkit-gpt-spielleiter.md:500`).

**Aus hq_pool ODER persönlicher Wallet (nach Squad-Abstimmung):**

2. **Briefing-Rohrpost-Käufe** — Wahlweise personal Wallet oder HQ-Pool (`masterprompt_v6.md:322`, `toolkit-gpt-spielleiter.md:248`).

**Unklar/nicht explizit zugeordnet (kein SSOT-Beleg für exclusiv hq_pool):**

- **Team-Perks (kampagnenstruktur.md:1650):** 500 CU, 200 CU Umschulung. Es steht im Repo **nicht explizit**, ob diese aus hq_pool oder aus einer Wallet bezahlt werden. Es wird nur „im HQ erworben" gesagt. Kein direkter hq_pool-Bezug in den relevanten Zeilen.
- **Chronopolis-Einkäufe / HQ-Shop:**  `log_market_purchase()` bucht vom Primary-Economy-Feld ab, das bei Koop = hq_pool ist. Bei Solo ist hq_pool ebenfalls das einzige Economy-Feld. Im direkten Einzelkauf könnte eine persönliche Wallet alternativ gemeint sein, aber die Runtime unterscheidet das nicht — sie bucht immer vom Primary ab.
- **HQ-Werkstatt, Klinik/OP, Forschung, Shared Upgrades:** Das Repo enthält **keinen expliziten SSOT-Beleg**, dass diese Kategorien _ausschließlich_ aus hq_pool gehen. In der Praxis werden alle Einkäufe über `log_market_purchase()` abgerechnet, das immer das Primary-Economy-Feld (= hq_pool) abbucht, ohne Wallet-Differenzierung zu unterstützen.

**Zusammenfassung c):** Das Repo unterscheidet auf Makro-Ebene _nicht_ zwischen „Kauf aus hq_pool" vs. „Kauf aus persönlicher Wallet" — `log_market_purchase()` bucht ausnahmslos vom Primary-Currency-Feld (= hq_pool) ab. Eine explizite „paid from wallet X"-Funktionalität existiert in der Runtime nicht. Die einzige Ausnahme mit namentlichem Beleg: die Arena-Gebühr ist explizit dem hq_pool zugeordnet.

---

## d) Wenn man hq_pool ersatzlos streicht: Welche Funktionen BRECHEN?

### Pflichtfeld in Save-Schemas → Validation-Break

`economy.hq_pool` ist **required** in beiden Schema-Dateien:  
- `systems/gameflow/saveGame.v7.schema.json:150–155` — `"required": ["hq_pool"]`, Typ `number`
- `systems/gameflow/saveGame.v7.export.schema.json:297–305` — identisch, `additionalProperties: false`
- `tools/test_v7_issue_pack.js:18` — `assert.ok(save.economy && Number.isFinite(save.economy.hq_pool), ...)`

**→ BRICHT SOFORT:** Alle Schema-Validierungen, CI-Tests, Schema-Konformitäts-Checks.

### Economy-Audit bricht

- `runtime.js:5987,6038,6044,6051,6066,6069` — `economy_audit_guidelines()` und `build_economy_audit()` referenzieren `hq_pool` als Ausgabefeld. Ohne das Feld kein Audit-Toast, keine Out-of-Range-Warnung.

### arenaStart()-Sequenz bricht

- `systems/currency/cu-waehrungssystem.md:57` — Sequenz nennt explizit `economy.hq_pool` als Ziel.  
  **→ Konkretes Umbiegen:** Entweder auf `characters[index0].wallet` (Session-Anker-Charakter) oder auf ein neues gemeinsames Feld. Aber: Kein sinnvolles persönliches Wallet für Arena-Gebühr in Koop (das Team zahlt, nicht eine Person).

### apply_wallet_split() bricht inhaltlich

- Der Debrief gibt explizit `HQ-Pool: … CU verfügbar` aus (`sl-referenz.md:1263`, `speicher-fortsetzung.md:1572`, `toolkit-gpt-spielleiter.md:622`).  
  **→ Muss umgebogen werden:** Ohne Shared-Pool kein Restbestand-Report nach Split. Entweder entfällt die Zeile oder man aggregiert alle Wallets.

### initialize_wallets_from_roster() bricht

- `sl-referenz.md:1268` — „verschiebt alte Solo-Guthaben vollständig in den HQ-Pool". Ohne Pool: Wohin mit dem Geld beim Solo→Koop-Wechsel?  
  **→ Bricht:** Logik müsste auf gleichmäßige Wallet-Verteilung umgebogen werden.

### Hazard-Pay-Fluss bricht

- `speicher-fortsetzung.md:1572` — Hazard-Pay landet im hq_pool, erst dann Wallet-Split.  
  **→ Bricht:** Hazard-Pay müsste direkt in die persönlichen Wallets gehen (entweder gleichmäßig oder nach eigenem Schema).

### Split/Merge-Logik bricht

- `speicher-fortsetzung.md:1471` — „`economy.hq_pool` gleichmäßig verteilen" beim Split  
- `speicher-fortsetzung.md:1495` — „`economy.hq_pool` aus beiden Saves addieren" beim Merge  
- `speicher-fortsetzung.md:859` — Session-Anker-Führung via `economy.hq_pool`  
  **→ Bricht fundamental:** Der gesamte Split/Merge-Mechanismus setzt auf einen gemeinsamen Pool als Split-Quelle und Merge-Summe. Ohne hq_pool muss jeder Split nur noch Wallets aufteilen — aber die Prämien-Zwischen-Pufferung fehlt.

### Legacy-Migrations-Pfad economy.cu → hq_pool bricht

- `sl-referenz.md:276`, `speicher-fortsetzung.md:467` — Migration setzt `economy.hq_pool` als Ziel.  
  **→ Muss auf neues Ziel umgebogen werden**, sonst schlägt Migration aller v6-Saves fehl.

### Charakterbogen-Anzeige !bogen bricht

- `speicher-fortsetzung.md:1664` — Zeigt `economy.hq_pool` im HUD.  
  **→ Muss angepasst werden.**

### Masterprompt-Template bricht

- `meta/masterprompt_v6.md:1048` — `"economy": { "hq_pool": 0 }` als Template.  
  **→ Muss aktualisiert werden.**

### zeitriss-core.md Beispiel-Save bricht

- `core/zeitriss-core.md:708` — `"economy": { "hq_pool": 0 }` als Beispiel.

---

## e) Wieviele Stellen müssten geändert werden?

### Canonical-Doc-Dateien (produktiver Spielbetrieb)

| Datei | Betroffene Zeilen (hq_pool) | Art der Änderung |
|-------|-----------------------------|-----------------|
| `systems/currency/cu-waehrungssystem.md` | Z.52,57,62 | Konzept, Sequenz-Beschreibung |
| `core/sl-referenz.md` | Z.276,287,330,441,1006,1264,1272,1280,1431 | 9 Stellen |
| `systems/gameflow/speicher-fortsetzung.md` | Z.17,226,350,376,437,458,467,503,523,531,585,703,821,832,843,856,859,872,873,935,1044,1471,1495,1572,1664,1796,1804,1836 | ~28 Stellen |
| `systems/toolkit-gpt-spielleiter.md` | Z.500,622 | 2 Stellen |
| `gameplay/kampagnenstruktur.md` | Z.2038 | 1 Stelle |
| `core/zeitriss-core.md` | Z.708 | 1 Stelle |
| `meta/masterprompt_v6.md` | Z.1048,322(indirekt) | 2 Stellen |
| `docs/testing.md` | Z.119,148 | 2 Stellen |
| `docs/qa/tester-playtest-briefing.md` | Z.62 | 1 Stelle |

**Gesamt Docs: ~9 Dateien, ~50 direkte Textstellen**

### Schema-Dateien (harter Break, Pflichtfelder)

| Datei | Art |
|-------|-----|
| `systems/gameflow/saveGame.v7.schema.json` | `required: [hq_pool]` + Feld-Definition → muss entfernt/ersetzt werden |
| `systems/gameflow/saveGame.v7.export.schema.json` | identisch, `additionalProperties: false` → noch kritischer |

### Runtime-Code

| Datei | Stellen | Art |
|-------|---------|-----|
| `runtime.js` | Z.5987,6038,6044,6051,6066,6069 | economy_audit-Output-Felder, umbiegen auf wallet-basiertes Audit |
| `tools/test_v7_issue_pack.js` | Z.18 | Assert auf `economy.hq_pool` |

**Gesamt Runtime: 2 Dateien, ~7–8 Stellen**

### Gesamtbild

- **~13 betroffene Dateien** (ohne interne QA-Evidence/Fixtures)  
- **~60 direkte Textstellen / Codezeilen** die geändert/umgebogen werden müssten  
- **3 Kategorien:** Schema-Pflichtfelder (hart, brechen CI), Runtime-Logik (Audit, Arena-Gebühr), Dokumentation (Debrief-Texte, Sequenz-Beschreibungen)

---

## Widersprüche / Unklarheiten

1. **Runtime.js vs. v7-Schema-Konzept:** `runtime.js` arbeitet intern mit `economy.cu` / `economy.credits` als Primary-Keys, nicht mit `economy.hq_pool`. Das Feld `hq_pool` erscheint in runtime.js nur in `economy_audit()`-Output-Objekten. Die KI-SL (ohne runtime.js) schreibt v7-JSON nativ mit `hq_pool`. Es handelt sich konzeptuell um dasselbe Feld, aber technisch gibt es einen Namensgap. Das ist **keine Inkonsistenz-Bug**, aber ein potenzieller Konfusionspunkt bei jeder Änderung.

2. **Team-Perks-Zahlungsquelle unbelegt:** `kampagnenstruktur.md:1650` nennt 500 CU für Team-Perks ohne explizite Quelle (hq_pool oder Wallet). Unklar, ob das als gemeinsamer oder individueller Aufwand gebucht werden soll.

3. **Markt-Käufe — keine Wallet-Differenzierung:** `log_market_purchase()` bucht immer vom Primary (= hq_pool), kennt keine Per-Charakter-Wallet-Buchung. Wer ein Implantat kauft, tut das de facto aus dem Team-Pool heraus, auch wenn die Doku das nicht so direkt sagt.

---

*Ende der Faktenanalyse. Keine Änderungen an Repo-Dateien vorgenommen.*
