# Bauplan: Abschaffung von `economy.hq_pool` als gespeicherte Geld-SSOT

> Erstellt 2026-06-16 (Subagent, Code/Schema/Test-Pass). NUR PLAN — keine Datei geändert.
> Repo: `/mnt/agent_share/cloud/repos/ZEITRISS-md-git` @ main `8b6dd411`.
> Zielarchitektur (Flo, steht fest): Geld lebt ausschließlich in Charakter-Wallets;
> Gruppenkasse = berechneter VIEW = Σ Wallets, nicht gespeichert.

---

## 0. Befund-Korrektur vorab (WICHTIG — ändert die Stoßrichtung)

Die Aufgabenstellung beschreibt `economy.hq_pool` als „gespeicherte besitzlose Geld-Zahl,
identisch mit `economy.cu`/`economy.credits` in der Runtime". **Das stimmt — aber mit einer
entscheidenden Nuance, die ich im Code verifiziert habe:**

1. **Die Laufzeit liest `hq_pool` NIE.** Der Primary-Currency-Resolver kennt nur
   `ECONOMY_PRIMARY_KEYS = ['credits','cu','balance','assets']` (runtime.js:2622). `hq_pool`
   ist **nicht** drin. Die gesamte Runtime-Geldlogik (Arena-Gebühr, Markt-Kauf, Wallet-Split)
   arbeitet auf `economy.cu` / `economy.credits`.
2. **`hq_pool` ist reines Serialisierungs-/Audit-Label.** Es taucht auf:
   - im **Save-Schema** als `economy.required: ["hq_pool"]` (beide Schemas),
   - im **Masterprompt-Template** `"economy": { "hq_pool": 0 }` (masterprompt_v6.md:1048),
   - in `build_economy_audit()` als Ausgabefeld `hq_pool: hqPool`, wobei `hqPool` aus
     `economy.cu` gelesen wird (runtime.js:6020, 6051) — also `cu` unter anderem Namen,
   - in allen v7-Fixtures als `"economy": { "hq_pool": N }`.
3. **`prepare_save_economy()` (runtime.js:8168) schreibt `cu`, `credits` UND `wallets`** in den
   Save — aber NICHT `hq_pool`. D.h. der **JS-Runtime-Serializer und das v7-Schema sind heute
   schon divergent**: Runtime produziert `economy.{cu,credits,wallets}`, das Schema verlangt
   `economy.hq_pool`. Die Brücke „cu == hq_pool" existiert nur konzeptionell in der Doku
   (`sl-referenz.md:276`: „economy.cu wird auf economy.hq_pool normalisiert"), nicht als
   echter Transformations-Code im Repo-runtime.js. Der LLM-SL (Masterprompt) ist der eigentliche
   Save-Schreiber im Produktivbetrieb; runtime.js ist Referenz-/Test-Harness.

**Konsequenz für den Umbau:** Es gibt zwei Wahrheits-Ebenen, die getrennt angefasst werden müssen:
- **Ebene A — Produktiv (LLM-Save-Format):** Masterprompt-Template + beide JSON-Schemas +
  Fixtures + Doku. Hier wird `economy.hq_pool` als gespeichertes Feld real abgeschafft.
- **Ebene B — Referenz-Runtime (runtime.js):** Hier muss die *Primary-Currency*-Logik von
  „gespeicherter Topf" auf „berechneter View aus Wallets" umgestellt werden, plus neue
  `transfer_cu`. Das ist der mechanisch heikelste Teil, weil `cu` heute additiv gepflegt wird.

Dieser Befund ist gut, nicht schlecht: weil `hq_pool` nie als Source-of-Truth *gelesen* wird,
ist die Abschaffung als gespeichertes Feld risikoärmer als befürchtet. Das Risiko sitzt in
`economy.cu` (dem realen Runtime-Topf) und in `characters[].wallet` vs `economy.wallets`.

---

## 1. SSOT-Entscheidung (zentraler Architektur-Knoten)

### Ist-Zustand (verifiziert)
Es gibt **drei** parallele Geld-Repräsentationen, die heute nur lose gekoppelt sind:

| Knoten | Typ | Wo | Wer pflegt ihn |
|---|---|---|---|
| `economy.cu` / `economy.credits` | number (besitzlos) | Runtime-State + Save | Arena, Markt, Wallet-Split (additiv), `sync_primary_currency` |
| `economy.wallets{ id: {balance,name} }` | keyed object (Owner = roster-id) | Runtime-State + Save | `apply_wallet_split`, `initialize_wallets_from_roster` |
| `characters[].wallet` | number (pro Charakter) | Save-Schema (required), Masterprompt | LLM-SL schreibt es; **runtime.js reconciliert es NICHT mit `economy.wallets`** |

Das ist der Kern des Exploits: `economy.cu` (Topf) und `economy.wallets` (Owner-Konten) sind
**zwei getrennte Geldmengen**, die im Split additiv verschoben werden, ohne harte
Σ-Konservierung. Und `characters[].wallet` (LLM-Save) ist eine *dritte* Zahl, die mit
`economy.wallets` (runtime) nicht zwingend übereinstimmt.

### Entscheidung: **`characters[].wallet` wird die einzige gespeicherte Geld-SSOT.**

Begründung:
- **Owner-Key ist natürlich.** Jede CU hängt an `character.id`. Split = Charakter nimmt sein
  `wallet` mit; Merge = `characters[]` werden union-iert, jeder bringt sein `wallet`. Konservativ
  per Konstruktion — der von Flo gewünschte „trivial-konservative" Zustand.
- **`characters[]` ist bereits der kanonische Roster-Container in v7** (sl-referenz.md, Index 0 =
  Session-Anker). Geld dort anzusiedeln folgt der existierenden Roster-SSOT statt eine zweite
  (`economy.wallets`) zu pflegen.
- **Gruppenkasse = `Σ characters[].wallet`** als reiner View. Nicht gespeichert.

Daraus folgt:
- **`economy.hq_pool`** (gespeicherter Topf): **abgeschafft** (Schema, Template, Fixtures, Doku).
- **`economy.cu` / `economy.credits`** (Runtime-Primary): wird vom *gespeicherten Topf* zum
  **berechneten View** `= sum_wallet_balances()`. Bleibt als abgeleiteter Laufzeitwert für
  Rückwärtskompatibilität (HUD, Arena-Resolver, Legacy-Importpfad), wird aber **nie mehr als
  eigenständige Geldmenge persistiert oder additiv mutiert**.
- **`economy.wallets`** (runtime keyed object): bleibt die **Laufzeit-Arbeitsstruktur**, deren
  Keys mit `characters[].id` deckungsgleich sind. Beim Save wird sie nach `characters[].wallet`
  projiziert (Owner-Key = character.id); beim Load wird sie aus `characters[].wallet`
  rehydriert. `economy.wallets` ist also Runtime-Spiegel der SSOT, nicht zweite SSOT.

### Sync-/Migrationsregel (roter Faden Konservativität)
- **Load:** `characters[].wallet` → `economy.wallets[char.id].balance`. Danach
  `economy.cu = economy.credits = Σ balances` (View). Legacy `economy.hq_pool`/`economy.cu` aus
  Altsaves → einmalig konservativ ins Anker-Wallet falten (siehe §5).
- **Save:** `economy.wallets[id].balance` → `characters[id].wallet`. `economy` bekommt **kein**
  `hq_pool` mehr; `cu`/`credits` werden als abgeleitete Summe weiter geschrieben (Legacy-Kompat,
  optional — siehe §3 Schema-Entscheidung) ODER ganz aus dem Save entfernt.
- **Invariante nach jeder Operation:** `Σ characters[].wallet == group_treasury_view()`. Kein
  Wert lebt außerhalb eines Owner-Keys.

> **Offene Designfrage D1 (Orchestrator/Flo):** Soll `economy.cu`/`credits` im Save *ganz
> verschwinden* (sauberster Schnitt, aber Legacy-Tools/Doku-Bridge brechen) oder als
> **abgeleiteter Read-Only-Spiegel** (`= Σ wallets`) erhalten bleiben (weicher, aber suggeriert
> fälschlich einen Topf)? Empfehlung unten: **erhalten als expliziter View-Cache** mit Kommentar,
> weil zu viele Stellen (HUD, Arena, sl-referenz) `cu` referenzieren. Schnitt sonst zu breit.

---

## 2. runtime.js — Diffs nach Funktion

### 2.1 `ECONOMY_PRIMARY_KEYS` + `resolve_primary_currency` (Z2622–2647)
**Neu:** Primary Currency wird aus Wallets abgeleitet statt aus einem gespeicherten Feld.

```js
// VORHER
const ECONOMY_PRIMARY_KEYS = ['credits', 'cu', 'balance', 'assets'];
function resolve_primary_currency(economy){
  if (!economy || typeof economy !== 'object') return 0;
  for (const key of ECONOMY_PRIMARY_KEYS){
    if (!(key in economy)) continue;
    const normalized = normalize_primary_currency(economy[key]);
    if (normalized !== null) return normalized;
  }
  return 0;
}

// NACHHER
// Legacy-Importkeys NUR noch für Altsave-Faltung (siehe migrate). Reihenfolge =
// Faltungspriorität beim Laden alter Saves; im Live-Betrieb ungenutzt.
const ECONOMY_LEGACY_POOL_KEYS = ['hq_pool', 'credits', 'cu', 'balance', 'assets'];

// Primary Currency = berechneter VIEW = Σ Wallet-Balances. KEIN gespeichertes Feld mehr.
function resolve_primary_currency(economy){
  if (!economy || typeof economy !== 'object') return 0;
  const { total } = sum_wallet_balances(economy.wallets);
  return total;
}
```

> `sum_wallet_balances` ist vor `resolve_primary_currency` definiert? Nein — heute steht
> `sum_wallet_balances` bei Z5929, `resolve_primary_currency` bei Z2631. JS-Funktionsdeklarationen
> sind gehoistet (function declarations), also funktioniert der Vorwärtsbezug. **Verifizieren:**
> beide sind `function name(){}`-Deklarationen (ja), kein `const fn =`. Hoisting greift. OK.

### 2.2 `sync_primary_currency` (Z2674–2706)
Heute setzt es `economy.cu = economy.credits = amount` (Topf-Schreiben). Neu: es darf den
View nicht mehr „setzen", sondern nur noch spiegeln. Da extrem viele Caller `sync_primary_currency`
aufrufen (Arena, Markt, Split, Load), ist der **konservativste Umbau**: Funktion behalten, aber
`override` ignorieren und immer auf den View-Wert zwingen.

```js
// NACHHER
function sync_primary_currency(economy, override, trace){
  if (!economy || typeof economy !== 'object') return 0;
  const before = Number.isFinite(economy.cu) ? economy.cu : 0;
  // SSOT ist Σ Wallets. override wird IGNORIERT (Legacy-Param), nur noch View-Spiegel.
  const amount = resolve_primary_currency(economy); // = Σ wallets
  economy.cu = amount;
  economy.credits = amount;          // Read-Only-Spiegel, NICHT als Topf nutzen
  const traceReason = typeof trace === 'object' && !Array.isArray(trace)
    ? trace.reason || trace.event || trace.type : trace;
  record_currency_sync(traceReason, before, amount, typeof trace === 'object' ? trace : null);
  return amount;
}
```

> **Achtung Verhaltensänderung:** Alle Caller, die heute `sync_primary_currency(economy, X)` mit
> einem expliziten Betrag riefen (Arena `writeArenaCurrency`, Markt, Split), bekommen jetzt den
> View. Das ist gewollt — die Geldänderung muss VORHER in den Wallets passiert sein, dann ist der
> View korrekt. Jede dieser Call-Sites muss umgebaut werden (siehe unten). Wer das vergisst, sieht
> den alten Betrag „wieder auftauchen" → Test-Canary nötig.

### 2.3 `ensure_economy` (Z2698–2706)
Bleibt fast gleich; Reihenfolge wichtig: erst Wallets sicherstellen, DANN View berechnen.

```js
function ensure_economy(){
  if (!state.economy || typeof state.economy !== 'object') state.economy = {};
  const economy = state.economy;
  ensure_wallets();              // ZUERST — View hängt davon ab
  sync_primary_currency(economy); // setzt economy.cu/credits = Σ wallets
  // Hard guarantee: kein gespeicherter Topf mehr
  if ('hq_pool' in economy) delete economy.hq_pool;
  return economy;
}
```

### 2.4 `log_market_purchase` (Z1711–1747) — Kauf aus Käufer-Wallet, scheitert bei Unterdeckung
Heute: `economy.cu = next` (Topf-Abzug). Neu: Abzug aus **dem Wallet des kaufenden Charakters**;
reicht es nicht → **scheitern**.

Käufer-Herkunft: heute hat `log_market_purchase(item, cost, options)` **keinen** Käufer-Parameter.
Vorschlag: `options.buyer_id` (oder `options.character_id`); Fallback = Anker-Charakter
(`build_wallet_roster().roster[0].id`, = `characters[0]`/`ensure_character()`).

Signalisierung „scheitern": **throw** (konsistent mit bestehendem `throw new Error('MarketLog:
Ungültiger Eintrag.')` und Arena-Gebühr-`throw`). Der HUD-Toast wird vom Caller/Catch erzeugt.

```js
function log_market_purchase(item, cost, options = {}){
  const payload = { ...options, item, cost_cu: cost };
  if (options.timestamp){ const iso = isoTimestamp(options.timestamp); if (iso) payload.timestamp = iso; }
  const marketLog = ensure_market_log();
  const normalized = normalize_market_entry(payload, new Date().toISOString());
  if (!normalized) throw new Error('MarketLog: Ungültiger Eintrag.');

  const costValue = normalize_primary_currency(normalized.cost_cu);
  if (costValue !== null && costValue > 0){
    const economy = ensure_economy();
    // Käufer bestimmen: explizit oder Anker (characters[0]).
    const rosterInfo = build_wallet_roster();
    const buyerId = (typeof options.buyer_id === 'string' && options.buyer_id.trim())
      || (typeof options.character_id === 'string' && options.character_id.trim())
      || (rosterInfo.roster[0] && rosterInfo.roster[0].id);
    if (!buyerId) throw new Error('Markt-Kauf: Kein Käufer-Wallet bestimmbar.');
    const record = get_wallet_record(buyerId, rosterInfo.indexById.has(buyerId)
      ? rosterInfo.roster[rosterInfo.indexById.get(buyerId)].label : null);
    const balance = Math.max(0, Math.round(record.balance || 0));
    if (balance < costValue){
      // KEIN Mitfinanzieren, KEIN Topf — Kauf scheitert.
      throw new Error(
        `Kauf gescheitert: ${normalized.item || 'Artikel'} kostet ${costValue} CU, ` +
        `Wallet ${record.name || buyerId} hat nur ${balance} CU.`);
    }
    record.balance = balance - costValue;
    sync_primary_currency(economy, undefined, { reason: 'market_purchase', note: normalized.item || null });
  }
  marketLog.push(normalized);
  state.logs.market = marketLog;
  if (marketLog.length > MARKET_LOG_LIMIT) marketLog.splice(0, marketLog.length - MARKET_LOG_LIMIT);
  return normalized;
}
```

> **Offene Designfrage D2:** Soll ein Markt-Kauf-`throw` einen HUD-Toast erzwingen? Empfehlung:
> ja, aber im **Caller** (z.B. `run_shop_checks`/Debrief-Shop-Handler), wo der UI-Kontext sitzt.
> `log_market_purchase` bleibt rein transaktional + wirft. Wo wird `log_market_purchase` aufgerufen?
> Im LLM-Produktivbetrieb gar nicht direkt (LLM bucht selbst). Im Harness via `tools/test_shop.js`
> / Debrief. **Verifizieren, dass alle Caller den throw fangen** (sonst Test-Crash statt Toast).

### 2.5 `apply_wallet_split` (Z5858–5907) — alles direkt in Wallets, KEIN Pool
Heute: Hazard-Pay → `economy.cu` (Topf); Reward → `economy.cu += reward`, dann Allokationen aus
dem Topf in Wallets verschoben; **unteilbarer Leftover bleibt im HQ-Pool** (`Rest … CU im HQ-Pool`).

Neu: Reward + Hazard fließen **direkt** in Wallets. Kein `economy.cu`-Topf-Schreiben mehr.
Leftover-Entscheidung (Flo): **runde in Anker-Wallet** (= `rosterInfo.roster[0]`, characters[0]).

```js
function apply_wallet_split(outcome, cuReward){
  const economy = ensure_economy();
  const rosterInfo = build_wallet_roster();
  const anchorId = rosterInfo.roster[0] ? rosterInfo.roster[0].id : null;
  const lines = [];

  // Hazard-Pay: kein Topf mehr -> als zusätzlicher Reward-Anteil an Anker (oder verteilt).
  const hazardSource = outcome?.economy?.hazard_pay ?? outcome?.hazard_pay ?? outcome?.economy?.hazard;
  const hazardPay = normalize_cu(hazardSource);
  if (hazardPay !== null && hazardPay > 0 && anchorId){
    const rec = get_wallet_record(anchorId, rosterInfo.roster[0].label);
    rec.balance = Math.max(0, Math.round(rec.balance || 0) + hazardPay);
    lines.push(`Hazard-Pay: ${hazardPay} CU an ${rec.name || anchorId}.`);
  }

  const reward = normalize_cu(cuReward);
  if (reward === null || reward <= 0){
    sync_primary_currency(economy);
    const treasury = group_treasury_view();
    lines.push(`Gruppenkasse: ${treasury} CU (Σ Wallets).`);
    return { lines, payout: hazardPay || 0, leftover: 0 };
  }

  const instructions = gather_wallet_instructions(outcome, rosterInfo);
  const { allocations, totalAssigned, leftover } = compute_wallet_allocations(reward, rosterInfo, instructions);

  // Direkt in Wallets buchen (KEIN economy.cu-Zwischentopf).
  allocations.forEach((entry) => {
    const record = get_wallet_record(entry.id, entry.label);
    if (!record) return;
    record.balance = Math.max(0, Math.round(record.balance || 0) + entry.amount);
    if (!record.name && entry.label) record.name = entry.label;
  });
  // Unteilbarer Leftover -> Anker-Wallet (konservativ, geht nicht verloren, kein Topf).
  if (leftover > 0 && anchorId){
    const rec = get_wallet_record(anchorId, rosterInfo.roster[0].label);
    rec.balance = Math.max(0, Math.round(rec.balance || 0) + leftover);
  }
  if (allocations.length){
    const summary = allocations.map((e) => `${e.label || e.id} +${e.amount} CU`).join(' | ');
    lines.push(`Wallet-Split (${allocations.length}×): ${summary}`);
  }
  sync_primary_currency(economy); // View neu berechnen
  const treasury = group_treasury_view();
  const remainderText = leftover > 0 ? ` (Rundungsrest ${leftover} CU an Anker-Wallet)` : '';
  lines.push(`Gruppenkasse: ${treasury} CU (Σ Wallets)${remainderText}.`);
  return { lines, payout: totalAssigned + leftover, leftover: 0 }; // leftover ist jetzt verbucht
}
```

> **HUD-Text-Drift:** Der String „HQ-Pool: … CU verfügbar" verschwindet zugunsten „Gruppenkasse:
> … CU (Σ Wallets)". Das berührt Watchguards/Smoke-Greps (sl-referenz, debrief-Tests). Siehe §4.
> **Verifizieren:** `grep -rn "HQ-Pool" tools/ scripts/ *.md` — alle Erwartungs-Strings finden.

### 2.6 `build_wallet_roster` / `normalize_wallet_instruction` / `gather_wallet_instructions` / `compute_wallet_allocations`
Bleiben **strukturell unverändert** — sie verteilen einen Gesamtbetrag deterministisch auf
Owner-Keys. Das passt zur neuen Welt 1:1. Einzige Anpassung: `compute_wallet_allocations` gibt
`leftover` weiter zurück, der Caller (`apply_wallet_split`) bucht ihn jetzt ins Anker-Wallet statt
in den Topf. Keine Signaturänderung nötig.

### 2.7 `initialize_wallets_from_roster` (Z5909–5927)
Heute legt es leere Wallets (balance 0) für alle Roster-IDs an. Doku (`sl-referenz.md:1264`)
behauptet, es „verschiebt alte Solo-Guthaben vollständig in den HQ-Pool" — das macht der **Code
gar nicht** (er setzt nur balance:0 für fehlende). Neu (zur SSOT-Konsolidierung): beim ersten
Anlegen die `characters[].wallet`-Werte übernehmen.

```js
function initialize_wallets_from_roster(){
  ensure_economy();
  const wallets = wallet_lookup();
  const { roster } = build_wallet_roster();
  let created = 0;
  roster.forEach((entry) => {
    if (!entry || !entry.id) return;
    if (!wallets[entry.id]){
      // Startguthaben aus characters[].wallet (SSOT) übernehmen, sonst 0.
      const seed = wallet_seed_from_character(entry.id); // neue Helferfunktion, liest characters[].wallet
      wallets[entry.id] = { balance: Math.max(0, Math.round(seed || 0)), name: entry.label || null };
      created += 1;
    } else if (!wallets[entry.id].name && entry.label){
      wallets[entry.id].name = entry.label;
    }
  });
  if (created > 0) hud_toast(`Wallets initialisiert (${created}×)`, 'HQ');
  return created;
}
```

> **Offene Designfrage D3:** Woher liest `wallet_seed_from_character(id)` den Startwert? In der
> Referenz-Runtime ist `characters[]` nicht der Live-Container (state nutzt `character`+`party`).
> Heute steht `wallet` an `state.character.wallet` / `party.characters[].wallet`? **Verifizieren:**
> `grep -n "\.wallet" runtime.js` lieferte 0 Treffer auf Lese-Seite — d.h. runtime.js liest
> `characters[].wallet` aktuell NIRGENDS. Das ist die eigentliche Lücke. Der Orchestrator muss
> entscheiden, ob die Referenz-Runtime `characters[].wallet` überhaupt verdrahten soll oder ob
> die SSOT-Projektion nur im LLM-Save-Format (Ebene A) + Migrations-Load (§5) lebt. **Empfehlung:**
> minimale Verdrahtung in load/save (siehe 2.10), Live-Arbeitsstruktur bleibt `economy.wallets`.

### 2.8 `sum_wallet_balances` (Z5929–5943) + neue `group_treasury_view`
`sum_wallet_balances` existiert und passt. Neu: dünner offizieller View-Alias.

```js
// Offizieller Gruppenkasse-View (= Σ Wallets), NICHT gespeichert.
function group_treasury_view(economy = state.economy){
  return sum_wallet_balances(economy && economy.wallets).total;
}
```

### 2.9 NEU: `transfer_cu(fromId, toId, amount)` — Wallet→Wallet, streng konservativ
```js
function transfer_cu(fromId, toId, amount){
  const economy = ensure_economy();
  const wallets = wallet_lookup();
  const amt = normalize_cu(amount);
  // Validierung
  if (amt === null || amt <= 0) throw new Error('Transfer: Betrag muss positiv sein.');
  const from = normalize_wallet_id(fromId);
  const to   = normalize_wallet_id(toId);
  if (!from || !to) throw new Error('Transfer: Ungültige Wallet-ID.');
  if (from === to) throw new Error('Transfer: Quelle und Ziel identisch.');
  if (!wallets[from]) throw new Error(`Transfer: Quell-Wallet ${from} existiert nicht.`);
  if (!wallets[to])   throw new Error(`Transfer: Ziel-Wallet ${to} existiert nicht.`);
  const fromBal = Math.max(0, Math.round(wallets[from].balance || 0));
  if (fromBal < amt) throw new Error(
    `Transfer gescheitert: ${wallets[from].name || from} hat nur ${fromBal} CU (benötigt ${amt}).`);
  // Konservative Verschiebung
  const before = group_treasury_view(economy);
  wallets[from].balance = fromBal - amt;
  wallets[to].balance   = Math.max(0, Math.round(wallets[to].balance || 0)) + amt;
  sync_primary_currency(economy); // View-Spiegel aktualisieren
  const after = group_treasury_view(economy);
  // Σ-Invariante (defensiv): Gesamtsumme MUSS gleich bleiben.
  if (before !== after) throw new Error(`Transfer-Invariante verletzt: ${before} != ${after}`);
  record_currency_sync('wallet_transfer', before, after,
    { note: `${from}->${to}: ${amt} CU`, source: 'transfer' });
  hud_toast(`Transfer: ${amt} CU ${wallets[from].name || from} → ${wallets[to].name || to}`, 'HQ');
  return { from, to, amount: amt, treasury: after };
}
```
Export in der module.exports-Liste (Z10481-Bereich) ergänzen: `transfer_cu`, `group_treasury_view`.

### 2.10 Arena-Gebühr (`readArenaCurrency`/`writeArenaCurrency`/`arenaStart`, Z6237/6665–6826)
Heute: Gebühr wird aus Primary-Currency (Topf) gezogen via `writeArenaCurrency(key, value-fee)`.
Neu (Flo-Vorschlag): aus dem **Wallet des die-Arena-betretenden Charakters**; in Koop = Initiator.

```js
// readArenaCurrency: liest jetzt das Initiator-Wallet statt economy[key].
function readArenaCurrency(options = {}){
  const economy = ensure_economy();
  const rosterInfo = build_wallet_roster();
  const initiatorId = (typeof options.initiator_id === 'string' && options.initiator_id.trim())
    || (rosterInfo.roster[0] && rosterInfo.roster[0].id);
  const record = initiatorId ? get_wallet_record(initiatorId,
    rosterInfo.indexById.has(initiatorId) ? rosterInfo.roster[rosterInfo.indexById.get(initiatorId)].label : null) : null;
  const value = record ? Math.max(0, Math.round(record.balance || 0)) : 0;
  return { id: initiatorId, value };
}

// writeArenaCurrency: zieht aus dem Initiator-Wallet ab.
function writeArenaFee(initiatorId, fee, reason = 'arena_fee'){
  const economy = ensure_economy();
  const record = get_wallet_record(initiatorId);
  record.balance = Math.max(0, Math.round(record.balance || 0) - Math.max(0, Math.round(fee)));
  sync_primary_currency(economy, undefined, { reason, source: 'arena' });
}
```
In `arenaStart`:
```js
  const { id: initiatorId, value } = readArenaCurrency(options);
  const fee = getArenaFee(value);
  if (value < fee) throw new Error('Arena-Gebühr kann nicht bezahlt werden. Initiator-Wallet prüfen.');
  ...
  writeArenaFee(initiatorId, fee, 'arena_fee');
```

> **Offene Designfrage D4:** `getArenaFee` skaliert mit der verfügbaren Currency (Brackets über
> `value`). Heute war `value` der ganze HQ-Topf; jetzt ist es nur das Initiator-Wallet → die
> prozentuale Gebühr fällt niedriger aus. Gewollt? Falls die Gebühr weiter auf Gruppenvermögen
> skalieren soll: `getArenaFee(group_treasury_view())`, aber **bezahlt** wird trotzdem aus dem
> Initiator-Wallet (kann dann ggf. nicht decken → scheitert → Spieler muss per `transfer_cu`
> zusammenlegen). Empfehlung: Gebühr auf `group_treasury_view()` skalieren (Balancing-Konsistenz),
> Bezahlung aus Initiator-Wallet (Owner-Prinzip). Flo entscheiden lassen.

### 2.11 `build_economy_audit` / `economy_audit_guidelines` / `maybe_toast_economy_audit` (Z5954–6075)
Heute prüft das Audit **zwei** Bänder getrennt: `hq_pool` (8000/25000/45000…) UND `wallet_avg`.
Neu: kein `hq_pool`-Zielwert mehr — Bänder rein auf Wallet-Logik (+ Gruppenkasse als Σ). Siehe §6
für die konkreten neuen Bandwerte. Code:

```js
function economy_audit_guidelines(level, walletCount){
  if (!Number.isFinite(level)) return null;
  let band=null, walletMin=null, walletMax=null;
  if (level >= 900){ band='900+'; walletMin=7000; walletMax=12000; }
  else if (level >= 512){ band='512'; walletMin=3500; walletMax=6000; }
  else if (level >= 120){ band='120'; walletMin=1200; walletMax=2400; }
  if (!band) return null;
  const treasury = walletCount > 0 ? { min: walletMin*walletCount, max: walletMax*walletCount } : null;
  return {
    level_band: band,
    targets: {
      wallet_avg: { min: walletMin, max: walletMax },
      treasury        // = Σ-Wallet-Zielband (ersetzt hq_pool-Band)
    }
  };
}

function build_economy_audit(s){
  const economy = s?.economy || {};
  const { total: walletSum, count: walletCount } = sum_wallet_balances(economy.wallets);
  const treasury = walletSum; // Gruppenkasse = Σ Wallets (View)
  const walletAvg = walletCount > 0 ? Math.round(walletSum / walletCount) : null;
  const { level, band_reason: bandReason } = resolve_economy_audit_level(s);
  const guidelines = economy_audit_guidelines(level, walletCount);
  const chronopolis = sum_market_spend(s?.logs);
  const targetRange = guidelines ? { ...guidelines.targets, level_band: guidelines.level_band } : null;
  const deltaFor = (v, r) => { if (!r || v==null) return null; if (v<r.min) return v-r.min; if (v>r.max) return v-r.max; return 0; };
  const delta = targetRange ? {
    treasury: deltaFor(treasury, targetRange.treasury),
    wallet_avg: deltaFor(walletAvg, targetRange.wallet_avg)
  } : null;
  const outOfRange = delta ? {
    treasury: delta.treasury !== null && delta.treasury !== 0,
    wallet_avg: delta.wallet_avg !== null && delta.wallet_avg !== 0
  } : null;
  return {
    level, band_reason: bandReason,
    treasury, wallet_sum: walletSum, wallet_count: walletCount,
    wallet_avg: walletAvg, wallet_avg_scope: 'economy.wallets',
    target_range: targetRange, delta,
    chronopolis_sinks: chronopolis, out_of_range: outOfRange
    // hq_pool-Feld ENTFERNT
  };
}

function maybe_toast_economy_audit(audit){
  if (!audit?.out_of_range) return;
  const parts = [];
  if (audit.out_of_range.treasury) parts.push('Gruppenkasse');
  if (audit.out_of_range.wallet_avg) parts.push('Wallets');
  const scope = parts.length ? parts.join('/') : 'Ökonomie';
  const band = audit.target_range ? `Lvl ${audit.target_range.level_band || audit.level || 'n/a'}` : 'Endgame';
  hud_toast(`Economy-Audit: ${scope} außerhalb Richtwerten (${band}).`, 'HQ');
}
```

> **Breaking für Tests:** `test_v7_issue_pack.js` prüft `target_range.level_band` (bleibt OK) und
> die Fixtures tragen `economy_audit`-Traces mit `hq_pool`-Feld. Audit-Trace-Felder ändern sich
> (`treasury` statt `hq_pool`). Siehe §4.

### 2.12 `prepare_save_economy` (Z8168–8190)
Heute schreibt es `cu`, `credits`, `wallets`. Neu: `hq_pool` weiterhin NICHT schreiben (war eh
nicht drin); `cu`/`credits` optional als View-Spiegel; **Owner-Projektion nach `characters[]`
passiert separat** (siehe 2.13). Mindestens: sicherstellen, dass kein `hq_pool` reinleckt.

```js
function prepare_save_economy(economy){
  const base = clone_plain_object(economy) || {};
  if ('hq_pool' in base) delete base.hq_pool; // niemals gespeicherten Topf exportieren
  const wallets = {};
  if (base.wallets && typeof base.wallets === 'object' && !Array.isArray(base.wallets)){
    for (const [key, value] of Object.entries(base.wallets)){
      const id = normalize_wallet_id(key); if (!id) continue;
      const record = normalize_wallet_record(value); if (!record) continue;
      wallets[id] = { balance: record.balance, ...(record.name ? { name: record.name } : {}) };
    }
  }
  base.wallets = wallets;
  const primary = sum_wallet_balances(wallets).total;
  base.cu = primary; base.credits = primary; // View-Spiegel (siehe D1)
  return base;
}
```

### 2.13 Load-/Save-Owner-Projektion (`hydrate_state` Z9141 + `select_state_for_save` Z8861)
Dies ist die **Verdrahtung von `characters[].wallet` ↔ `economy.wallets`**, die heute fehlt.
Referenz-Runtime hält Roster in `character`+`party.characters[]`+`team.members[]`. Plan:

- **Load (`hydrate_state` / `load_save` Z9735ff):** Nach `ensure_economy()` einmal
  `migrate_legacy_economy_to_wallets(data)` (§5) ausführen, danach
  `initialize_wallets_from_roster()` (das jetzt `characters[].wallet`-Seeds übernimmt).
- **Save (`select_state_for_save`):** Nach `prepare_save_party` die `economy.wallets[id].balance`
  in die jeweiligen `party.characters[].wallet` (und ggf. `character.wallet`) zurückschreiben, so
  dass der gespeicherte `characters[].wallet` == runtime-Wallet ist. Helfer:
  `project_wallets_to_characters(payload)`.

> **Offene Designfrage D5:** Ob die Referenz-Runtime diese Projektion wirklich braucht, hängt
> daran, ob `tools/test_save.js`/`test_load.js` Roundtrip-Gleichheit von `characters[].wallet`
> prüfen. **Verifizieren** (siehe §4). Wenn die Tests nur `economy.wallets` prüfen, kann die
> Projektion zunächst minimal bleiben (nur Schema-Konformität). Sauberer ist die volle Projektion.

---

## 3. Schema-Diffs (die 2 harten Breaks)

### 3.1 `systems/gameflow/saveGame.v7.schema.json` (Z146–158, `additionalProperties:true`)
```jsonc
// VORHER
"economy": {
  "type": "object",
  "additionalProperties": true,
  "required": ["hq_pool"],
  "properties": { "hq_pool": { "type": "number" } }
}
// NACHHER
"economy": {
  "type": "object",
  "additionalProperties": true,
  "required": ["wallets"],
  "properties": {
    "wallets": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["balance"],
        "properties": {
          "balance": { "type": "number" },
          "name": { "type": "string" }
        }
      }
    },
    "cu": { "type": "number" },        // optionaler View-Spiegel (D1)
    "credits": { "type": "number" }
  }
}
```
Da `additionalProperties:true`, bleibt `cu`/`credits` ohnehin erlaubt; explizite Properties nur zur
Doku. **`required` wechselt von `hq_pool` auf `wallets`.**

> **Offene Designfrage D6:** Soll die echte gespeicherte SSOT `characters[].wallet` sein (dann ist
> `economy.wallets` im Save *redundant* und sollte vielleicht NICHT required sein), oder
> `economy.wallets`? Konsistent mit §1-Entscheidung (`characters[].wallet` = SSOT) wäre:
> `economy` braucht **gar kein** required-Feld mehr (`required: []` bzw. weglassen), weil die
> Gruppenkasse ein View ist und Geld in `characters[].wallet` liegt. **Empfehlung:** `economy`
> ohne `required` (leeres Objekt erlaubt), `characters[].wallet` bleibt required (ist es schon,
> Z108). Das ist der sauberste Ausdruck von „Geld lebt nur in Wallets". `economy.wallets` dann nur
> optionaler Runtime-Cache. → **Diese Variante bevorzuge ich; sie macht das Export-Schema unten
> einfacher.**

**Bevorzugte Variante (economy ohne required):**
```jsonc
"economy": {
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "wallets": { "type": "object" },
    "cu": { "type": "number" },
    "credits": { "type": "number" }
  }
}
```

### 3.2 `systems/gameflow/saveGame.v7.export.schema.json` (Z296–306, `additionalProperties:false` — hart!)
Weil `additionalProperties:false`, muss das economy-Objekt exakt passen. Mit der bevorzugten
Variante:
```jsonc
// VORHER
"economy": {
  "type": "object",
  "additionalProperties": false,
  "required": ["hq_pool"],
  "properties": { "hq_pool": { "type": "number" } }
}
// NACHHER
"economy": {
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "wallets": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "additionalProperties": false,
        "required": ["balance"],
        "properties": {
          "balance": { "type": "number" },
          "name": { "type": "string" }
        }
      }
    },
    "cu": { "type": "number" },
    "credits": { "type": "number" }
  }
}
```
> **Kritisch wegen `additionalProperties:false`:** Was immer `prepare_save_economy` real ausgibt,
> MUSS exakt durch dieses Schema gedeckt sein. Ausgabe ist heute `{cu, credits, wallets}`. Mit
> obigem Schema passt das. Falls D1 entscheidet `cu`/`credits` aus dem Save zu entfernen → die
> beiden Properties hier streichen. Falls `economy` ganz leer sein darf, bleibt es valide (kein
> required). **Verifizieren:** `merge_assert.py` lädt dieses Schema live → Selbsttest muss grün
> bleiben (es prüft heute u.a. `economy.hq_pool` in `total_wealth`, siehe §4.2).

---

## 4. Test-/Fixture-Plan

### 4.1 `tools/test_v7_issue_pack.js:18`
```js
// VORHER
assert.ok(save.economy && Number.isFinite(save.economy.hq_pool), `${label}: economy.hq_pool fehlt.`);
// NACHHER — neue Wahrheit: Geld in characters[].wallet, Gruppenkasse = Σ
assert.ok(save.economy && typeof save.economy === 'object', `${label}: economy-Block fehlt.`);
assert.ok(save.characters.every((c) => Number.isFinite(c.wallet)),
  `${label}: jedes characters[].wallet muss numerisch sein (Geld-SSOT).`);
// optionaler View-Spiegel-Check, falls economy.cu mitgeschrieben wird:
if (Number.isFinite(save.economy.cu)){
  const sumWallets = save.characters.reduce((s,c)=>s+(Number.isFinite(c.wallet)?c.wallet:0),0);
  // economy.cu ist View = Σ characters[].wallet (Toleranz: economy.wallets kann Subset/Spiegel sein)
}
```
Außerdem: die `5er-highlevel`-Assertion nutzt `auditBand` aus dem `economy_audit`-Trace
(`target_range.level_band`) — bleibt gültig, da `level_band` erhalten. Aber: die Fixture-Traces
enthalten `hq_pool`-Felder → siehe Fixture-Migration unten.

### 4.2 `playtests/zeitriss/harness/merge_assert.py`
- `total_wealth()` (Z~) liest `economy.hq_pool + Σ characters[].wallet`. **Neu:** `hq_pool` raus,
  Gesamtvermögen = `Σ characters[].wallet` (optional + `economy.wallets`-Sicherung, falls
  characters fehlen). Da Geld jetzt nur in Wallets lebt, ist `total_wealth = Σ characters[].wallet`.
  ```python
  def total_wealth(save: dict) -> float:
      wallets = 0.0
      for c in save.get("characters", []):
          w = c.get("wallet")
          if isinstance(w, (int, float)): wallets += w
      # Fallback: falls economy.wallets vorhanden und characters leer
      if not wallets:
          for rec in (save.get("economy") or {}).get("wallets", {}).values():
              b = rec.get("balance") if isinstance(rec, dict) else None
              if isinstance(b,(int,float)): wallets += b
      return float(wallets)
  ```
- `assert_merge()` Block „2) economy.hq_pool ist ankergeführt" + „4b) HQ-Pool-Leck" + die
  ANCHOR-ECON/HQ-POOL-LEAK-Codes: auf Wallet-Wahrheit umstellen. Da es **keinen Topf** mehr gibt,
  entfällt die ganze „ankergeführter hq_pool"-Logik. Der **WEALTH-EXPLOIT/-LEAK-Guard
  (`assert_wealth_conservation`) wird wichtiger** und bleibt — er prüft jetzt rein
  `Σ characters[].wallet`. Das ist genau die Konservativitäts-Garantie, die Flo will.
- `--selftest` baut künstliche anchors mit `economy.hq_pool` (Z~ „anchor_w = {economy:{hq_pool:1000}...}").
  Diese Selbsttest-Fixtures auf Wallet-only umstellen:
  ```python
  anchor_w = {"characters":[{"id":"A","wallet":1000},{"id":"B","wallet":500}]}
  merge_inflated = {"characters":[{"id":"A","wallet":1500},{"id":"B","wallet":1000}]}
  merge_conserved = {"characters":[{"id":"A","wallet":1000},{"id":"B","wallet":500}]}
  ```
- Schema-Selbsttest: lädt `saveGame.v7.export.schema.json` live → nach Schema-Diff muss
  `python3 harness/merge_assert.py --selftest` grün bleiben. **VBR: ausführen.**

### 4.3 Fixtures unter `internal/qa/fixtures/savegame_v7*.json`
Alle v7-Fixtures haben `economy: { hq_pool: N }` und **kein** `economy.wallets`:

| Fixture | hq_pool | Migration |
|---|---|---|
| `savegame_v7_5er_hq_highlevel.json` | 53200 | → in Wallets falten; characters[].wallet existiert schon, hq_pool zusätzlich → Anker-Wallet (characters[0]) +53200 ODER gleichverteilt. Achtung: Audit-Band 900+. |
| `savegame_v7_level_history.json` | 53200 | dito |
| `savegame_v7_level_history_attrs_gedeckt.json` | 53200 | dito |
| `savegame_v7_chat_load.json` | 6400 | → Anker-Wallet |
| `savegame_v7_abort_resume.json` | 11100 | → Anker-Wallet |
| `savegame_v7_merge_rift_pvp.json` | 22600 | → Anker-Wallet (Merge-Fixture: prüfen ob WEALTH-Guard danach grün) |
| `savegame_v7_arena_round_checkpoint.json` | 3000 | → Anker-Wallet |
| `savegame_v7_chronopolis_roundtrip.json` | 19800 | → Anker-Wallet |
| `savegame_v7_split_3_2_merge.json` | 18300 | → Anker-Wallet (WICHTIG: WEALTH-Konservierung über Split/Merge — neue Summe muss konsistent sein) |
| `savegame_v7_personal_export_from_group.json` | 0 | trivial: `economy.hq_pool` → entfernen; Geld liegt schon in `characters[0].wallet=1450` |

**Migrations-Regel (einmalig, konservativ):** Pro Fixture `economy.hq_pool` entfernen; den Betrag
**ins Anker-Wallet `characters[0].wallet` addieren** (empfohlen, siehe §5-Begründung) und
optional `economy.wallets` aus `characters[].wallet` aufbauen, falls Tests es erwarten. Die
`economy_audit`-Traces in den Fixtures (`hq_pool: 8500` etc., in `logs.trace`) ebenfalls auf neue
Audit-Struktur (`treasury` statt `hq_pool`) umschreiben — sonst schlägt evtl. ein Trace-Konsistenz-
Watchguard an. **Verifizieren:** `grep -rn '"hq_pool"' internal/qa/fixtures/savegame_v7*.json`.

> Da die Audit-Band-Zielwerte sich ändern (§6), kann es sein, dass 900+-Fixtures (53200 in Anker
> = ein einzelnes Wallet ~53k) jetzt „out_of_range" wären. Bei Migration prüfen, ob
> `target_range`-Erwartungen in den Fixtures angepasst werden müssen (insb. `5er_hq_highlevel`,
> das `level_band: '900+'` asserted).

### 4.4 `scripts/smoke.sh` + Watchguards
`smoke.sh` selbst prüft economy nicht direkt, aber ruft Tests, die brechen:
- `node tools/test_v7_issue_pack.js` → grep `v7-issue-pack-ok` (siehe 4.1)
- `node tools/test_v7_schema_consistency.js` → lädt Schema + Fixtures (siehe 4.3); evtl.
  `forbiddenRoot`/economy-Checks.
- `node tools/test_v7_export_fieldlist_watchguard.js` → prüft Doku-Pflichtfelder-Liste; falls dort
  `hq_pool` als Pflichtfeld steht (prüfen!), anpassen.
- `python3 tools/lint_runtime.py` → **drei harte hq_pool-Asserts** (Z120, Z152, Z393):
  - Z120: `req(r"economy\.hq_pool", section, ...)` → auf `economy.wallets`/`characters[].wallet`
    umstellen.
  - Z152: `req(r"\"hq_pool\"\s*:", section, "Save-Exportformat nutzt economy.hq_pool")` → auf
    `"wallets"` bzw. `characters[].wallet` umstellen.
  - Z393: `req(r'"hq_pool"\s*:', block, "HQ-Deepsave nutzt economy.hq_pool")` → dito.
  Diese drei sind **harte Smoke-Blocker** und müssen synchron mit der Doku (§ unten) geändert werden.
- `python3 -m unittest -q` → prüfen, ob Python-Unittests economy berühren.

**VBR-Pflichtlauf nach Umbau:** `bash scripts/smoke.sh` komplett grün + `merge_assert.py --selftest`.

### 4.5 Doku, die mit-linted wird (sonst Smoke rot)
- `core/sl-referenz.md` (Z276, 287, 330, 441, 1006, 1264, 1272, 1280, 1431): hq_pool-Erzählung →
  Wallet-SSOT + Gruppenkasse-View. Z287 (`lint_runtime` Pflicht-Regex) und der Save-v7-Block
  müssen die neuen Pflichtbegriffe enthalten.
- `systems/gameflow/speicher-fortsetzung.md` (Z17, 226, 350, 376, 437, 458, 467, 503, 523, 531,
  585, 703, 821, 832, 843, 856, 859, 872, 873): Economy-Sync-Beschreibung, Exportformat-Block
  (`"hq_pool":` → `"wallets":`/`characters[].wallet`), `economy_audit`-Felder (`hq_pool`→`treasury`),
  Solo→Koop/Koop→Solo-Regeln (hq_pool ankergeführt → entfällt, Wallets wandern mit Charakteren).
- `systems/currency/cu-waehrungssystem.md` (Z52, 57, 62 + „HQ-Pool & Wallet-SSOT"-Abschnitt +
  „Rewards → Wallet-Richtwerte"): Kernabschnitt neu schreiben (kein HQ-Pool-Konto mehr;
  Gruppenkasse = Σ; Kauf aus Wallet; transfer_cu; neue Bänder §6).
- `meta/masterprompt_v6.md` (Z1048): `"economy": { "hq_pool": 0 }` → `"economy": { "wallets": {} }`
  (oder `{}`); Save-Template ist das, was der LLM real reproduziert → **wichtigster Produktiv-Hebel**.
- `gameplay/kampagnenstruktur.md` (Z2038), `core/zeitriss-core.md` (Z708): hq_pool-Erwähnungen.
- v6-Fixtures (`savegame_v6_*`, `qa_save_v6_dummy`): v6 ist **Legacy-Importpfad** → `hq_pool` dort
  bewusst BELASSEN (testet Migration §5). Nicht anfassen, außer ein v6→v7-Migrations-Test erwartet
  die Faltung.

---

## 5. Migration alter Saves beim Laden

**Funktion `migrate_legacy_economy_to_wallets(data)`**, aufgerufen in `load_save` direkt nach
`hydrate_state` / vor `initialize_wallets_from_roster` (Z~9735):

```js
function migrate_legacy_economy_to_wallets(data){
  const economy = state.economy || (state.economy = {});
  // Vorhandenen Topf einsammeln: hq_pool zuerst, dann cu/credits/balance/assets.
  let legacyPool = 0;
  for (const key of ECONOMY_LEGACY_POOL_KEYS){     // ['hq_pool','credits','cu','balance','assets']
    const v = normalize_primary_currency(economy[key]);
    if (v !== null && v > 0){ legacyPool = v; break; } // erster gefundener Topf gewinnt
  }
  // Topf-Felder NICHT mehr als Geldmenge führen.
  delete economy.hq_pool;
  if (legacyPool > 0){
    ensure_wallets();
    const { roster } = build_wallet_roster();
    const anchorId = roster[0] ? roster[0].id : 'agent-1';
    const rec = get_wallet_record(anchorId, roster[0] ? roster[0].label : null);
    rec.balance = Math.max(0, Math.round(rec.balance || 0) + legacyPool); // konservativ: nichts geht verloren
    record_currency_sync('legacy_pool_fold', 0, legacyPool,
      { note: `hq_pool→${anchorId}`, source: 'load_migration' });
  }
  sync_primary_currency(economy); // View = Σ Wallets
}
```

**Anker-Wallet vs. Gleichverteilung — Empfehlung: Anker-Wallet (characters[0]).** Begründung:
- **Deterministisch & konservativ:** Genau ein Ziel, keine Rundungsreste, Σ exakt erhalten.
- **Semantisch ehrlich:** Der HQ-Pool war ein „besitzloser" Topf; beim Zwang zu einem Owner ist
  der Session-Anker (characters[0], der den Save führt) die natürliche Wahl — er „verwaltet" die
  Gruppenkasse historisch.
- **Spielbar reparierbar:** Falls der Spieler das Geld verteilen will, gibt es jetzt `transfer_cu`.
- Gleichverteilung wäre „fairer", aber bei nicht-teilbaren Beträgen entstehen Rundungsreste
  (wieder Leftover-Problem) und sie verändert die *Verteilung* (nicht die Summe) — das ist eine
  stärkere, evtl. unerwünschte Annahme. Anker-Faltung ist die minimalinvasive, rein konservative
  Operation.

> **Einmaligkeit:** Da nach Migration `hq_pool` gelöscht und nie wieder geschrieben wird, ist die
> Faltung idempotent (ein zweiter Load findet keinen Topf mehr). Gesamtvermögen ändert sich nie.

---

## 6. Neue Balancing-Bänder (echter Schritt, kein TODO)

**Problem:** Heute existiert ein **HQ-Pool-Budget** (Lvl120: 8–10k, Lvl512: 25–30k, Lvl900+:
45–60k) **zusätzlich** zu Pro-Wallet-Bändern (1–2k / 3–5k / 6–10k). Schafft man den Pool ab, ohne
den Budgetanteil in die Wallets zu falten, fehlt das Geld → oder es taucht als Inflation an
anderer Stelle auf. Der Pool muss konzeptionell in die Pro-Wallet-Zielwerte **eingerechnet** werden.

**Falt-Logik (für ein 5er-Team als Referenzgröße — Roster-Median):**

| Band | Alt: HQ-Pool | Alt: Wallet Ø | Alt-Gesamt (5er) | Pool/Kopf (5er) | **Neu: Wallet Ø** | **Neu: Gruppenkasse (5er)** |
|---|---|---|---|---|---|---|
| 120 | 8 000–10 000 | 1 000–2 000 | 13 000–20 000 | +1 600–2 000 | **1 200–2 400** ⌀ ~+400 | 6 000–12 000 |
| 512 | 25 000–30 000 | 3 000–5 000 | 40 000–55 000 | +5 000–6 000 | **3 500–6 000** | 17 500–30 000 |
| 900+ | 45 000–60 000 | 6 000–10 000 | 75 000–110 000 | +9 000–12 000 | **7 000–12 000** | 35 000–60 000 |

**Begründung der konkreten Werte:**
- Ich falte den Pro-Kopf-Anteil des alten Pools (Pool/Teamgröße) in das Wallet-Band, runde aber
  **bewusst nach unten** statt 1:1, weil:
  1. Der alte Pool war ein **gemeinsamer** Puffer mit Skaleneffekt (5 Leute teilen sich Sinks);
     pro Kopf voll aufaddiert würde die Pro-Kopf-Kaufkraft steigen = Inflation. Eine moderate
     Stauchung (~30–40% des Pool/Kopf-Anteils landet im Band, Rest verschwindet als entfallener
     „besitzloser Puffer") hält die effektive Kaufkraft stabil.
  2. Die **Gruppenkasse-Bänder (Σ)** liegen jetzt sichtbar UNTER der alten Summe (z.B. 512:
     17,5–30k statt 40–55k), weil der Topf als separater Vermögensspeicher wegfällt. Das ist
     gewollt: weniger totes Kapital, jede CU hat einen Owner. Die Sinks (Chronopolis,
     Implantate, Research) bleiben unverändert (cu-waehrungssystem.md) → der Loop „2–3 Missionen
     heben Wallets, Sinks bauen ab" bleibt intakt, nur ohne Pool-Zwischenspeicher.
- Konkret als Code in `economy_audit_guidelines` (siehe 2.11): 120→`walletMin=1200,walletMax=2400`;
  512→`3500/6000`; 900+→`7000/12000`. `treasury`-Band = walletMin/max × walletCount.

> **Offene Designfrage D7 (Balancing, Flo):** Der „Stauchungsfaktor" ist eine echte Tuning-
> Entscheidung. Ich schlage die obigen Werte als konservative Mitte vor. Alternativen: (a) Pool/Kopf
> voll aufaddieren (großzügiger, leichte Inflation), (b) nur halben Pool/Kopf (härter, drückt
> Endgame-Kaufkraft). Empfehlung (a) für „großzügig fühlt sich gut an", (b) wenn Anti-Inflation
> Priorität hat. Meine Default-Tabelle liegt zwischen den Extremen. **Flo/Orchestrator sollte den
> Faktor bestätigen, da er das Spielgefühl direkt steuert.**

---

## 7. Restrisiken & offene Designfragen (gesammelt)

**Offene Entscheidungen für Orchestrator/Flo:**
- **D1** — `economy.cu`/`credits` im Save: ganz raus (sauber, breit brechend) vs. View-Spiegel
  behalten (empfohlen).
- **D2** — Markt-Kauf-Fehlschlag: `throw` + Toast im Caller (empfohlen) vs. Rückgabewert.
- **D3/D5** — Wie tief verdrahtet die **Referenz-Runtime** `characters[].wallet`? (Live-State nutzt
  `character`+`party`, nicht `characters[]`.) Minimal (nur Load-Seed + Save-Projektion, empfohlen)
  vs. voll.
- **D4** — Arena-Gebühr-Skalierung: auf Initiator-Wallet (niedrigere Gebühr) vs. auf
  `group_treasury_view()` (empfohlen) bei Bezahlung aus Initiator-Wallet.
- **D6** — `economy`-Schema: `required:["wallets"]` vs. **kein required** (empfohlen — Geld lebt in
  `characters[].wallet`, economy.wallets nur Cache).
- **D7** — Balancing-Stauchungsfaktor (§6).

**Restrisiken:**
1. **Zwei Save-Schreiber.** Produktiv schreibt der **LLM** (Masterprompt-Template), nicht
   runtime.js. Wenn das Template nicht sauber auf Wallet-only umgestellt wird, produzieren reale
   Spieler weiter `hq_pool`-Saves → Schema-Fail beim Re-Load. Masterprompt-Diff (Z1048) ist der
   **wichtigste** Produktiv-Hebel, nicht der Code.
2. **`additionalProperties:false` im Export-Schema** ist scharf: jedes real ausgegebene
   economy-Feld muss exakt gedeckt sein. `prepare_save_economy` (`{cu,credits,wallets}`) und Schema
   müssen synchron bleiben. **Verifizieren via merge_assert --selftest.**
3. **Audit-Trace-Drift in Fixtures.** Die `economy_audit`-Traces (`hq_pool`-Feld) in 10 Fixtures
   müssen mit dem neuen Audit-Output (`treasury`) konsistent sein, sonst Watchguard/Issue-Pack rot.
4. **Hoisting-Abhängigkeit** `resolve_primary_currency`→`sum_wallet_balances` (Vorwärtsbezug). Sind
   beide `function`-Deklarationen → OK, aber bei Refactor auf `const fn=` würde es brechen.
5. **HUD-/Grep-Strings**: „HQ-Pool: … verfügbar" → „Gruppenkasse: …". Diverse Test-Greps (debrief,
   sl-referenz lint) hängen an den exakten Strings. Vor Merge `grep -rn "HQ-Pool"` durchgehen.
6. **Konservativität als Dauer-Canary:** `assert_wealth_conservation` (merge_assert) wird zur
   zentralen Invariante. Empfehlung: einen analogen JS-Canary in smoke aufnehmen, der nach
   Split→Merge `Σ characters[].wallet` vor/nach vergleicht. Das ist die strukturelle Garantie,
   dass der von Flo genannte Exploit „architektonisch nicht mehr existiert".

---

## Anhang: Betroffene Dateien + Zeilen (Checkliste für den Orchestrator)

**runtime.js**
- Z2622 `ECONOMY_PRIMARY_KEYS` → `ECONOMY_LEGACY_POOL_KEYS` (+ `hq_pool` voranstellen, nur Migration)
- Z2631 `resolve_primary_currency` → View aus `sum_wallet_balances`
- Z2674 `sync_primary_currency` → override ignorieren, View-Spiegel
- Z2698 `ensure_economy` → wallets-first + `delete economy.hq_pool`
- Z1711 `log_market_purchase` → Käufer-Wallet-Abzug + throw bei Unterdeckung (neuer `options.buyer_id`)
- Z5858 `apply_wallet_split` → direkt in Wallets, Leftover→Anker, kein Topf, neuer HUD-Text
- Z5909 `initialize_wallets_from_roster` → Seed aus `characters[].wallet` (neue Helferfn)
- Z5929 `sum_wallet_balances` → unverändert; NEU `group_treasury_view`
- NEU `transfer_cu(fromId,toId,amount)` + Export Z~10481
- Z5954 `economy_audit_guidelines` → neue Bänder (§6), kein hq-Band
- Z6018 `build_economy_audit` → `treasury` statt `hq_pool`
- Z6063 `maybe_toast_economy_audit` → „Gruppenkasse" statt „HQ-Pool"
- Z6237/6665 `readArenaCurrency`/`writeArenaCurrency` + Z6773 `arenaStart` → Gebühr aus Initiator-Wallet
- Z8168 `prepare_save_economy` → `delete hq_pool`, View-Spiegel
- Z9141/9735 `hydrate_state`/`load_save` → `migrate_legacy_economy_to_wallets` + Owner-Seed
- Z8861 `select_state_for_save` → optionale Wallet→characters[].wallet-Projektion
- Z9588 Merge-Block (`HQ-Pool (economy.cu): Session-Anker-Vorrang`) → Wallet-union-Sprache

**Schemas**
- `saveGame.v7.schema.json` Z146–158 → economy: required raus, wallets-Property (bevorzugt: kein required)
- `saveGame.v7.export.schema.json` Z296–306 → analog, `additionalProperties:false`-konform

**Tests/Harness**
- `tools/test_v7_issue_pack.js:18` → characters[].wallet statt hq_pool
- `tools/test_v7_schema_consistency.js` → prüfen (lädt Fixtures/Schema)
- `tools/test_v7_export_fieldlist_watchguard.js` → prüfen ob hq_pool-Pflichtfeld
- `tools/lint_runtime.py` Z120/Z152/Z393 → hq_pool-Regex → wallets/characters[].wallet
- `playtests/.../merge_assert.py` → `total_wealth`, `assert_merge` (Block 2/4b), `--selftest`-Fixtures
- `internal/qa/fixtures/savegame_v7_*.json` (10 Stück) → hq_pool→Anker-Wallet falten + audit-Traces

**Doku (lint-gated)**
- `core/sl-referenz.md`, `systems/gameflow/speicher-fortsetzung.md`,
  `systems/currency/cu-waehrungssystem.md`, `meta/masterprompt_v6.md` (Z1048!),
  `gameplay/kampagnenstruktur.md`, `core/zeitriss-core.md`

**Verifikation (VBR, Pflicht nach Umbau):**
```
bash scripts/smoke.sh
python3 playtests/zeitriss/harness/merge_assert.py --selftest
```
