const assert = require('assert');
const rt = require('../runtime');

rt.state.location = 'HQ';
rt.state.phase = 'core';
rt.state.character = {
  id: 'CHR-HOST',
  cooldowns: {},
  attributes: { SYS_max: 1, SYS_installed: 1, SYS_runtime: 1, SYS_used: 1 },
  stress: 0,
  psi_heat: 0,
  lvl: 512
};
rt.state.campaign = { episode: 2, mission: 1, px: 0 };
rt.state.party = { characters: [] };
rt.state.team = { members: [] };
rt.state.logs = { flags: {}, hud: [], trace: [] };
rt.state.economy = {
  cu: 3200,
  credits: 3200,
  wallets: {
    host: { balance: 800, name: 'Host' }
  }
};

const incomingSave = {
  save_version: 6,
  zr_version: rt.ZR_VERSION,
  location: 'FIELD',
  phase: 'core',
  character: {
    id: 'CHR-IMPORT',
    cooldowns: {},
    attributes: { SYS_max: 1, SYS_installed: 1, SYS_runtime: 1, SYS_used: 1 },
    stress: 0,
    psi_heat: 0,
    lvl: 120
  },
  campaign: { episode: 1, mission: 2, px: 0, mode: 'preserve' },
  economy: {
    cu: 1500,
    credits: 1500,
    wallets: {
      host: { balance: 50, name: 'Diverging' },
      guest: { balance: 200, name: 'Guest' }
    }
  },
  logs: { hud: [], trace: [], flags: { merge_conflicts: [] } },
  loadout: {},
  ui: { gm_style: 'verbose', intro_seen: true, suggest_mode: false, action_mode: 'uncut' },
  arc_dashboard: { offene_seeds: [], fraktionen: {}, fragen: [] },
  party: { characters: [] },
  team: { members: [] }
};

rt.load_deep(JSON.stringify(incomingSave));

assert.strictEqual(rt.state.economy.cu, 3200, 'Host-HQ-Pool muss Vorrang haben.');
const wallets = rt.state.economy.wallets;
assert.strictEqual(wallets.host.balance, 800, 'Host-Wallet darf nicht überschrieben werden.');
assert.strictEqual(wallets.host.name, 'Host');
assert.strictEqual(wallets.guest.balance, 200, 'Import-Wallet muss übernommen werden.');

const conflicts = rt.state.logs.flags.merge_conflicts || [];
const walletConflicts = conflicts.filter((entry) => entry.field === 'wallet');
const hasWalletConflict = walletConflicts.some((entry) => entry.note && entry.note.includes('Wallet union'));
const hasHqConflict = walletConflicts.some((entry) => entry.note && entry.note.includes('HQ-Pool'));
assert.ok(walletConflicts.length >= 2, 'Wallet-Konflikte fehlen.');
assert.ok(hasWalletConflict, 'Wallet-Konflikt (Union) fehlt.');
assert.ok(hasHqConflict, 'HQ-Pool-Konflikt fehlt.');

console.log('economy-merge-ok');
