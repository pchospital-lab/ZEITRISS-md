# Entscheidungsvorlage: `economy.hq_pool` abschaffen?

**Stand:** 2026-06-16 · Synthese aus zwei parallelen Worker-Analysen
(Repo-Fakten / Design-UX) + eigener Bewertung (Altair). **Double-Critic durchgelaufen
(Fakten + Logik, beide Opus/high) — Befunde unten eingearbeitet.**

---

## TL;DR — Empfehlung: JA, abschaffen. Wallets werden alleinige Geld-SSOT. (Mit 4 Auflagen.)

Beide Worker-Analysen UND beider Critics kommen zum selben Schluss: abschaffen.
Die Begründung ist strukturell:

> Geld, das **einem Schlüssel gehört** (`character.id` → `wallet`), überlebt
> Split/Merge sauber, weil jede CU genau einem Eigentümer in genau einem Branch
> gehört → Merge dedupliziert pro ID, kann nicht doppelt zählen.
>
> `economy.hq_pool` ist **besitzlos/ungeschlüsselt**. Beim Split wird der ganze
> Save inkl. Pool kopiert. Beim Merge gibt es nur zwei Wege, beide
> falsch: **halbieren** → Leck (−29% beobachtet), oder **summieren** → Geld aus
> dem Nichts (der Split→Merge-Exploit, den Flo gerochen hat).

**Präzisierung nach Logik-Critic (wichtige Korrektur meiner ersten Fassung):**
Die Nicht-Konservativität folgt NICHT zwingend aus dem Pool-Konzept „als
Mathematik", sondern aus dem **fehlenden Owner-Key**. Beweis: der `funds`-Zukunfts-
pfad unten (geschlüsseltes Sub-Konto) WÄRE ein konservativer Pool. Es ist also
eine **Kosten-/Simplizitäts-Entscheidung**, kein Theorem — ich abschaffen, weil
Owner-Keying sich für den seltenen Nutzen JETZT nicht lohnt, nicht weil es
unmöglich wäre. EINE Ausnahme, wo die Mathematik doch hart hält: „gemeinsam
ausgeben WÄHREND die Gruppe getrennt ist" (beide Branches ziehen unabhängig) —
das ist auch geschlüsselt nicht konservativ. Dieses Feature war aber
wahrscheinlich nie gewollt → Abschaffen killt nur etwas, das niemand klar braucht.

Empirisch gedeckt: 4-1 halbierte (Leck), 3-2 kopierte (Inflations-Risiko). Die SL
handelt nicht-deterministisch, weil die Spec selbst keine konservative Regel kennt.

---

## Was der gemeinsame Pool HEUTE real tut (Repo-Fakten)

1. **Transit-Puffer:** Missionsprämie + Hazard-Pay landen erst im Pool, dann
   `apply_wallet_split()` auf die Wallets. ABER: Rewards sind bereits pro-Agent
   formuliert („Jeder erhält 300 CU") → der Pool ist nur Durchlaufstation.
2. **Arena-Gebühr** (250 CU + 1-3%) — einziger explizit pool-exklusiver Abzug.
3. **Markt/Shop-Käufe** laufen über `log_market_purchase()`, das vom Primary-
   Currency-Feld (= Pool) abbucht. **Per-Charakter-Wallet-Buchung existiert
   technisch NICHT** — wer ein Implantat kauft, zahlt de facto aus dem Team-Topf.
4. **Economy-Audit-Bänder** 120/512/900+ referenzieren `hq_pool` als Zielfeld.
5. **Split/Merge, Solo↔Koop-Migration, Legacy-cu→hq_pool** hängen dran.

**Wichtige Nuance (Repo-Worker):** `runtime.js` arbeitet intern mit
`economy.cu`/`economy.credits` als Primary-Keys; `hq_pool` ist der v7-Schema-Name
desselben Werts. Kein Bug, aber ein Namensgap, der bei der Umsetzung Konfusion
stiften kann.

## Solo-Fall (Mehrheit): Pool = reiner Overhead

Für einen Spieler gibt es kein „Team". Reward → Pool → 1× Split ins einzige
Wallet = zwei desync-fähige Zahlen, getrennt auditiert, zusätzlicher Toast-Pfad.
**Doppel-Buchhaltung ohne Mehrwert.** Solo will eine Zahl: „mein Konto".

---

## Was wir gewinnen / verlieren

**GEWINN:** Exploit strukturell weg · Split/Merge wird trivial (`economy =
Σ wallets`, erbt bewährte ID-Dedup-Logik) · eine Wahrheit · Solo-Overhead weg ·
weniger Schema-/Konflikt-/Halluzinationsfläche für die SL.

**VERLUST:** Kein dediziertes Shared-Konto für echte Team-Käufe (Schiff,
Quartier-Upgrade, Fraktionsspende). ABER:
- Reale P&P-Gruppen teilen per „wir legen je 200 zusammen" → über Wallets abbildbar.
- Fraktionsfonds/Hard-Cap-Overflow ist konzeptionell ein **Sink** (Geld verlässt
  Spielerkontrolle), kein mitgeführter Topf → braucht keine Balance.
- Lore „ITI-Nullzeit-Konto" bleibt — es **ist** dann das Wallet.

---

## Verworfene Alternativen (warum nicht)

- **(a) Pool nur im Gruppen-Modus:** behält das Problem genau dort, wo Split/Merge
  passiert. Löst die schwere Hälfte nicht.
- **(b) Pool + Konservierungsregel:** braucht Owner-/Lineage-Tracking pro Anteil.
  Komplex, fragil, verlangt verlässliche Arithmetik von der SL — die laut Playtest
  genau das nicht zuverlässig kann.
- **(c) Pool nur als ankergebundener Rest (nie auf Branches):** konservativ, aber
  der Pool ist im Branch tot → höhlt den einzigen Daseinszweck (gemeinsam ausgeben
  WÄHREND getrennt) selbst aus. Halbherzig.

## Der saubere Zukunftspfad für echtes Team-Geld (falls je gebraucht)

NICHT als co-mingled Pool wiederbeleben, sondern als **geschlüsseltes,
ankergebundenes, default-off `funds`-Sub-Konto** (gehört einer synthetischen
Entität, z.B. `funds[].id="HQ-FUND"`). Dedupliziert beim Merge identisch wie
Wallets, liegt beim Split auf genau einem Branch, in Solo abwesend. So bekommt man
opt-in Team-Schatzkammer OHNE Konservierungsproblem. **Nicht jetzt bauen — nur den
Pfad offenhalten.**

---

## Double-Critic-Befunde (eingearbeitet)

**Fakten-Critic (Quellen-Verifikation, alle Schlüsselpunkte gegen Repo geprüft):**
Faktenbasis trägt. ✅ `hq_pool` required in beiden Schemas (export = additionalProperties:false,
härter) · ✅ `log_market_purchase()` bucht nur Primary, keine Per-Wallet-Buchung
· ✅ Arena-Gebühr aus Primary · ✅ Split=halbieren/Merge=summieren wörtlich belegt
· ✅ Aufwand ~13 Dateien exakt. **Zwei Abstriche:** (1) „Rewards pro-Agent → reine
Durchlaufstation" ist mechanisch geschönt — `apply_wallet_split` schreibt den vollen
Reward als Lump in den Pool, teilt dann, und ein **unteilbarer Rest bleibt im Pool**
(„Rest X CU im HQ-Pool"). (2) Dieser **Wallet-Split-Leftover** + der
**Hard-Cap-Overflow→Fraktionsfonds** brauchen beim Abschaffen explizit einen neuen
Ablageort — sonst verlieren sie still ihr Ziel.

**Runtime-Nuance (beide Critics):** `runtime.js` SCHREIBT `hq_pool` nie — es arbeitet
intern auf `economy.cu`, `hq_pool` ist nur der v7-Export-Name + economy_audit-Lesefeld.
Real-Risiko liegt also in **Schema + Docs + KI-SL-Prompt**, weniger im Code. „3
Funktionen umbiegen" überzeichnet den Runtime-Teil leicht.

**Logik-Critic (Advocatus Diaboli): Empfehlung tragfähig — JA, mit 4 Auflagen:**
- **(a) Offene Frage #3 VOR der Umsetzung entscheiden.** Heute = „einer kauft fürs
  Team" (gelebter Komfort). Per-Charakter-Buchung existiert technisch nicht. Die
  Empfehlung darf nicht umgesetzt werden, bevor das geklärt ist.
- **(b) Wallet→Wallet-Transfer sicherstellen.** „Reale Gruppen legen je 200 zusammen"
  ist nur abbildbar, wenn es eine Transfer-Mechanik gibt. Fehlt sie, ist das
  Abschaffen eine **Koop-Regression** (nicht „kein Architektur-Risiko" — das war
  zu glatt; Per-Wallet-Kauf + Transfer sind NEUBAU).
- **(c) „Mathematik"-Framing ehrlich abschwächen** → erledigt (siehe TL;DR oben).
- **(d) Balancing als echten Arbeitsschritt, nicht TODO.** Die Bänder 120/512/900+
  setzen den Pool SEPARAT voraus; 8-10k Pool in Pro-Wallet-Ziele falten ist
  nicht-trivial — falsch kalibriert reproduziert es das Leck/Inflations-GEFÜHL an
  neuer Stelle.

## Umsetzungs-Aufwand (Repo-Fakten)

- **~13 Dateien, ~60 Stellen.**
- **2 harte Schema-Breaks:** `saveGame.v7.schema.json` + `.export.schema.json`
  (`hq_pool` ist `required`) → CI bricht sofort, `test_v7_issue_pack.js:18` auch.
- **3 Funktionen umbiegen:** `apply_wallet_split()`, `initialize_wallets_from_roster()`,
  Hazard-Pay-Fluss.
- **Runtime:** `economy_audit` auf Wallet-Bänder umstellen, Arena-Gebühr-Quelle klären.
- **Docs:** speicher-fortsetzung.md (~28 Stellen), sl-referenz.md (9), Modul 15,
  Masterprompt-Template, etc.
- **Balancing-TODO (kein Blocker):** Level-Bänder neu kalibrieren (HQ-Budget faltet
  sich in höhere Pro-Wallet-Zielwerte).

**Einschätzung:** Großer, aber mechanischer PR. Kein Architektur-Risiko, weil die
Ziel-Logik (Wallet-ID-Dedup) bereits existiert und erprobt ist — wir entfernen
einen Sonderpfad, statt einen neuen zu bauen. Ideal als eigener PR mit
Critic-Kaskade in einer frischen Session.

## Offene Fragen an Flo (Design-Entscheidungen im Fix)

1. **Migration alter Saves:** `hq_pool` beim Laden → Anker-Charakter-Wallet
   ODER gleichverteilt auf aktuellen Roster? (beide konservativ, einmalig)
2. **Arena-Gebühr in Koop:** aus Anker-Wallet? Gleichverteilt? Oder zahlt der
   Initiator?
3. **⭐ Shop/Implantat-Käufe (DIE Kernfrage, laut Logik-Critic VOR Umsetzung zu
   klären):** Soll künftig jeder aus seinem eigenen Wallet zahlen (= echte
   per-Charakter-Buchung, NEUBAU) — oder bleibt „einer zahlt für die Gruppe"?
   Davon hängt ab, ob das Abschaffen ein Komfort-Verlust wird.
4. **Wallet→Wallet-Transfer:** Brauchen wir „CU an Teammate übergeben"? Ohne das
   ist „zusammenlegen für Großanschaffung" nicht spielbar (Koop-Regression-Risiko).
5. **Leftover + Hard-Cap-Overflow:** Wohin mit dem unteilbaren Wallet-Split-Rest
   und dem >Cap-Overflow, wenn kein Pool mehr da ist? (Vorschlag: Rest rundet in
   Anker-Wallet, Overflow = reiner Sink/Fraktionsfonds.)

---

**Verdict nach Double-Critic:** Abschaffen ist richtig (Exploit real, Solo-Overhead
real, Ziel-Logik existiert bereits). ABER es ist KEIN reiner „Sonderpfad entfernen"-
PR — Fragen #3/#4 sind echte Gameplay-Designentscheidungen mit Neubau-Anteil, die
VOR der Umsetzung mit Flo geklärt werden müssen. Reihenfolge: erst Flo entscheidet
#3+#4, dann Fix-PR.
