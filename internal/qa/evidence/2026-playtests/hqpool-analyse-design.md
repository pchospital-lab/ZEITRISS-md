# ZEITRISS – Design-Bewertung: `economy.hq_pool` abschaffen?

**Frage:** Soll der gemeinsame Geld-Topf (`economy.hq_pool`) zugunsten reiner
persönlicher Wallets (`characters[].wallet`) abgeschafft werden?

**Quellen gelesen:** `core/spieler-handbuch.md` (Gameflow, Split/Merge,
MMO-ohne-Server, Session-Anker), `systems/currency/cu-waehrungssystem.md`
(Modul 15), `systems/gameflow/speicher-fortsetzung.md` (§Kontinuitätsmodell,
§Cross-Mode-Import, §Pflichtbeats Split/Rejoin, §Wallets).

---

## Kernbefund vorab: Das Problem ist nicht „geteilt vs. persönlich", sondern „besitzlos vs. besitzt"

Wallets überleben Split/Merge **sauber**, weil jede CU einem **geschlüsselten
Eigentümer** gehört (`character.id`), der in genau **einem** Branch existiert.
Der Merge dedupliziert pro ID, nimmt den neuesten Stand pro ID — Geld kann
nicht doppelt gezählt werden, weil ein Charakter nicht in zwei Branches
gleichzeitig „echt" ist.

`economy.hq_pool` bricht aus genau dem gegenteiligen Grund: Er ist **besitzlos
und ungeschlüsselt** (kein Owner, keine ID). Beim Split wird der ganze Save —
inkl. Pool — kopiert. Beim Merge gibt es dann nur zwei mathematisch mögliche
Wege, und beide sind falsch:

- **Halbieren/Anker-gewinnt:** ein Branch-Anteil geht verloren → das beobachtete
  −29%-Leck.
- **Summieren:** beide Kopien werden addiert → **Geld aus dem Nichts**, der
  Split→Merge→Split→Merge-Exploit.

Das ist **kein** Tuning-Problem, sondern strukturell: Ein co-mingled Konto ohne
Eigentümer-Schlüssel ist unter einem Branch/Merge-Modell prinzipiell nicht
konservativ rekonstruierbar. Die Spec ahnt das bereits — sie schreibt
„`economy.hq_pool` bleibt ankergeführt", Gast-`hq_pool` landet in
`continuity_conflicts`. Genau diese „Anker gewinnt"-Regel **ist** der −29%-Leck,
wenn der Nicht-Anker-Branch zwischendurch verdient hat.

---

## 1. Welchen ECHTEN Spielzweck erfüllt ein gemeinsamer Topf?

**Theoretisch dokumentierte Zwecke** (Modul 15 nennt sie):
- Gemeinsame HQ-Anschaffungen / Werkstatt- & Quartier-Upgrades.
- Team-/Fraktions-Assets (das legendäre Tech-IV-Schiff ist explizit
  „Fraktions-Asset … der ganzen Spielerfraktion").
- Research-/Archiv-Spenden, Fraktionsfonds, Hard-Cap-Overflow (>250k → fließt
  „in Fraktionsfonds").

**Praktisch — wie wird gespielt?** Die Belohnungsmechanik zahlt **pro Agent**
(„Jeder von euch erhält 300 CU"), und `apply_wallet_split()` verteilt
anschließend auf die persönlichen Wallets. Fast alle Sinks sind **persönlich**
(Waffen, Implantate, Gear, Wartung 10%/3 Miss., Komfort). Der hq_pool ist im
heutigen Flow vor allem ein **Durchlauf-/Transitkonto** (Rewards landen erst
dort, dann Split), **nicht** ein Konto, aus dem Spieler aktiv kaufen.

**Bewertung:** Es gibt vereinzelte, meist Endgame-/Story-lastige Szenarien, wo
ein geteiltes Asset narrativ Sinn ergibt (Schiff, Fraktionsspende). Aber:
1. Diese sind selten und könnten als **Sink** oder **Story-Beat** abgebildet
   werden, nicht als laufend mitgeführte, co-mingled Balance.
2. Flos Beobachtung trägt: „Niemand will sein solo erspieltes Geld in die
   Gruppe teilen." Ein Topf, der Soloeinkommen automatisch vergemeinschaftet,
   ist ein **Anti-Feature** für das Spielgefühl.

→ Der Topf vermischt zwei Rollen, die nicht zusammengehören: **Transitpuffer**
(kurzlebig) und **persistente Team-Schatzkammer** (langlebig). Dieser
Rollenkonflikt ist die zweite Wurzel der Probleme.

## 2. Solo-Spieler (Mehrheitsfall): Macht ein getrennter HQ-Pool Sinn?

Nein. Für **einen** Spieler gibt es kein „Team" und nichts „Geteiltes". Der
Reward fließt in `hq_pool`, dann 1× Split in das einzige Wallet — zwei Zahlen,
die synchron gehalten und **getrennt** auditiert werden (`economy_audit` prüft
HQ-Band UND Wallet-Band je Level-Stufe, eigene Out-of-Range-Toasts).

Das ist **Doppel-Buchhaltung ohne Mehrwert**: zwei desync-fähige Zahlen, ein
zusätzlicher Toast-/Konflikt-Pfad, mehr Schema-Fläche — für den **Mehrheitsfall**
reiner Overhead. Solo will genau eine Zahl: „mein Konto".

## 3. Abschaffen — was gewinnt/verliert man?

**GEWINN**
- **Exploit weg:** Kein besitzloses, duplizierbares Konto mehr → Split→Merge
  kann keine CU mehr erzeugen.
- **Split/Merge wird trivial:** `economy = Σ wallets`. Jede CU ist ID-besitzt,
  dedupliziert beim Merge **exakt wie Wallets es heute schon tun**. Kein
  Konservierungs-Sonderpfad, keine Halbierung, keine Addition.
- **Eine Wahrheit:** `economy_audit` schrumpft auf Wallet-Bänder; der „erst
  HQ-Buchung, dann Wallet-Split"-Schritt entfällt (Rewards sind ohnehin
  pro-Agent) → schlankerer Debrief.
- **Solo-Overhead weg** für die Mehrheit.
- Weniger Schema/`continuity_conflicts`-Pfade, weniger Halluzinations-Fläche
  für die LLM-SL (die laut Playtests die Pool-Arithmetik gerade nicht
  zuverlässig hinbekommt).

**VERLUST**
- Kein dediziertes geteiltes Konto für echte Team-Käufe. Aber: Eine reale
  Pen&Paper-Gruppe teilt sowieso per „wir legen je 200 zusammen" — abbildbar als
  geteilte Kosten/Erstattung über Wallets.
- Heimat für Fraktionsfonds / Hard-Cap-Overflow muss neu definiert werden. Aber
  ein Fraktionsfonds ist konzeptionell **kein Team-Topf**, sondern ein **Sink**
  (Geld verlässt Spielerkontrolle) — der braucht keine mitgeführte Balance,
  sondern kann reiner Abfluss sein.
- Lore-Verlust „ITI-HQ-Konto" minimal: Das In-World-Konto in der Nullzeit bleibt
  — es **ist** dann einfach das Wallet.

## 4. Alternativen zum kompletten Abschaffen

**(a) Pool nur im Gruppen-Modus, im Solo = Wallet.**
Behebt den Solo-Overhead, aber **behält das Split/Merge-Problem genau in dem
Modus, in dem Split/Merge stattfindet** (Gruppe). Löst die schwierige Hälfte
nicht. Schwach.

**(b) Pool behalten + Konservierungsregel.**
Erfordert Lineage-/Owner-Tracking für den Pool (wer hat welchen Anteil seit dem
Split verdient/ausgegeben). Komplex, fragil, und verlangt verlässliche
Arithmetik von der KI-SL — Playtests zeigen, dass genau das nicht trägt. Hohe
Regel-Last für seltenen Nutzen. Schwach.

**(c) Pool nur als „ungesplitteter Rest", ankergebunden, nie auf Branches.**
Auf dem Split bleibt der Pool **nur beim Anker-Branch**, andere Branches starten
mit `hq_pool = 0`; beim Merge ist der Anker-Pool autoritativ, Branch-Pools werden
ignoriert. Das ist **konservativ** (keine Erzeugung) und konsistent mit der
bereits existierenden SSOT („hq_pool bleibt ankergeführt"). Es ist die beste
„Keep"-Variante — aber es bedeutet, dass der Pool im Branch faktisch tot ist
(die abgespaltete Gruppe kann nicht aus dem gemeinsamen Topf zahlen), was den
einzigen Daseinszweck eines Team-Topfs (gemeinsam ausgeben **während** getrennt)
ohnehin aushöhlt. Funktioniert, ist aber halbherzig.

**(d) Hybrid: Wallets = einziges Spielergeld; Fraktionsfonds als GESCHLÜSSELTES
Sub-Konto.**
Der eigentliche Fix für **jedes** geteilte Geld: gib ihm einen
**Eigentümer-Schlüssel**. Ein Team-Fonds wird modelliert wie ein Wallet, das
einer synthetischen Entität gehört (z. B. `funds[].id = "HQ-FUND"` oder ein
Pseudo-Charakter im Roster). Dann:
- dedupliziert er beim Merge **identisch** wie Wallets (kein Exploit),
- liegt beim Split auf **genau einem** Branch (dem Anker/„wer das HQ trägt") →
  nie dupliziert,
- ist **default-off** und in Solo schlicht abwesend.
So bekommt man eine echte, opt-in Team-Schatzkammer **ohne** das
Konservierungsproblem.

## 5. EMPFEHLUNG

**Abschaffen — mit sauberem Hybrid-Pfad für später.**

Konkret:

1. **`economy.hq_pool` als kanonisches Spielerkonto streichen. Wallets werden
   SSOT:** `economy = Σ characters[].wallet`. Rewards (bereits pro-Agent
   formuliert) fließen direkt in Wallets; der „erst Pool, dann Split"-Schritt
   entfällt.
2. **Split/Merge erbt die bewährte Wallet-Logik:** ID-besitzt, anker-geführt,
   Abweichungen → `continuity_conflicts[]`. Damit ist Split/Merge trivial **und**
   exploit-frei in einem Schritt.
3. **Migration:** `hq_pool` wird beim Laden zum reinen Importpfad (wie
   `economy.cu`/`credits` heute) und kollabiert in das Anker-Charakter-Wallet
   (oder gleichverteilt auf den aktuellen Roster — Designwahl, aber konservativ
   und einmalig).
4. **Echte Team-Schatzkammer NICHT als co-mingled Pool wiederbeleben.** Wenn ein
   konkretes Shared-Purchase-Feature kommt (Schiff, Quartier-Upgrade,
   Fraktionsspende), als **geschlüsseltes, ankergebundenes, default-off**
   `funds`-Sub-Konto (Variante 4d) — niemals als ungeschlüsselter Topf.
5. **Fraktionsfonds/Hard-Cap-Overflow** = reiner **Sink** (Geld raus aus
   Spielerkontrolle), keine mitgeführte Balance nötig.

**Begründung in einem Satz:** Für ein Spiel, das Solo **und** Gruppe **und**
Split/Merge können muss, ist die einzige strukturell saubere Geldeinheit eine,
die **einem Schlüssel gehört** — und das sind die Wallets; ein besitzloser
gemeinsamer Topf ist unter Branch/Merge prinzipiell nicht konservativ und löst
ein Problem (gemeinsames Ausgeben), das im Mehrheitsfall (Solo) gar nicht
existiert und im Gruppenfall realistischer per „zusammenlegen" über Wallets
abgebildet wird.

**Balancing-TODO (kein Blocker):** Die Level-Band-Richtwerte (HQ 8–10k / Wallets
1–2k usw.) müssen neu kalibriert werden — das frühere HQ-Pool-Budget faltet sich
in höhere Pro-Wallet-Zielwerte; `economy_audit` prüft danach nur noch Wallet-
Bänder.

---

*Bewertung, keine Datei-Änderungen am Spiel-Repo. Erstellt für hqpool-design.*
