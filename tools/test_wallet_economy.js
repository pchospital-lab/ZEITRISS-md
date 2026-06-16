// Regressionstest fuer die Wallet-SSOT-Oekonomie (hq_pool-Abschaffung 2026-06-16).
//
// Deckt genau die Luecken ab, die smoke vorher nicht fing, weil kein Test den
// echten migrate_save/load-Pfad mit Geld durchspielte:
//   1. Legacy-hq_pool-Load: Gesamtvermoegen bleibt erhalten (Pool -> Anker-Wallet).
//   2. Kein Inflations-Re-Fold des cu/credits-View-Spiegels bei Roster-Wachstum.
//   3. characters[].wallet wird beim Export real geschrieben (deklarierte SSOT).
//   4. transfer_cu schreibt ein cu_transfer-Trace und ist streng konservativ.
//   5. apply_wallet_split haelt Σ-Wallets (kein Topf, Rest -> Anker).
const assert = require('assert');
const rt = require('../runtime.js');

function sumWallets(economy){
  return Object.values((economy && economy.wallets) || {})
    .reduce((s, r) => s + (Number.isFinite(r.balance) ? r.balance : 0), 0);
}

// 1) Legacy-hq_pool-Load erhaelt das Gesamtvermoegen konservativ.
{
  const legacy = {
    v: 7, zr_version: '4.2.6', save_version: 6,
    campaign: { episode: 7, mission: 5, mode: 'core' },
    characters: [
      { id: 'AGENT-1', name: 'Nova', wallet: 2800, attr: {}, lvl: 5 },
      { id: 'AGENT-2', name: 'Ghost', wallet: 2600, attr: {}, lvl: 5 }
    ],
    economy: { hq_pool: 18300 },
    logs: { flags: {} }, arc: {}, ui: { gm_style: 'verbose' }, arena: {}
  };
  const before = 2800 + 2600 + 18300;
  const m = rt.migrate_save(JSON.parse(JSON.stringify(legacy)));
  assert.strictEqual(sumWallets(m.economy), before,
    'Legacy-Load: Σ Wallets muss alt(Pool+Wallets) entsprechen (kein Geldverlust).');
  assert.strictEqual(m.economy.cu, before, 'Legacy-Load: cu-View muss = Σ Wallets sein.');
  assert.ok(!('hq_pool' in m.economy), 'Legacy-Load: hq_pool darf nicht ueberleben.');
  assert.strictEqual(m.party.characters[0].wallet, 2800 + 18300,
    'Legacy-Load: Pool muss ins Anker-Wallet (Index 0) gefaltet werden.');
  assert.strictEqual(m.party.characters[1].wallet, 2600,
    'Legacy-Load: Nicht-Anker-Wallets bleiben unveraendert.');
}

// 2) Kein Inflations-Re-Fold: cu/credits sind View-Spiegel, kein Topf.
{
  const save = {
    v: 7, zr_version: '4.2.6', save_version: 6,
    campaign: { episode: 1, mission: 0, mode: 'core' },
    characters: [
      { id: 'A', name: 'A', wallet: 100, attr: {}, lvl: 3 },
      { id: 'B', name: 'B', wallet: 0, attr: {}, lvl: 3 }
    ],
    economy: { wallets: { A: { balance: 100, name: 'A' } }, cu: 100, credits: 100 },
    logs: { flags: {} }, arc: {}, ui: { gm_style: 'verbose' }, arena: {}
  };
  const m = rt.migrate_save(JSON.parse(JSON.stringify(save)));
  assert.strictEqual(sumWallets(m.economy), 100,
    'Kein Re-Fold: cu/credits-View darf nicht erneut als Topf gefaltet werden.');
  assert.strictEqual(m.economy.wallets.A.balance, 100,
    'Kein Re-Fold: Anker-Wallet bleibt bei 100, keine Inflation.');
}

// 3) characters[].wallet wird beim Export real geschrieben (SSOT existiert).
{
  const m = rt.migrate_save({
    v: 7, zr_version: '4.2.6', save_version: 6,
    campaign: { episode: 1, mission: 0, mode: 'core' },
    characters: [
      { id: 'A', name: 'A', wallet: 300, attr: {}, lvl: 3 },
      { id: 'B', name: 'B', wallet: 200, attr: {}, lvl: 3 }
    ],
    economy: { wallets: { A: { balance: 300, name: 'A' }, B: { balance: 200, name: 'B' } } },
    logs: { flags: {} }, arc: {}, ui: { gm_style: 'verbose' }, arena: {}
  });
  // economy.wallets und party.characters[].wallet muessen deckungsgleich sein.
  assert.strictEqual(m.party.characters[0].wallet, 300, 'Export: characters[0].wallet == economy.wallets.A.');
  assert.strictEqual(m.party.characters[1].wallet, 200, 'Export: characters[1].wallet == economy.wallets.B.');
}

// 4) transfer_cu: cu_transfer-Trace + strenge Konservierung.
{
  rt.state.character = { id: 'NOVA', name: 'Nova', wallet: 1000, attr: {} };
  rt.state.party = { characters: [{ id: 'NOVA', name: 'Nova' }, { id: 'GHOST', name: 'Ghost' }] };
  rt.state.team = {};
  rt.state.economy = { wallets: { NOVA: { balance: 1000, name: 'Nova' }, GHOST: { balance: 500, name: 'Ghost' } } };
  rt.state.logs = { trace: [], flags: {} };
  const before = rt.group_treasury_view(rt.state.economy);
  const res = rt.transfer_cu('NOVA', 'GHOST', 400);
  assert.strictEqual(rt.state.economy.wallets.NOVA.balance, 600, 'Transfer: Geber -400.');
  assert.strictEqual(rt.state.economy.wallets.GHOST.balance, 900, 'Transfer: Empfaenger +400.');
  assert.strictEqual(rt.group_treasury_view(rt.state.economy), before, 'Transfer: Σ Wallets konserviert.');
  const traces = (rt.state.logs.trace || []).map((t) => t.event);
  assert.ok(traces.includes('cu_transfer'), 'Transfer: cu_transfer-Trace muss geschrieben werden.');
  assert.deepStrictEqual({ from: res.from, to: res.to, amount: res.amount },
    { from: 'NOVA', to: 'GHOST', amount: 400 }, 'Transfer: Rueckgabe stimmt.');
  // Unterdeckung wirft, ohne Teilbuchung.
  assert.throws(() => rt.transfer_cu('GHOST', 'NOVA', 99999), /nur|nicht/i,
    'Transfer: Unterdeckung muss werfen.');
  assert.strictEqual(rt.state.economy.wallets.GHOST.balance, 900, 'Transfer: keine Teilbuchung bei Fehlschlag.');
  // Selbsttransfer + negativ werfen.
  assert.throws(() => rt.transfer_cu('NOVA', 'NOVA', 10), /identisch/i, 'Transfer: Selbsttransfer wirft.');
  assert.throws(() => rt.transfer_cu('NOVA', 'GHOST', -5), /positiv/i, 'Transfer: negativer Betrag wirft.');
}

// 5) apply_wallet_split: Σ-Wallets konserviert, kein Topf, Rest -> Anker.
{
  rt.state.character = { id: 'NOVA', name: 'Nova', wallet: 0, attr: {} };
  rt.state.party = { characters: [{ id: 'NOVA', name: 'Nova' }, { id: 'GHOST', name: 'Ghost' }] };
  rt.state.team = {};
  rt.state.economy = { wallets: { NOVA: { balance: 0, name: 'Nova' }, GHOST: { balance: 0, name: 'Ghost' } } };
  rt.state.logs = { trace: [], hud: [], flags: {} };
  // 101 CU auf 2 Wallets -> 50/50 + 1 Rest an Anker.
  rt.apply_wallet_split({}, 101);
  const total = rt.group_treasury_view(rt.state.economy);
  assert.strictEqual(total, 101, 'Split: Σ Wallets == ausgeschuetteter Reward (kein Geld verloren/erzeugt).');
  assert.ok(!('hq_pool' in rt.state.economy), 'Split: kein hq_pool-Topf entsteht.');
}

console.log('wallet-economy-ok');
