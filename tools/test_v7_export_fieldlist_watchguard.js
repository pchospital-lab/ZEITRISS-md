const path = require('path');
const { createDocTextLoader } = require('./watchguard_doc_loader');

const root = path.resolve(__dirname, '..');
const { readMarkdown } = createDocTextLoader({
  root,
  scopeLabel: 'V7-Export-Fieldlist-Watchguard',
});

function assert(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

const doc = readMarkdown(
  'systems/gameflow/speicher-fortsetzung.md',
  [/### Kompakt-Profil \(Save v7\)/i],
  'v7-Export-Kompakt-Profil',
);

const requiredSnippets = [
  'entry_choice_skipped', 'episode_start', 'episode_end',
  'logs.hud', 'logs.psi', 'logs.arena_psi',
  'ui.intro_seen', 'ui.dice.debug_rolls',
  'has_psi', 'psi_heat', 'pp', 'psi_abilities', 'artifact?',
  'arena.active', 'arena.phase', 'arena.queue_state',
  'arena.contract_id', 'arena.streak',
  'arena.pending_rewards', 'arena.banked_rewards',
  'arena.first_wins', 'arena.match_policy'
];

for (const snippet of requiredSnippets) {
  assert(doc.text.includes(snippet), `v7-watchguard: Pflichtfeld fehlt: ${snippet}`);
}

assert(!doc.text.includes('`arena?`'), 'v7-watchguard: Verbotenes optionales arena?-Feld gefunden.');
assert(!/Arena nur wenn genutzt/.test(doc.text), 'v7-watchguard: Restdrift "Arena nur wenn genutzt" gefunden.');

console.log('v7-export-fieldlist-watchguard-ok');
