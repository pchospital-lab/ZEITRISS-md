// Regressionstest fuer den load_deep-Oekonomie-Merge unter Wallet-SSOT.
//
// Historie: Bis zur hq_pool-Abschaffung (2026-06-16, Wallet-SSOT, #3230) testete
// diese Datei den "Session-Anker-HQ-Pool muss Vorrang haben"-Pfad mit cu als
// gespeichertem Topf (cu===3200). Das war stale: Unter Wallet-SSOT ist cu ein
// abgeleiteter VIEW (= Σ Wallets), kein gespeicherter Geldtopf. Die alte
// Assertion (cu===3200 bei Σ Wallets===800) konnte runtime gar nicht mehr
// gelten und liess `npm test` rot laufen (Smoke fing es nicht, weil dieser
// Test nur an `npm test` haengt, nicht am Smoke-Stack).
//
// Neu deckt der Test den load_deep-Host-Anker-Merge ueber ein echtes Roster ab
// (Komplement zu test_wallet_economy.js, der migrate_save/transfer/split prueft).
// Wallet-IDs MUESSEN Roster-Character-IDs sein - ensure_wallets/Roster-Reconcile
// pruned sonst nicht zugeordnete Wallets (war die Fragilitaet des Alt-Fixtures
// mit kuenstlichen Keys host/guest).
//   1. cu/credits sind nach dem Laden = Σ Wallets (View, kein Topf).
//   2. Session-Anker-Wallets behalten Vorrang (kein Inflations-Aufaddieren des Imports).
//   3. Ein Wallet-union-Konflikt wird protokolliert, wenn Anker != Import.
//   4. Kein hq_pool-Topf ueberlebt das Laden.
const assert = require('assert');
const rt = require('../runtime');

rt.state.location = 'HQ';
rt.state.phase = 'core';
rt.state.character = {
  id: 'AGENT-1',
  cooldowns: {},
  attributes: { SYS_max: 1, SYS_installed: 1, SYS_runtime: 1, SYS_used: 1 },
  stress: 0,
  psi_heat: 0,
  lvl: 6
};
rt.state.campaign = { episode: 2, mission: 1, px: 0 };
rt.state.party = {
  characters: [
    { id: 'AGENT-1', name: 'Nova' },
    { id: 'AGENT-2', name: 'Ghost' }
  ]
};
rt.state.team = { members: [] };
rt.state.logs = { flags: {}, hud: [], trace: [] };
// Host-Anker: Geld liegt in den Wallets der Roster-IDs. cu wird als View abgeleitet.
rt.state.economy = {
  wallets: {
    'AGENT-1': { balance: 800, name: 'Nova' },
    'AGENT-2': { balance: 1200, name: 'Ghost' }
  }
};

const incomingSave = {
  save_version: 6,
  zr_version: rt.ZR_VERSION,
  location: 'FIELD',
  phase: 'core',
  character: {
    id: 'AGENT-1',
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_installed: 1, SYS_runtime: 1, SYS_used: 1 },
    stress: 0,
    psi_heat: 0,
    lvl: 6
  },
  campaign: { episode: 1, mission: 2, px: 0, mode: 'preserve' },
  // WICHTIG: Geld-SSOT ist characters[].wallet. load_deep -> migrate_save ->
  // fold_legacy_pool_into_characters projiziert economy.wallets UNBEDINGT aus
  // characters[].wallet. Der divergente Import-Betrag MUSS daher in die SSOT,
  // sonst wird er auf 0 projiziert und der Merge testet 800-vs-0 statt 800-vs-50.
  party: {
    characters: [
      { id: 'AGENT-1', name: 'Nova', wallet: 50 },
      { id: 'AGENT-2', name: 'Ghost', wallet: 1200 }
    ]
  },
  economy: {
    wallets: {
      'AGENT-1': { balance: 50, name: 'Nova' },
      'AGENT-2': { balance: 1200, name: 'Ghost' }
    }
  },
  logs: { hud: [], trace: [], flags: { merge_conflicts: [] } },
  loadout: {},
  ui: { gm_style: 'verbose', intro_seen: true, suggest_mode: false, action_mode: 'uncut' },
  arc_dashboard: { offene_seeds: [], fraktionen: {}, fragen: [] },
  team: { members: [] }
};

rt.load_deep(JSON.stringify(incomingSave));

const wallets = rt.state.economy.wallets;

// 2) Session-Anker-Wallets behalten Vorrang, kein Inflations-Aufaddieren des Imports.
assert.strictEqual(wallets['AGENT-1'].balance, 800, 'Session-Anker-Wallet (AGENT-1) darf nicht ueberschrieben/aufaddiert werden.');
assert.strictEqual(wallets['AGENT-2'].balance, 1200, 'AGENT-2-Wallet bleibt erhalten.');

// 1) cu/credits sind reiner View (= Σ Wallets): 800 + 1200 = 2000.
const sumWallets = Object.values(wallets)
  .reduce((s, r) => s + (Number.isFinite(r.balance) ? r.balance : 0), 0);
assert.strictEqual(sumWallets, 2000, 'Σ Wallets == 2000 (Anker-Werte gewinnen).');
assert.strictEqual(rt.state.economy.cu, sumWallets, 'cu muss = Σ Wallets sein (View, kein Topf).');
assert.strictEqual(rt.state.economy.credits, rt.state.economy.cu, 'credits spiegelt cu.');

// 4) Kein hq_pool-Topf darf nach dem Laden existieren.
assert.ok(!('hq_pool' in rt.state.economy), 'Kein hq_pool-Topf darf nach dem Laden existieren.');

// 3) Wallet-union-Konflikt protokolliert (Anker AGENT-1=800 != Import=50).
const conflicts = rt.state.logs.flags.merge_conflicts || [];
const walletConflicts = conflicts.filter((entry) => entry.field === 'wallet');
assert.ok(walletConflicts.length >= 1, 'Wallet-Konflikt fehlt (Anker != Import muss protokolliert werden).');
const unionConflict = walletConflicts.find(
  (entry) => entry.note && entry.note.includes('Wallet union') && entry.note.includes('AGENT-1')
);
assert.ok(unionConflict, 'Wallet-union-Konflikt fuer AGENT-1 (Session-Anker bevorzugt) fehlt.');
// Divergenz festnageln: der Import-Wert (50) muss wirklich in den Konflikt einfliessen,
// damit der Test echte 800-vs-50-Divergenz prueft (nicht 800-vs-0).
assert.ok(
  JSON.stringify(unionConflict.source).includes('50'),
  'Konflikt-source muss den divergierenden Import-Betrag (50) tragen.'
);

console.log('economy-merge-ok');
